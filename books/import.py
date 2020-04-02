import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


with open("books.csv", "r") as csv_file:
    csv_read = csv.reader(csv_file)
    next(csv_read)

    for isbn, title, author, year in csv_read:
        db.execute("INSERT INTO tests (isbn, title, author, year) \
            VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, 
            "title": title,
            "author": author,
            "year": year})
        db.commit()
    print("Books added!")