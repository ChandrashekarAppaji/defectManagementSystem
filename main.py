import datetime

from bson import ObjectId
from flask import Flask, render_template, request, session, redirect
import pymongo
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
Raise_ticket_images_files_path = APP_ROOT + "/static/raise_ticket_images"


my_client = pymongo.MongoClient("mongodb://localhost:27017")
my_database = my_client["Defect_Management_System"]
admin_collection = my_database["admin"]
developer_collection = my_database["developer"]
user_collection = my_database["user"]
manager_collection = my_database["manager"]
tickets_collection = my_database["tickets"]
ticket_updates_collection = my_database["ticket_updates"]
notifications_collection = my_database["notifications"]

app = Flask(__name__)
app.secret_key = "defect_management"


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


query = {}
count = admin_collection.count_documents(query)
if count == 0:
    query = {"username": "admin", "password": "admin"}
    admin_collection.insert_one(query)


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
    return render_template("add_manager.html")


@app.route("/add_manager_action", methods=['post'])
def manager_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    experience = request.form.get("experience")
    query = {"email":email}
    count = manager_collection.count_documents(query)
    if count > 0:
        return render_template("admin_message.html", message="This email already Exist!")
    query = {"phone": phone}
    count = manager_collection.count_documents(query)
    if count > 0:
        return render_template("admin_message.html", message="This phone number already Exist!")
    query = {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone, "password": password, "experience": experience}
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
    return render_template("add_developer.html")


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
    query = {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone, "password": password, "experience": experience,
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
    query = {"email": email,"password": password}
    count = user_collection.count_documents(query)
    if count > 0:
        user = user_collection.find_one(query)
        session['role'] = 'user'
        session['user_id'] = str(user['_id'])
        return redirect("/user_home")
    else:
        return render_template("msg.html", message="Invalid Email and Password")


@app.route("/user_home")
def user_home():
    return render_template("user_home.html")


@app.route("/raise_ticket")
def raise_ticket():
    return render_template("raise_ticket.html")


@app.route("/raise_ticket_action", methods=['post'])
def raise_ticket_action():
    ticket_title = request.form.get("ticket_title")
    description = request.form.get("description")
    date = datetime.datetime.today()
    picture = request.files.get("picture")
    path = Raise_ticket_images_files_path + "/" + picture.filename
    picture.save(path)
    user_id = session['user_id']
    query = {"ticket_title": ticket_title, "description": description, "picture": picture.filename, "date": date, "user_id":ObjectId(user_id), "status": 'Ticket Raise'}
    result = tickets_collection.insert_one(query)
    ticket_id = result.inserted_id
    notification_title = "New Ticket Raised"
    notification_description = description
    date = datetime.datetime.today()
    user_id = session['user_id']
    query = {"_id": ObjectId(ticket_id), "notification_title":notification_title, "notification_description": notification_description, "date": date, "user_id": ObjectId(user_id),"ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
    return render_template("user_message.html", message="Ticket added successfully")


@app.route("/view_tickets")
def view_tickets():
    if session['role'] == 'developer':
        developer_id = session['developer_id']
        query = {"developer_id": ObjectId(developer_id)}
    elif session['role'] == 'manager':
        manager_id = session['manager_id']
        query = {}
    elif session['role'] == 'user':
        user_id = session['user_id']
        query = {"user_id": ObjectId(user_id)}
    tickets = tickets_collection.find(query)
    tickets = list(tickets)
    return render_template("view_tickets.html", get_manager_by_manager_id=get_manager_by_manager_id, tickets=tickets, get_ticket_by_manager_id=get_ticket_by_manager_id, get_ticket_by_developer_id=get_ticket_by_developer_id, get_ticket_by_user_id=get_ticket_by_user_id,get_developer_by_developer_id=get_developer_by_developer_id, get_user_by_user_id=get_user_by_user_id)


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
        return redirect("/manager_home")
    else:
        return render_template("msg.html", message="Invalid Email and Password")


@app.route("/manager_home")
def manager_home():
    return render_template("manager_home.html")


@app.route("/accept_ticket")
def accept_ticket():
    ticket_id = request.args.get("ticket_id")
    manager_id = session['manager_id']
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket Accepted","manager_id": ObjectId(manager_id)}}
    tickets_collection.update_one(query1,query2)
    notification_title = "Ticket Accepted"
    notification_description = "The " + session['role'] + " updated status as Ticket Accepted"
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description":notification_description, "date":date,"ticket_id":ObjectId(ticket_id) }
    notifications_collection.insert_one(query)
    return redirect("/view_tickets")


@app.route("/reject_ticket")
def reject_ticket():
    ticket_id = request.args.get("ticket_id")
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket Rejected"}}
    tickets_collection.update_one(query1,query2)
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
    tickets_collection.update_one(query1,query2)
    notification_title = "Ticket Closed"
    notification_description = "The " + session['role'] + " updated status as Ticket Closed"
    date = datetime.datetime.now()
    query = {"notification_title": notification_title, "notification_description": notification_description,
             "date": date, "ticket_id": ObjectId(ticket_id)}
    notifications_collection.insert_one(query)
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
        return redirect("/developer_home")
    else:
        return render_template("msg.html", message="Invalid Email and Password")


@app.route("/developer_home")
def developer_home():
    return render_template("developer_home.html")


@app.route("/assign_to_developer")
def assign_to_developer():
    ticket_id = request.args.get("ticket_id")
    query = {}
    developers = developer_collection.find(query)
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


@app.route("/ticket_in_process")
def ticket_in_process():
    ticket_id = request.args.get("ticket_id")
    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "Ticket In Process"}}
    tickets_collection.update_one(query1, query2)
    notification_title = "Ticket In Process"
    notification_description = "The" + session['role'] + "updated status as Ticket In Process"
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


@app.route("/add_comment_action")
def add_comment_action():
    comment = request.args.get("comment")
    ticket_id = request.args.get("ticket_id")
    date = datetime.datetime.now()
    if session['role'] == 'manager':
        query = {"comment": comment, "manager_id":ObjectId(session['manager_id']), "role": session['role'], "date": date}
    elif session['role'] == 'developer':
            query = {"comment": comment, "developer_id": ObjectId(session['developer_id']), "role": session['role'], "date": date}
    elif session['role'] == 'user':
            query = {"comment": comment, "user_id": ObjectId(session['user_id']), "role": session['role'], "date": date}

    query1 = {"_id": ObjectId(ticket_id)}
    query2 = {"$push": {"comments": query}}
    tickets_collection.update_one(query1,query2)
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
    return render_template("add_ticket_update.html",ticket_id=ticket_id)


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
    query = {}
    ticket_updates = ticket_updates_collection.find(query)
    ticket_updates = list(ticket_updates)
    return render_template("view_ticket_updates.html", ticket_updates=ticket_updates)


@app.route("/manager_notifications")
def manager_notifications():
    manager_id = session['manager_id']
    query = {"manager_id":ObjectId(manager_id)}
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
    query = {"user_id":ObjectId(user_id)}
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
    query = {"developer_id":ObjectId(developer_id)}
    tickets = tickets_collection.find(query)
    ticket_ids = []
    for ticket in tickets:
        ticket_ids.append(ticket['_id'])
    query = {"ticket_id": {"$in": ticket_ids}}
    notifications = notifications_collection.find(query)
    return render_template("developer_notifications.html", notifications=notifications)


app.run(debug=True)
