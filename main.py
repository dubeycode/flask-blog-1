from flask import Flask, render_template, request, url_for, session, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json, os
import math
from flask_migrate import Migrate

# try:
#     with open(r"tech_blog\config.json", "r") as c:
#         params = json.load(c)["params"]
# except Exception as e:
#     params = {}


try:
    with open(r"./config.json", "r") as c:
        params = json.load(c)["params"]
except Exception as e:
    print("Error loading config.json:", e)


local_server = "True"

app = Flask(__name__)
app.secret_key = "4f3c2b1a5d6e7f8g9h0i1j2k3l4m5n6o"  # Strong Secret Key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///byteverse.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Add this line
# app.config['UPLOAD_FOLDER']=params['uplod_location']
import os

# Use absolute path on local machine
if "localhost" in os.getenv("FLASK_ENV", ""):
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "static", "assets", "img")
else:
    # Use relative path for cloud hosting (Render/Vercel)
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "static", "assets", "img")


# ----------------------------Email Configuration---------------------------#
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["gmail_user"],
    MAIL_PASSWORD=params["gmail_pass"],
)
mail = Mail(app)

# ----------------------------------Database Configuration----------------------#
if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]


# ----------------------------------- Database control coontact -------------------------#
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=True)


# ----------------------------------- Database control Post -------------------------#
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(20), nullable=False)
    subtitle = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


# ----------------------------------- Home route -------------------------#
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params["no_of_posts"]))
    page = request.args.get("page")
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[
        (page - 1)
        * int(params["no_of_posts"]) : (page - 1)
        * int(params["no_of_posts"])
        + int(params["no_of_posts"])
    ]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template(
        "index.html", params=params, posts=posts, prev=prev, next=next
    )


# -----------------------------------About route -------------------------#
@app.route("/about")
def about():
    return render_template("about.html", params=params)


# ----------------------------------- Get post for dashboard -------------------------#
@app.route("/post/<string:post_slug>", methods=["GET"])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=post)


# ----------------------------------- Login method and section  -------------------------#
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session and session["user"] == params["admin_user"]:
        return redirect(url_for("dashboard"))  # Redirect if already logged in

    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")

        if username == params["admin_user"] and userpass == params["admin_password"]:
            session["user"] = username
            return redirect(url_for("dashboard"))  # Redirect to dashboard after login

        return render_template(
            "login.html", params=params, error="Invalid credentials!"
        )

    return render_template(
        "login.html", params=params
    )  # Show login page if GET request


# ----------------------------------- Dashboard route-------------------------#
@app.route("/dashboard")
def dashboard():
    if "user" not in session or session["user"] != params["admin_user"]:

        return redirect(url_for("login"))  # if not logged in
    posts = Posts.query.filter_by().all()

    return render_template(
        "dashboard.html", params=params, posts=posts
    )  # Show dashboard if logged in


# -----------------------------------Log out route -------------------------#
@app.route("/logout")
def logout():
    session.pop("user", None)  # Clears the entire session
    return redirect(url_for("login"))  # Redirect to login page


# -----------------------------------Delete-------------------------#
@app.route("/delete/<int:sno>", methods=["GET", "POST"])
def delete(sno):
    if "user" in session and session["user"] == params["admin_user"]:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


# ----------------------------------- Admin power  -------------------------#


@app.route("/edit/<string:sno>", methods=["GET", "POST"])
def edit(sno):
    if "user" in session and session["user"] == params["admin_user"]:
        post = None  # Initialize post to avoid errors

        if sno != "0":  # If editing an existing post
            post = Posts.query.filter_by(sno=sno).first()

        if request.method == "POST":  # If form is submitted
            box_title = request.form.get("title", "")
            tline = request.form.get("tline", "")
            subtitle = request.form.get("subtitle", "")
            slug = request.form.get("slug", "")
            content = request.form.get("content", "")
            img_file = request.form.get("img_file", "")
            date = datetime.now()

            if sno == "0":  # Creating a new post
                new_post = Posts(
                    title=box_title,
                    slug=slug,
                    content=content,
                    subtitle=subtitle,
                    tagline=tline,
                    img_file=img_file,
                    date=date,
                )
                db.session.add(new_post)
                db.session.commit()
                return redirect(url_for("edit", sno=new_post.sno))

            elif post:  # Updating an existing post
                post.title = box_title
                post.tagline = tline
                post.subtitle = subtitle
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect(url_for("edit", sno=sno))

        return render_template("edit.html", params=params, sno=sno, post=post)


# ----------------------------------- file uploder route -------------------------#
# @app.route("/uploder",methods=['GET','POST'])
# def uploder():
#     if 'user' in session and session["user"] == params["admin_user"]:
#         if (request.method=='POST'):
#             f=request.files['file1']
#             f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
#             return "uploded successfully"


# ----------------------------------- Coontact form route -------------------------#
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        message = request.form.get("message")

        entry = Contacts(
            name=name, phone_num=phone, msg=message, email=email, date=datetime.now()
        )
        db.session.add(entry)
        db.session.commit()

        mail.send_message(
            "New Message from ByteVerse by " + name,
            sender=email,  # Use user's email as sender
            recipients=[params["gmail_user"]],
            body=message + "\nPhone: " + phone,
        )

    return render_template("contact.html", params=params)


# ----------------------------------- Main -------------------------#
if __name__ == "__main__":
    app.run(debug=True)
