import os
import requests
import json

from types import *
from flask import Flask, session, render_template, jsonify, request, redirect, abort, send_from_directory
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

# Custom functions
from helpers import *

app = Flask(__name__)

# Aditional Static folder
app.config['CUSTOM_STATIC_PATH'] = "node_modules"

# Aditional Debugger
from flask_debugtoolbar import DebugToolbarExtension
app.debug = True
app.config["SECRET_KEY"] = "DontTellAnyone"

toolbar = DebugToolbarExtension(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Establish API KEY from goodreads.com
api_key = os.getenv("API_KEY_GOODREADS")


@app.route("/")
def index():
   return render_template("index.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    """Login user"""
    if request.method == "POST":

        # Forget any user_id
        session.clear()

        if request.method == "POST":

            # Ensure username was submitted
            if not request.form.get("username"):
                return jsonify({"message": "must provide username", "status": 403}) 

            # Ensure password was submitted
            elif not request.form.get("pass"):
                return jsonify({"message": "must provide password", "status": 403}) 

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username", {"username" : request.form.get("username") }).fetchone()
            rows = dict(rows)

            # Ensure username exists
            if rows is None:
                return jsonify({"message": "invalid username", "status": 403}) 

            # Ensure password is correct
            if not check_password_hash(rows['password'], request.form.get("pass")):
                return jsonify({"message": "invalid password", "status": 403}) 

            # Remember which user has logged in
            session["user_id"] = rows['user_id']

            # Redirect user to home page
            return redirect("/search")
    else:
        return render_template("login.html")

@app.route("/logout", methods = ['POST', 'GET'])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    
        
@app.route("/register", methods = ['POST', 'GET'])
def register_user():
    """Register user"""
    if request.method == "POST":
        
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("pass")
        #email = request.form.get("email")

        try:
            validate_username(username, db)
            validate_password(password)
            #validate_email(email)
        except ValueError as e:
            return jsonify({"message": str(e), "status": 400}) 

        # Convert original password to a hash
        hash_pass = generate_password_hash(password)

        # Insert user
        '''db.execute("INSERT INTO users (name,username, password, role_id) VALUES (:name, :username, :password, :role_id)",
        {"name": name, "username": username, "password": hash_pass, "role_id": 1})'''
        db.execute("INSERT INTO users (name,username, password) VALUES (:name, :username, :password)",
        {"name": name, "username": username, "password": hash_pass})

        db.commit()

        # Get user id from db
        user_id = db.execute("SELECT user_id FROM users WHERE username = :username",
        {"username": username }).fetchone()

        # Remember which user has logged in
        session["user_id"] = user_id[0]

        # Redirect user to home page
        return redirect("/")

    else:
         #Get countries lists json response from restcountries API
        countries = requests.get("https://restcountries.eu/rest/v2/all", params={"fields": "name"})

        return render_template("register.html", countries=countries.json())
    

@app.route("/search", methods = ['POST', 'GET'])
@login_required
def search():
    """Search book"""
    if request.method == "POST":

        search = request.form.get("search-input")

        """ Users should be able to type in the ISBN number of a book, 
        the title of a book, or the author of a book """

        if isinstance(search, str) & validate_string_content(search) == False:
            rows = db.execute(f"SELECT * FROM books WHERE \
            ( LOWER(title) LIKE '%{search.lower()}%' OR LOWER(author) LIKE '%{search.lower()}%' ) \
            LIMIT 50").fetchall()

        elif validate_string_content(search) == True:
            rows = db.execute(f"SELECT * FROM books WHERE ISBN_number LIKE '%{search}%' LIMIT 50").fetchall()

        if rows:
            json_response = []

            for row in rows:
                json_response.append({ 
                            "isbn_number": row[0],
                        "title": row[1],
                        "author": row[2],
                        "publication_year": row[3]
                })
            return jsonify({"success": True, "list": json_response}), 200

        else:
            return jsonify({"success": False, "message": "There is no Result on that search. Try other ISBN, book name or author"}), 404
    else:
        return render_template("search.html")


@app.route("/books/<string:isbn>", methods = ['POST', 'GET'])
@login_required
def show_book(isbn):
    """Search book"""
    if request.method == "POST":
        """ TODO Query Review """

        rating = request.form.get('rating')

        review_description = request.form.get('review-description')

        if validate_if_user_has_review(session["user_id"], isbn, db) == False:
            db.execute("INSERT INTO reviews (user_id, ISBN_number, score, description) VALUES (:user_id, :ISBN_number, :rating, :description)", 
            {"user_id": session['user_id'], "ISBN_number": isbn, "rating": rating, "description": review_description})

            db.commit()

            username = db.execute("SELECT username FROM users WHERE user_id = :id", {"id": session["user_id"]}).fetchone()

            return jsonify({"success": True, "rating": rating, "review_description": review_description, "username": username.username}), 200

        else: 
            return jsonify({"success": False, "message": "The User has already left a review"}), 403


    else:
        """ Book Details """

        # API Good Reads 
        goodreads_response = requests.get("https://www.goodreads.com/book/review_counts.json",  params={"key": api_key, "isbns": isbn})
        
        reviews = db.execute("SELECT reviews.score, reviews.description, username FROM reviews INNER JOIN users ON reviews.user_id = users.user_id WHERE isbn_number = :isbn",
        {"isbn" : isbn}).fetchall()

        book_details = db.execute("SELECT * FROM books WHERE isbn_number = :isbn", {"isbn": isbn}).fetchone()

        print(session["user_id"])

        user_has_review = validate_if_user_has_review(session["user_id"], isbn, db)

        if book_details is None:
            abort(404)

        return render_template("book.html", book_details = book_details, reviews = reviews, goodreads_response = goodreads_response.json(),
        user_has_review = user_has_review, isbn = isbn)


""" API ACCESS """
@app.route('/api/<string:isbn>')
@login_required
def get_book_review_summary(isbn):
    """ Via Get Method, send the review summary of the request isbn  """

    review_summary = db.execute("SELECT title, author, publication_year, reviews.isbn_number, COUNT(reviews.isbn_number), \
    AVG(score) FROM books INNER JOIN reviews ON books.ISBN_number = reviews.ISBN_number  \
    WHERE books.isbn_number = :isbn GROUP BY reviews.isbn_number, publication_year, title, author",
    {"isbn": isbn}).fetchone()

    if review_summary:
        return jsonify({
        "title": review_summary[0],
        "author": review_summary[1], 
        "publication_year": review_summary[2], 
        "isbn_number": review_summary[3],
        "review_count": review_summary[4],
        "score": review_summary[5]
        }), 200

    # If the above query does not get a result, that means that the requested isbn do not have a review
    # Let´s see if the isbn is loaded in the db. If it stills returns a None value, that means that the requested isbn does not exists
    if review_summary == None:
        review_summary = db.execute("SELECT title, author, publication_year, isbn_number FROM books WHERE ISBN_number = :isbn", {"isbn": isbn}).fetchone()

    if review_summary:
        return jsonify({
        "title": review_summary[0],
        "author": review_summary[1], 
        "publication_year": review_summary[2], 
        "isbn_number": review_summary[3],
        "review_count": 0,
        "score": 0
        }), 200
    else: 
        return jsonify({"message": "The isbn has not being found"}), 404

# Custom static data
@app.route('/node_modules/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['CUSTOM_STATIC_PATH'], filename)