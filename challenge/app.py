import os
import re
from flask import Flask, make_response, redirect, send_file, render_template, request, session, url_for
from werkzeug.utils import secure_filename
import jwt
from controls.database import Database
from controls.convert_pdf import *

app = Flask(__name__)
app.secret_key = os.urandom(32)

JWT_ALG = "HS256"
JWT_KEY = "640ac4e02546bdee1a7fc487b970d3ff"
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'txt', 'html', 'png', 'jpg', 'jpeg'}

@app.before_request
def before_request():
    if request.path == "/login" or request.path == "/register":
        return
    session.clear()
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

database = Database()

def create_jwt(user):
    header = {
        "alg": JWT_ALG,
        "typ": "JWT"
    }
    payload = {
        "login": True,
        "username": user[1],
        "is_admin": user[3]
    }
    return jwt.encode(payload, JWT_KEY, algorithm=JWT_ALG, headers=header)

def is_admin(jwt_payload):
    return jwt_payload.get('is_admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "GET":
        return render_template("verify.html", title="Register to the Hell's Lab")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

    if not username or not password:
        return render_template("error.html", title="Error", error="missing parameters", redirect_url="/register"), 400

    status = database.create_user(username, password)
    if not status:
        session.clear()
        return render_template("error.html", title="Error", error=f"User {username} already exists",
                               redirect_url="/register"), 400
    else:
        return render_template("success.html", title="Create Successful",
                               message=f"User {username} created successfully", redirect_url="/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("verify.html", title="Log-in to the Hell's Lab")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("error.html", title="Error", error="missing parameters", redirect_url="/login"), 400

        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:-]')
        if regex.search(username) or regex.search(password):
            return render_template("error.html", title="Error", error="invalid username or password",
                                   redirect_url="/login"), 400

        user, status = database.get_user(username, password)
        if status == False:
            return render_template("error.html", title="Error", error="invalid credentials", redirect_url="/login"), 400
        if user:
            token = create_jwt(user)
            response = make_response(redirect(url_for("home")))
            response.set_cookie("token", token)
            return response
    return render_template("error.html", title="Error", error="unknown error", redirect_url="/login"), 500


@app.route("/", methods=["GET", "POST"])
def index():
    session.clear()
    response = make_response(redirect(url_for("login")))
    response.set_cookie("token", "", expires=0)
    return response


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    response = make_response(redirect(url_for("login")))
    response.set_cookie("token", "", expires=0)
    return response


@app.route("/home", methods=["GET", "POST"])
def home():
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("login"))

    try:
        jwt_payload = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.InvalidTokenError:
        return redirect(url_for("login"))
    
    if not jwt_payload.get("login"):
        return redirect(url_for("login"))
    
    if jwt_payload.get('login'):
        return render_template("home.html", title="Welcome to the Hell's Lab")

@app.route("/convert", methods=["GET", "POST"])
def convert_2_pdf():
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("login"))
    
    try:
        jwt_payload = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.InvalidTokenError:
        return redirect(url_for("login"))
    
    if not jwt_payload.get("login"):
        return redirect(url_for("login"))
    
    if jwt_payload.get('login') and is_admin(jwt_payload):
        if request.method == "GET":
            return render_template("admin.html", title="Convert PDF to Text")

        if request.method == "POST":
            # check if the post request is input text or file html uploaded
            file = request.files.get('file')            
            if not file:
                return render_template("error.html", title="Error", error="No file provided", redirect_url="/convert"), 400

            if file:
                try:
                    if file.filename == '':
                        return render_template("error.html", title="Error", error="No selected file", redirect_url="/convert"), 400
                    if not allowed_file(file.filename):
                        return render_template("error.html", title="Error", error="Are you Hacking me?", redirect_url="/convert"), 400
                    # if file is html, convert to pdf
                    if file.filename.rsplit('.', 1)[1].lower() in ['html', 'txt']:
                        filename = secure_filename(file.filename)
                        new_filename = os.urandom(16).hex() + '.' + file.filename.rsplit('.', 1)[1].lower()
                        file.save(os.path.join(UPLOAD_FOLDER, new_filename))
                        if file.filename.rsplit('.', 1)[1].lower() == "html":      
                            pdf_file = html_to_pdf(os.path.join(UPLOAD_FOLDER, new_filename))
                        else:
                            pdf_file = text_to_pdf(os.path.join(UPLOAD_FOLDER, new_filename))
                        
                        # Save the pdf file to the server
                        pdf_filename = os.urandom(16).hex() + '.pdf'
                        pdf_file.seek(0)
                        with open(os.path.join(UPLOAD_FOLDER, pdf_filename), 'wb') as f:
                            f.write(pdf_file.read())
                        pdf_file.close()
                        return render_template("view_file.html", pdf_filename=pdf_filename)
                    elif file.filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']:
                        filename = secure_filename(file.filename)
                        new_filename = os.urandom(16).hex() + '.' + file.filename.rsplit('.', 1)[1].lower()
                        file.save(os.path.join(UPLOAD_FOLDER, new_filename))
                        pdf_file = image_to_pdf(os.path.join(UPLOAD_FOLDER, new_filename))
                        # Save the pdf file to the server
                        pdf_filename = os.urandom(16).hex() + '.pdf'
                        pdf_file.seek(0)
                        with open(os.path.join(UPLOAD_FOLDER, pdf_filename), 'wb') as f:
                            f.write(pdf_file.read())
                        pdf_file.close()
                        return render_template("view_file.html", pdf_filename=pdf_filename)
                except Exception as e:
                    return render_template("error.html", title="Error", error="Maybe Wrong Format", redirect_url="/convert"), 500
    return render_template("error.html", title="Error", error="Are you Hacking me?", redirect_url="/login"), 500

@app.route("/view_pdf", methods=["GET"])
def view_pdf():
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("login"))
    
    try:
        jwt_payload = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.InvalidTokenError:
        return redirect(url_for("login"))
    
    if not jwt_payload.get("login"):
        return redirect(url_for("login"))
    
    if jwt_payload.get('login'):
        pdf_filename = request.args.get('f')
        if not pdf_filename:
            return render_template("error.html", title="Error", error="No file provided", redirect_url="/convert"), 400
        return send_file(os.path.join(UPLOAD_FOLDER, pdf_filename), as_attachment=False)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=11223)
