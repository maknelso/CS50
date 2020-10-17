#WIP

# e.g. $ python import.py characters.csv
# Take CSV and import that data into a SQLite db
from sys import argv, exit
import cs50
from cs50 import SQL
import csv

if len(argv) != 2:
    print("missing command-line argument")
    exit(1)

# Create db by opening and closing file first
open(f"students.db", "w").close()

# Open that file for SQLite
db = cs50.SQL("sqlite:///students.db")

# Create table called students in database file called students.db
# Specific columns we want - db.execute("CREATE TABLE students(fName TEXT, mName TEXT, lName TEXT, house TEXT, year TEXT")
db.execute("CREATE TABLE students (name TEXT, house TEXT, birth TEXT)")

# Open CSV file
with open(argv[1], "r") as characters:
    # Create DictReader
    reader = csv.DictReader(characters, delimiter=',')

    for row in reader:
        name = row["name"]
        house = row["house"]
        birth = row["birth"]

        # Insert into students db
        db.execute("INSERT INTO students(name, house, birth) VALUES(?, ?, ?)", name, house, birth)
