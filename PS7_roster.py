from sys import argv, exit
from cs50 import SQL

if len(argv) != 2:
    print("Correct Usage: python roster.py house")
    exit(1)

# Connect to database
db = SQL("sqlite:///students.db")

students = db.execute("SELECT * FROM students WHERE house = ? ORDER BY last, first", argv[1])

for student in students:
    # Take dict values and store them into named variables
    first, middle, last, birth = student["first"], student["middle"], student["last"], student["birth"]

    # Initialise name array
    name = []
    name.append(first)

    # Check if there is a middle name
    if middle is not None:
        name.append(middle)

    name.append(last)

    print(f"{' '.join(name)}, born {birth}")
