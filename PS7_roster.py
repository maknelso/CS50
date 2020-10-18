# Program should accept the name of a house as a CLA
# e.g. $ python roster.py Gryffindor
from sys import argv, exit
import cs50
from cs50 import SQL
import csv

if len(argv) != 2:
    print("missing command-line argument: please include house")
    exit(1)

# Open the file for SQLite
db = cs50.SQL("sqlite:///students.db")

rows = db.execute("SELECT * FROM Students WHERE house = ? ORDER BY lName, fName", argv[1])
for row in rows:
    # Give myself alias for easier typing
    fName, mName, lName, birth = row["fName"], row["mName"], row["lName"], row["birth"]

    if mName == None:
        print(f"{fName} {lName}, born {birth}")
    elif mName != None:
        print(f"{fName} {mName} {lName}, born {birth}")
