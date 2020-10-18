# Program should accept the name of a house as a CLA

# e.g. $ python roster.py Gryffindor
# Hermione Jean Granger, born 1979

from sys import argv, exit
import cs50
from cs50 import SQL
import csv

if len(argv) != 2:
    print("missing command-line argument: please include house")
    exit(1)

db = cs50.SQL("sqlite:///students.db")

for row in db.execute("SELECT * FROM Students LIMIT 5;"):
    print(row)
