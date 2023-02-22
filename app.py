import os
from flask import Flask, request, render_template,Response,make_response
from PIL import Image
from conversions import convert_to_jpg, convert_to_png, convertgif_toimg, convertto_art, convertto_grayscale, compress_image, convertto_gif
from pdftools import compress_pdf,convert_pdf
import io
import time
import base64
from utils4 import generate_unique_id

from pymongo import MongoClient

# client = MongoClient("mongodb://localhost:27017")
client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")

db = client["imageLab"]
pdf_collection = db["pdf_files"]
image_collection = db['Images']

app = Flask(__name__, template_folder='templates', static_folder='static',)


@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/pdftool")
def pdftools():
    return render_template("pdftool.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/pngtojpgconvert', methods=['POST'])
def png_to_jpg():
    return convert_to_jpg()

@app.route('/bgremove', methods=['POST']) 
def background_remove():
    return render_template("error.html",error_msg='Thank you for visiting! Our website is currently under construction. We apologize for any inconvenience.')
#     return remove_bg()

@app.route('/jpgtopngconvert', methods=['POST'])
def jpg_to_png():
    return convert_to_png()

@app.route('/topencilart', methods=['POST'])
def image_to_pencilart():
   return convertto_art()

@app.route('/tograyscale', methods=['POST'])
def to_grayscale():
   return convertto_grayscale()

@app.route('/togif', methods=['POST'])
def to_gif():
   return convertto_gif()

@app.route('/giftoimg', methods=['POST'])
def gif_to_img():
   return convertgif_toimg()

@app.route('/compressimg', methods=['POST'])
def img_compress():
   return compress_image()

@app.route('/compress', methods=['POST'])
def compresspdf():
    return compress_pdf()

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    return convert_pdf()

@app.route('/pdf/<user_id>')
def pdf_view(user_id):
    pdf_data = pdf_collection.find_one({"user_id": user_id})
    if pdf_data:
        pdf_binary_data = pdf_data["file"]
    else:
        return render_template("error.html",  error_msg='No file found on Database')
    response = Response(pdf_binary_data, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=pdf_file.pdf'
    return response

@app.route('/download/<user_id>')
def download(user_id):
    image_collection_data=image_collection.find_one({'user_id': user_id})
    if image_collection_data:
        binary_image_data = image_collection_data['image_data']
    else:
        return render_template("error.html",  error_msg='No file found on Database')
    image = Image.open(io.BytesIO(binary_image_data))
    image_format = image.format
    response = make_response(binary_image_data)
    response.headers.set('Content-Type', 'image/'+ image_format)
    response.headers.set('Content-Disposition', 'attachment', filename=f'img{int(time.time())}.{image_format}')
    return response

@app.route('/contact-form-handler', methods=['POST'])
def handle_contact_form():
    try:
        client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")
        db = client["imageLab"]
        contact_collection = db['contactForm']

        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        user_id = generate_unique_id()
        data = {"contactID":user_id,"name": name, "email": email, "message": message}
        contact_collection.insert_one(data)
        return render_template("contact.html", message="Successfully submitted",contactId=user_id)
    except Exception as e:
        return "Error occurred while saving form data: {}".format(str(e))

if  __name__ == "__main__":
    app.run();
