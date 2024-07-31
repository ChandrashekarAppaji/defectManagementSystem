import datetime

from bson import ObjectId
from flask import Flask, render_template, request, session, redirect, flash, url_for
import pymongo
import os
from config import Config

# APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# Raise_ticket_images_files_path = APP_ROOT + "/static/raise_ticket_images"
app = Flask(__name__)
app.secret_key = "defect_management"
app.config.from_object(Config)

Raise_ticket_images_files_path = app.config['UPLOAD_FOLDER']
my_client = pymongo.MongoClient(app.config['MONGO_URI'])
my_database = my_client["Defect_Management_System"]
admin_collection = my_database["admin"]
developer_collection = my_database["developer"]
user_collection = my_database["user"]
manager_collection = my_database["manager"]
tickets_collection = my_database["tickets"]
ticket_updates_collection = my_database["status"]
notifications_collection = my_database["notifications"]
projects_collection = my_database["projects"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/project_manager_login")
def project_manager_login():
    return render_template("project_manager_login.html")


@app.route("/developer_login")
def developer_login():
    return render_template("developer_login.html")


@app.route("/user_login")
def user_login():
    return render_template("user_login.html")


@app.route("/add_project")
def add_project():
    return render_template("add_project.html")


@app.route("/user_registration")
def user_registration():
    return render_template("user_registration.html")


@app.route("/user_registration_action", methods=['post'])
def user_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    zip_code = request.form.get("zip_code")
    query = {"email": email}
    count = user_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Email address already Registered")
    query = {"phone": phone}
    count = user_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Phone Number already Registered")
    user = {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone, "password": password,
            "state": state, "city": city, "address": address, "zip_code": zip_code}
    user_collection.insert_one(user)
    return render_template("msg.html", message="Your Registration Successfully")


'''
query = {}
count = admin_collection.count_documents(query)
if count == 0:
    query = {"username": "admin", "password": "admin"}
    admin_collection.insert_one(query)
'''


@app.route("/add_project_action", methods=['post'])
def add_project_action():
    project_name = request.form.get("project_name")
    description = request.form.get("description")

    project_data = {
        "project_name": project_name,
        "description": description,
        "managers": [],
        "developers": []
    }

    projects_collection.insert_one(project_data)
    return render_template("admin_message.html", message="Project created successfully")


@app.route("/assign_to_project")
def assign_to_project():
    query = {}
    developers = developer_collection.find(query)
    managers = manager_collection.find(query)
    projects = projects_collection.find(query)
    developers = list(developers)
    managers = list(managers)
    projects = list(projects)

    # Create dictionaries for quick lookup
    manager_dict = {str(manager['_id']): manager for manager in managers}
    developer_dict = {str(developer['_id']): developer for developer in developers}

    # Prepare the data for rendering
    project_data = []
    for project in projects:
        project_id = str(project['_id'])
        project_name = project.get("project_name", "Unknown")

        # Get managers and developers for the current project
        current_managers = [manager_dict.get(str(manager_id)) for manager_id in project.get("managers", [])]
        current_developers = [developer_dict.get(str(developer_id)) for developer_id in project.get("developers", [])]

        project_data.append({
            "project_name": project_name,
            "managers": current_managers,
            "developers": current_developers
        })

    return render_template("assign_to_project.html",projects=projects,managers=managers,developers=developers,project_data=project_data)


@app.route("/assign_to_project_action", methods=['POST'])
def assign_to_project_action():
    project_id = request.form.get("project_id")
    manager_id = request.form.get("manager_id")
    developer_id = request.form.get("developer_id")

    # Fetch the current project details
    project = projects_collection.find_one({"_id": ObjectId(project_id)})

    # Initialize the message
    message = "Assigned to project successfully"

    if manager_id:
        # Check if the manager is already assigned to the project
        if ObjectId(manager_id) in project.get("managers", []):
            message = "Manager is already assigned to the project"
        else:
            projects_collection.update_one(
                {"_id": ObjectId(project_id)},
                {"$addToSet": {"managers": ObjectId(manager_id)}}
            )

    if developer_id:
        # Check if the developer is already assigned to the project
        if ObjectId(developer_id) in project.get("developers", []):
            message = "Developer is already assigned to the project"
        else:
            projects_collection.update_one(
                {"_id": ObjectId(project_id)},
                {"$addToSet": {"developers": ObjectId(developer_id)}}
            )

    # Fetch all projects, managers, and developers
    projects = list(projects_collection.find())
    managers = list(manager_collection.find())
    developers = list(developer_collection.find())

    # Print debug information
    print(f"Projects: {projects}")
    print(f"Managers: {managers}")
    print(f"Developers: {developers}")


    # Create dictionaries for quick lookup
    manager_dict = {str(manager['_id']): manager for manager in managers}
    developer_dict = {str(developer['_id']): developer for developer in developers}

    # Prepare the data for rendering
    project_data = []
    for project in projects:
        project_id = str(project['_id'])
        project_name = project.get("project_name", "Unknown")

        # Get managers and developers for the current project
        current_managers = [manager_dict.get(str(manager_id)) for manager_id in project.get("managers", [])]
        current_developers = [developer_dict.get(str(developer_id)) for developer_id in project.get("developers", [])]

        project_data.append({
            "project_name": project_name,
            "managers": current_managers,
            "developers": current_developers
        })

    return render_template(
        "assign_to_project.html",
        projects=projects,
        managers=managers,
        developers=developers,
        message=message,project_data=project_data
    )


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == "admin" and password == "admin":
        session['role'] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("msg.html", message="Invalid Username and Password")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/add_manager")
def add_manager():
    query = {}
    managers = manager_collection.find(query)
    managers = list(managers)
    # return render_template("view_managers.html", managers=managers)
    return render_template("add_manager.html", managers=managers)


@app.route("/add_manager_action", methods=['post'])
def manager_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    experience = request.form.get("experience")
    address = request.form.get("address")
    dob = request.form.get("dob")

    # Check for duplicate email
    query = {"email": email}
    count = manager_collection.count_documents(query)
    if count > 0:
        return render_template("admin_message.html", message="This email already exists!")

    # Check for duplicate phone number
    query = {"phone": phone}
    count = manager_collection.count_documents(query)
    if count > 0:
        return render_template("admin_message.html", message="This phone number already exists!")

    # Insert new manager
    query = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "password": password,
        "experience": experience,
        "address": address,
        "dob": dob
    }
    manager_collection.insert_one(query)
    return render_template("admin_message.html", message="Manager added successfully")


@app.route("/view_managers")
def view_managers():
    query = {}
    managers = manager_collection.find(query)
    managers = list(managers)
    return render_template("view_managers.html", managers=managers)


@app.route("/add_developer")
def add_developer():
    query = {}
    developers = developer_collection.find(query)
    developers = list(developers)
    # return render_template("view_developers.html", developers=developers)
    return render_template("add_developer.html", developers=developers)


@app.route("/add_developer_action", methods=['post'])
def add_developer_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    experience = request.form.get("experience")
    skills = request.form.get("skills")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    zip_code = request.form.get("zip_code")
    query = {"email": email}
    count = developer_collection.count_documents(query)
    if count > 0:
        return render_template("admin_message.html", message="This email already Exist!")
    query = {"phone": phone}
    count = developer_collection.count_documents(query)
    if count > 0:
        return render_template("admin_message.html", message="This phone number already Exist!")
    query = {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone, "password": password,
             "experience": experience,
             "skills": skills, "address": address, "city": city, "state": state, "zip_code": zip_code}
    developer_collection.insert_one(query)
    return render_template("admin_message.html", message="Developer added successfully")


@app.route("/view_developers")
def view_developers():
    query = {}
    developers = developer_collection.find(query)
    developers = list(developers)
    return render_template("view_developers.html", developers=developers)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/user_login_action", methods=['post'])
def user_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = user_collection.count_documents(query)
    if count > 0:
        user = user_collection.find_one(query)
        session['role'] = 'user'
        session['user_id'] = str(user['_id'])
        session['name'] = str(user['first_name']) + ' [User]'
        return redirect("/user_home")
    else:
        return render_template("msg.html", message="Invalid Email and Password")


@app.route("/user_home")
def user_home():
    if 'user_id' in session:
        name = session['name']
    return render_template("user_home.html", name=name)


@app.route("/raise_ticket", methods=['GET'])
def raise_ticket():
    projects = projects_collection.find()
    return render_template("raise_ticket.html", projects=projects)


@app.route("/raise_ticket_action", methods=['post'])
def raise_ticket_action():
    ticket_title = request.form.get("ticket_title")
    description = request.form.get("description")
    date = datetime.datetime.today()
    picture = request.files.get("picture")
    path = Raise_ticket_images_files_path + "/" + picture.filename
    picture.save(path)
    user_id = session['user_id']
    project_id = request.form.get("project_id")

    # Create ticket entry
    ticket_data = {
        "ticket_title": ticket_title,
        "description": description,
        "picture": picture.filename,
        "date": date,
        "user_id": ObjectId(user_id),
        "status": 'Open',
        "project_id": ObjectId(project_id)
    }
    result = tickets_collection.insert_one(ticket_data)
    ticket_id = result.inserted_id

    # Create notification entry
    notification_data = {
        "notification_title": "New Ticket Raised",
        "notification_description": description,
        "date": date,
        "user_id": ObjectId(user_id),
        "ticket_id": ObjectId(ticket_id)
    }
    notifications_collection.insert_one(notification_data)

    # Flash message or render template
    return render_template("user_message.html", message="Ticket added successfully")


@app.route("/view_tickets")
def view_tickets():
    user_role = session['role']

    if user_role == 'manager':
        # Fetch projects managed by the manager
        manager_id = session['manager_id']
        projects = projects_collection.find({"managers": ObjectId(manager_id)})
        project_ids = [project['_id'] for project in projects]
        tickets = tickets_collection.find({
            "project_id": {"$in": project_ids},
            "$or": [
                {"manager_id": {"$exists": False}},  # Manager ID does not exist
                {"manager_id": ObjectId(manager_id)}  # Manager ID matches
            ]
        })


    elif user_role == 'developer':
        # Fetch projects assigned to the developer
        developer_id = session['developer_id']
        projects = projects_collection.find({"developers": ObjectId(developer_id)})
        project_ids = [project['_id'] for project in projects]
        tickets = tickets_collection.find({"project_id": {"$in": project_ids}})
        tickets = tickets_collection.find({
            "project_id": {"$in": project_ids},
            "developer_id": ObjectId(developer_id)
        })
    else:
        # Fetch tickets raised by the
        user_id = session['user_id']
        projects = projects_collection.find({})
        project_ids = [project['_id'] for project in projects]
        tickets = tickets_collection.find({"user_id": ObjectId(user_id)})

    tickets = list(tickets)
    for ticket in tickets:
        print(f"Original ticket: {ticket}")
        if 'project_id' in ticket and isinstance(ticket['project_id'], ObjectId):
            ticket['project_id'] = str(ticket['project_id'])
        print(f"Processed ticket: {ticket}")
    return render_template("view_tickets.html", get_manager_by_manager_id=get_manager_by_manager_id, tickets=tickets,
                           get_ticket_by_manager_id=get_ticket_by_manager_id,
                           get_ticket_by_developer_id=get_ticket_by_developer_id,
                           get_ticket_by_user_id=get_ticket_by_user_id,
                           get_developer_by_developer_id=get_developer_by_developer_id,
                           get_user_by_user_id=get_user_by_user_id,
                           get_project_by_id=get_project_by_id)


@app.route("/change_password_action", methods=['POST'])
def change_password_action():
    email = request.form.get("email")
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")

    if new_password != confirm_new_password:
        return render_template("admin_message.html", message="New passwords do not match!")

    # Find the manager by email
    manager = manager_collection.find_one({"email": email})

    if manager and manager['password'] == current_password:
        manager_collection.update_one({"email": email}, {"$set": {"password": new_password}})
        return render_template("admin_message.html", message="Password changed successfully")
    else:
        return render_template("admin_message.html", message="Current password is incorrect or email not found!")


@app.route("/change_password", methods=['GET'])
def change_password():
    return render_template("change_password.html")


@app.route("/project_manager_login_action", methods=['post'])
def project_manager_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = manager_collection.count_documents(query)
    if count > 0:
        manager = manager_collection.find_one(query)
        session['role'] = 'manager'
        session['manager_id'] = str(manager['_id'])
        session['name'] = str(manager['first_name']) + '[Project_Manager]'
        return redirect("/manager_home")
    else:
        return render_template("msg.html", message="Invalid Email and Password")


@app.route("/manager_home")
def manager_home():
    if 'manager_id' in session:
        name = session['name']
    return render_template("manager_home.html", name=name)


@app.route("/accept_ticket")
def accept_ticket():
    ticket_id = request.args.get("ticket_id")
    manager_id = session['manager_id']
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket Accepted", "manager_id": ObjectId(manager_id)}}
    tickets_collection.update_one(query1, query2)
    notification_title = "Ticket Accepted"
    notification_description = "The " + session['role'] + " updated status as Ticket Accepted"
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description": notification_description,
             "date": date, "ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
    return redirect("/view_tickets")


@app.route("/reject_ticket")
def reject_ticket():
    ticket_id = request.args.get("ticket_id")
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket Rejected"}}
    tickets_collection.update_one(query1, query2)
    notification_title = "Ticket Rejected"
    notification_description = "The " + session['role'] + " updated status as Ticket Rejected"
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description": notification_description,
             "date": date, "ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
    return redirect("/view_tickets")


@app.route("/close_ticket")
def close_ticket():
    ticket_id = request.args.get("ticket_id")
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket Closed"}}
    tickets_collection.update_one(query1, query2)
    notification_title = "Ticket Closed"
    notification_description = "The " + session['role'] + " updated status as Ticket Closed"
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description": notification_description,
             "date": date, "ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
    return redirect("/view_tickets")


@app.route("/developer_login_action", methods=['post'])
def developer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = developer_collection.count_documents(query)
    if count > 0:
        developer = developer_collection.find_one(query)
        session['role'] = 'developer'
        session['developer_id'] = str(developer['_id'])
        session['name'] = str(developer['first_name']) + '[Developer]'
        return redirect("/developer_home")
    else:
        return render_template("msg.html", message="Invalid Email and Password")


@app.route("/developer_home")
def developer_home():
    if 'developer_id' in session:
        name = session['name']
    return render_template("developer_home.html", name=name)


@app.route("/assign_to_developer")
def assign_to_developer():
    ticket_id = request.args.get("ticket_id")

    # Fetch the ticket to get the project_id
    ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        return "Ticket not found", 404

    project_id = ticket.get("project_id")

    if not project_id:
        return "Project ID not found in ticket", 404

    # Fetch the project to get the list of developer IDs
    project = projects_collection.find_one({"_id": project_id})
    if not project:
        return "Project not found", 404

    # Get the list of developer IDs for the project
    developer_ids = project.get("developers", [])

    # Fetch all developers but filter by those who are in the project
    developers = developer_collection.find({"_id": {"$in": developer_ids}})
    developers = list(developers)

    return render_template("assign_to_developer.html", developers=developers, ticket_id=ticket_id)


@app.route("/assign_to_developer_action")
def assign_to_developer_action():
    ticket_id = request.args.get("ticket_id")
    developer_id = request.args.get("developer_id")
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket Assigned to Developer", "developer_id": ObjectId(developer_id)}}
    tickets_collection.update_one(query1, query2)
    notification_title = "Assign To Developer"
    notification_description = "The " + session['role'] + " updated status as Ticket Assign To Developer"
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description": notification_description,
             "date": date, "ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
    return render_template("manager_message.html", message="Developer Assigned Successfully")


@app.route("/ticket_in_progress")
def ticket_in_process():
    ticket_id = request.args.get("ticket_id")
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket In Progress"}}
    tickets_collection.update_one(query1, query2)
    notification_title = "Ticket In Progress"
    notification_description = "The " + session['role'] + " updated status as Ticket In Progress"
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description": notification_description,
             "date": date, "ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
    return redirect("/view_tickets")


def get_ticket_by_manager_id(manger_id):
    query = {"_id": manger_id}
    mangers = manager_collection.find_one(query)
    return mangers


def get_ticket_by_developer_id(developer_id):
    query = {"_id": developer_id}
    developers = developer_collection.find_one(query)
    return developers


def get_ticket_by_user_id(user_id):
    query = {"_id": user_id}
    users = user_collection.find_one(query)
    return users


def get_project_by_id(project_id):
    try:
        if isinstance(project_id, str):
            project_id = ObjectId(project_id)  # Convert string back to ObjectId
        return projects_collection.find_one({"_id": project_id})
    except Exception as e:
        print(f"Error fetching project by ID {project_id}: {e}")
        return None


@app.route("/add_comment_action")
def add_comment_action():
    comment = request.args.get("comment")
    ticket_id = request.args.get("ticket_id")
    date = datetime.datetime.now()
    if session['role'] == 'manager':
        query = {"comment": comment, "manager_id": ObjectId(session['manager_id']), "role": session['role'],
                 "date": date}
    elif session['role'] == 'developer':
        query = {"comment": comment, "developer_id": ObjectId(session['developer_id']), "role": session['role'],
                 "date": date}
    elif session['role'] == 'user':
        query = {"comment": comment, "user_id": ObjectId(session['user_id']), "role": session['role'], "date": date}

    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$push": {"comments": query}}
    tickets_collection.update_one(query1, query2)
    return redirect("/view_tickets")


def get_developer_by_developer_id(developer_id):
    query = {"_id": developer_id}
    developers = developer_collection.find_one(query)
    return developers


def get_manager_by_manager_id(manager_id):
    manager = manager_collection.find_one({"_id": ObjectId(manager_id)})
    return manager


def get_user_by_user_id(user_id):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    return user


@app.route("/add_ticket_update")
def add_ticket_update():
    ticket_id = request.args.get("ticket_id")
    return render_template("add_ticket_update.html", ticket_id=ticket_id)


@app.route("/add_ticket_update_action")
def add_ticket_update_action():
    ticket_id = request.args.get("ticket_id")
    update = request.args.get("update")
    date = datetime.datetime.now()
    query = {"update": update, "date": date, "ticket_id": ObjectId(ticket_id)}
    ticket_updates_collection.insert_one(query)
    notification_title = "Update Added"
    notification_description = update
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description": notification_description,
             "date": date, "ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
    return render_template("developer_message.html", message="Your ticket update added successfully")


@app.route("/view_ticket_updates")
def view_ticket_updates():
    ticket_id = request.args.get("ticket_id")
    ticket_updates = ticket_updates_collection.find({"ticket_id": ObjectId(ticket_id)})
    ticket_updates = list(ticket_updates)
    return render_template("view_ticket_updates.html", ticket_updates=ticket_updates)


@app.route("/manager_notifications")
def manager_notifications():
    manager_id = session['manager_id']
    query = {"manager_id": ObjectId(manager_id)}
    tickets = tickets_collection.find(query)
    ticket_ids = []
    for ticket in tickets:
        ticket_ids.append(ticket['_id'])
    query = {"ticket_id": {"$in": ticket_ids}}
    notifications = notifications_collection.find(query)
    return render_template("manager_notifications.html", notifications=notifications)


@app.route("/user_notifications")
def user_notifications():
    user_id = session['user_id']
    query = {"user_id": ObjectId(user_id)}
    tickets = tickets_collection.find(query)
    ticket_ids = []
    for ticket in tickets:
        ticket_ids.append(ticket['_id'])
    query = {"ticket_id": {"$in": ticket_ids}}
    notifications = notifications_collection.find(query)
    return render_template("user_notifications.html", notifications=notifications)


@app.route("/developer_notifications")
def developer_notifications():
    developer_id = session['developer_id']
    query = {"developer_id": ObjectId(developer_id)}
    tickets = tickets_collection.find(query)
    ticket_ids = []
    for ticket in tickets:
        ticket_ids.append(ticket['_id'])
    query = {"ticket_id": {"$in": ticket_ids}}
    notifications = notifications_collection.find(query)
    return render_template("developer_notifications.html", notifications=notifications)


@app.context_processor
def inject_user():
    return dict(name=session.get('name'))


app.run(debug=True)
