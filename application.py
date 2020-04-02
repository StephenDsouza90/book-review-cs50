import os
import requests
import waitress

from flask import Flask, session, request, render_template, redirect, jsonify, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from modelsP1 import SQLBackend
from decorator import handle_session


def create_app(db):
    """ Creates the server app """

    app = Flask(__name__)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    # scoped_session from SQLBackend class
    db = db.db

    @app.route("/")
    @handle_session
    def index():
        """ Home page """

        return render_template("index.html")

    @app.route("/sign-up", methods=["GET", "POST"])
    def sign_up():
        """ User sign up """

        session.clear()
        if request.method == "POST":

            existing_user = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username":request.form.get("username")}).fetchone()

            if not request.form.get("username"):
                return render_template("error.html", 
                    message="Please provide username!")

            elif existing_user:
                return render_template("error.html", 
                    message="Username already exist!")

            elif not request.form.get("password"):
                return render_template("error.html", 
                    message="Please provide password!")

            elif not request.form.get("confirmation"):
                return render_template("error.html", 
                    message="Please provide confirmation for password!")

            elif not request.form.get("password") == request.form.get("confirmation"):
                return render_template("error.html", 
                    message="Passwords do not match!")

            else:
                hash_password = generate_password_hash(request.form.get("password"), 
                                    method='pbkdf2:sha256', salt_length=8)   
                db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username":request.form.get("username"), 
                    "password":hash_password})
                db.commit()
                return redirect("/login")

        else:
            return render_template("sign_up.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """ User login """

        session.clear()
        if request.method == "POST":

            record = db.execute("SELECT * FROM users WHERE username = :username", 
                {"username": request.form.get("username")}).fetchone()

            if not request.form.get("username"):
                return render_template("error.html", message="Please provide username!")

            elif not request.form.get("password"):
                return render_template("error.html", message="Please provide password!")

            elif record == None:
                return render_template("error.html", message="User does not exist!")

            elif not check_password_hash(record[1], request.form.get("password")):
                return render_template("error.html", message="Invalid password!")

            else:
                session["username"] = record[0]
                return redirect("/")

        else:
            return render_template("login.html")

    @app.route("/logout")
    def logout():
        """ User logout """

        session.clear()
        return redirect("/")

    @app.route("/search", methods=["GET"])
    @handle_session
    def search():
        """ Seach for books """

        if not request.args.get("book"):
            return render_template("error.html", 
                message="Please enter ISBN, Title or Author!")

        query = "%" + request.args.get("book") + "%"
        query = query.title()
        rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                isbn LIKE :query OR \
                title LIKE :query OR \
                author LIKE :query \
                LIMIT 10",
                {"query": query})

        if rows.rowcount == 0:
            return render_template("error.html", message="Book cannot be found in database!")
        else:
            books = rows.fetchall()
            return render_template("results.html", books=books)

    @app.route("/book/<isbn>", methods=["GET","POST"])
    @handle_session
    def book(isbn):
        """ User review, rating and comments."""

        if request.method == "POST":
            result = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn",
                    {"username": session["username"],
                    "isbn": isbn})

            if result.rowcount == 1:            
                flash('Only one review submission allowed!', 'warning')
                return redirect("/book/" + isbn)

            else:
                db.execute("INSERT INTO reviews (username, isbn, comments, rating) \
                    VALUES (:username, :isbn, :comments, :rating)",
                    {"username": session["username"], 
                    "isbn": isbn, 
                    "comments": request.form.get("comments"), 
                    "rating": request.form.get("rating")})
                db.commit()
                flash('Review submitted!', 'info')
                return redirect("/book/" + isbn)
        
        else:
            book_details = db.execute("SELECT isbn, title, author, year FROM books \
                        WHERE isbn = :isbn",
                        {"isbn": isbn}).fetchall()
            # Ratings from GOODREADS
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                    params={"key": os.environ.get("GOODREADS_KEY"), "isbns": isbn})

            if res.status_code == 200:
                response = res.json()
                response = response['books'][0]
                book_details.append(response)

            else:
                # 0 is missing from some isbn in books.csv 
                res = requests.get("https://www.goodreads.com/book/review_counts.json",
                    params={"key": os.environ.get("GOODREADS_KEY"), "isbns": "0"+isbn})
                response = res.json()
                response = response['books'][0]
                book_details.append(response)

            # Reviews from users
            reviews = db.execute("SELECT users.username, comments, rating \
                                FROM users \
                                INNER JOIN reviews \
                                ON users.username = reviews.username \
                                WHERE isbn = :isbn", \
                                {"isbn": isbn}).fetchall()
            return render_template("book.html", book_details=book_details, reviews=reviews)

    @app.route("/api/<isbn>", methods=["GET"])
    @handle_session
    def api_call(isbn):
        """ JSON response for user's GET request """

        row = db.execute("SELECT title, author, year, books.isbn, \
                        COUNT(reviews.isbn) as review_count, \
                        AVG(reviews.rating) as average_score \
                        FROM books \
                        FULL OUTER JOIN reviews \
                        ON books.isbn = reviews.isbn \
                        WHERE books.isbn = :isbn \
                        GROUP BY title, author, year, books.isbn",
                        {"isbn": isbn})
        
        if row.rowcount != 1:
            return jsonify({"Error": "ISBN number isn’t in database!"}), 404

        else:
            r = row.fetchone()
            result = {
                "title": r[0],
                "author": r[1],
                "year": r[2],
                "isbn": r[3],
                "review_count": r[4],
                "average_score": r[5]
            }
            return jsonify(result)

    return app


def main():
    """ Run the server """

    DATABASE_URL = os.environ.get('DATABASE_URL')
    db = SQLBackend(DATABASE_URL)
    app = create_app(db)
    waitress.serve(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()