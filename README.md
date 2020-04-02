# Book Review Website

This project is a book review website in which a user can sign up and login to view reviews of books. 

A user can search for books using a book's ISBN, Title or Author's name. The results returned are either an exact match to the user's request or a list of possible matches. The user can then go to the book's page to find out more details about the book, in particular the book's ratings and comments from other users and the average ratings and number of ratings from [goodreads](https://www.goodreads.com/). Goodreads is a popular book review website. The user can also give their own rating and comment for the book.


## Database

This project uses the PostgreSQL database hosted by [Heroku](https://www.heroku.com/). 

The tables in the database are:

1. users
2. books
3. reviews

### Users Table

When a user signs up for the website, their user name and a hash password is stored in the users table.

### Books Table

In this table, a csv file has been used via `import.py` to import and store a book's ISBN, Title, Author and Year in the books table.

To run the import:

```
>> python import.py
```

### Reviews Table

When a user provides a rating and comment, it is stored in the reviews table.

### Connection to the DB

In the `modelsP1.py`, the SQLBackend class handles creating the engine and scoped session. The connection string of Postgres is stored in the environment variable `DATABASE_URL`.


## The Application

The `application.py` uses Flask to create RESTFUL APIs, SQLALchemy for raw SQL commands while the user interface is a website.

To run the application:

```
>> python application.py
```

## Install Dependencies

The dependencies are saved in the requirements.txt file. 

It can be installed via the following command:

```

>> pip install -r requirements.txt

```