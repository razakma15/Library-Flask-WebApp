import os
import requests
import csv
from flask import Flask, render_template, request
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker



app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/book_page",methods=["POST"])
def search():
    search_details = request.form.get("search_bar")
    detail_bar = request.form.get("detail_bar")
    detail_bar = detail_bar.lower()
    if search_details != "" and detail_bar != "":
        book_data = db.execute(f"SELECT * FROM books WHERE {detail_bar} LIKE '%{search_details}%'").fetchall()
        if book_data != []:
            loop_length = len(book_data)
            avg_rating = []
            for x in range(loop_length):
                res = requests.get("https://www.goodreads.com/book/review_counts.json", params={f"key": "enBGskZA1A4vM2AIKcWjw", "isbns": {book_data[x][1]} })
                response = res.json()
                response = response['books']
                response = response[0]
                response = response['average_rating']
                avg_rating.append(response)
                return render_template("Book_page.html",book_data=book_data,loop_length=loop_length,response=avg_rating)
        else:
            return render_template("Search_error.html")
    else:
        return render_template("Search_error.html")

@app.route("/")
def home():
    return render_template("Main_page.html")


@app.route("/login")
def login():
    return render_template("Login.html")

@app.route("/login_further",methods=["POST"])
def login_f():
    username = request.form.get("username_login")
    password = request.form.get("password_login")
    if username != "" or password != "":
        login_data = db.execute("SELECT username_col,password_col FROM login").fetchall()
        loop_count = db.execute("SELECT COUNT(*) FROM login").fetchall()
        loop_count = loop_count[0][0]
        for x in range(loop_count):
            if username == login_data[x][0] and password == login_data[x][1]:
                username = "verified"
                return render_template("Login_further.html",username=username)
            else:
                if x == (loop_count - 1):
                    username = "not verified"
                    return render_template("Login_further.html",username=username)
    else:
        username = "no inputs"
        return render_template("Login_further.html",username=username)


@app.route("/create")
def create():
    return render_template("Create.html")

@app.route("/create_further",methods=["POST"])
def create_f():
    verification_data = db.execute("SELECT username_col,password_col FROM login").fetchall()
    loop_count = db.execute("SELECT COUNT(*) FROM login").fetchall()
    loop_count = loop_count[0][0]
    new_username = request.form.get("username_create")
    new_password = request.form.get("password_create")
    if new_password != "" and new_username != "":
        for x in range(loop_count):
            if new_username == verification_data[x][0]:
                return render_template("Create_further.html")
            else:
                if x == (loop_count - 1):
                    login_list = [new_username,new_password]
                    db.execute("INSERT INTO login (username_col,password_col) VALUES (:u,:p)",{"u":login_list[0],"p":login_list[1]})
                    db.commit()
                    login_list = "verified"
                    return render_template("Create_further.html",new_username=new_username,new_password=new_password,login_list=login_list)
    else:
        return render_template("Create_further.html")

@app.route("/form")
def tester():
    return render_template("Main_page.html", name=response)
