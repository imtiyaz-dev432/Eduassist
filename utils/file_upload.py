import os
from uuid import uuid4
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf"}

#this line checks pdf is presnt or not and if present it can be split into two parts by right side
def allowed_pdf(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Keep the original misspelled helper available for any existing imports.
def alllowed_pdf(filename):
    return allowed_pdf(filename)


def save_pdf(file, upload_folder): #this line file and konse folder mein upload hogi
    if not file:
        return None
    if file.filename == "":
        return None

    original_filename = secure_filename(file.filename) #file made a  secure 
    if not original_filename or not allowed_pdf(original_filename):
        raise ValueError("Only PDF files are allowed")

    extension = original_filename.rsplit(".", 1)[1].lower() #name of pdf can be divided into two types 
    unique_filename = f"{uuid4().hex}.{extension}" #give unique  name to every pdf

    os.makedirs(upload_folder, exist_ok=True) #check folder is present or not if not then created 
    file_path = os.path.join(upload_folder, unique_filename) #this line can make a path
    file.save(file_path) #this line save pdf

    return {
        "stored_filename": unique_filename,
        "original_filename": original_filename
    }        
