# e.g. $ python import.py characters.csv
# after running above - run sqlite3 students.db to run SQL
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
db.execute("CREATE TABLE students (fname TEXT, mName TEXT, lName TEXT, house TEXT, birth TEXT)")

# Open CSV file
with open(argv[1], "r") as characters:
    # Create DictReader
    reader = csv.DictReader(characters, delimiter=',')

    for row in reader:
        name = row["name"]
        house = row["house"]
        birth = row["birth"]

        # Use split function on name to split into words
        # example 1: Hannah Abbott      => Hannah, Abbott
        # example 2: Harry James Potter => Harry, James, Potter
        splitName = name.split(" ")

        # full name does not have a middle name
        if len(splitName) == 2:
            db.execute("INSERT INTO students(fName, mName, lName, house, birth) VALUES(?, ?, ?, ?, ?)", splitName[0], None, splitName[1], house, birth)

        # full name has a middle name
        elif len(splitName) == 3:
            db.execute("INSERT INTO students(fName, mName, lName, house, birth) VALUES(?, ?, ?, ?, ?)", splitName[0], splitName[1], splitName[2], house, birth)
