from sys import argv, exit
import csv
from cs50 import SQL

if len(argv) != 2:
    print("Correct Usage: python import.py characters.csv")
    exit(1)

# Connect to database
db = SQL("sqlite:///students.db")

with open(argv[1], "r") as students:

    # Create DictReader
    reader = csv.DictReader(students)

    for row in reader:
        name = row["name"].split()
        first_name = name[0]

        # Check if there is a middle name
        if len(name) == 3:
            middle_name = name[1]
            last_name = name[2]
        else:
            middle_name = None
            last_name = name[1]

        # SQL query
        db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)",
                    first_name, middle_name, last_name, row["house"], row["birth"])
