import os


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    MONGO_URI = 'mongodb://localhost:27017'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/raise_ticket_images')
    #MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maximum file upload size (16MB)
