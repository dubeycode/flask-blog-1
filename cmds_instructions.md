changes made in config.json file:

{
    "params": {
        "local_server": "True",
        "local_uri": "sqlite:///byteverse.db",
        "prod_uri": "sqlite:///byteverse.db",
        "tw_url": "https://x.com/Dube72281Satyam",
        "git_hub_url": "https://github.com/",
        "linkdin_url": "https://www.linkedin.com/in/satyam-dubey-863a68304/",
        "gmail_user": "example@gmail.com",
        "gmail_pass": "your_pass",
        "blog": "Byteverse",
        "about_text": "",
        "no_of_posts": "2",
        "admin_user": "dubey@",
        "admin_password": "123456789",
        "uplod_location": "static/assets/img"
    }
}


# app.config['UPLOAD_FOLDER']=params['uplod_location']

------- What we acutally do here is we are using relative path,by get the current working dir which is flas-blog here ---- then we upload the static files in project-dir/static/assets/img

if "localhost" in os.getenv("FLASK_ENV", ""):
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "static", "assets", "img")
else:
    # Use relative path for cloud hosting (Render/Vercel)
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "static", "assets", "img")


I have used sqlite which is easy to configure and use in our project and we dont need a seperate server for the Database - sqlite is file based db so we can setup the flask app in render without a seperate a db server


export FLASK_APP=main.py
flask run


flask db init
flask db migrate -m "Initial migration"
flask db upgrade

