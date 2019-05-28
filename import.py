""" Program for importing a csv file into a postgres db """

import csv
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    if sys.argc != 2:
        print("Usage: import.py file.csv")
        exit()

    # We use the sys library to open a csv file on our local computer via terminal
    csv_file = open(f"{sys.argv[1]}")

    # We read the csv file
    reader = csv.reader(csv_file)

    # csv row counter
    num = 0

    for isbn,title,author,year in reader:

       print(f"{num} - ISBN {isbn}, Title {title}, Author {author}, Year {year}.")
       num = num + 1

       db.execute("INSERT INTO books (ISBN_number, title, author, publication_year) VALUES (:isbn, :title, :author, :year)",
       {"isbn": isbn, "title": title, "author": author, "year": year})

    # If we get to this point, the csv file was read succesfully
    print("CSV file was read succesfully!!!")

    db.commit()

if __name__ == "__main__":
    main()
