import os
import re

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///info.db")

@app.route("/")
def index():
    """ Show the last 5 most recently submitted information"""
    submissions = db.execute("""
                               SELECT company, base_salary, bonus, rsu, SUM(base_salary + bonus + RSU) AS TC, city, transacted
                               FROM info
                               GROUP BY id
                               ORDER BY id DESC
                               LIMIT 5
                              """
                            )

    for i in range(len(submissions)):
        company = submissions[i]["company"]
        TC = submissions[i]["TC"]
        city = submissions[i]["city"]
        transacted = submissions[i]["transacted"]

    return render_template("homepage.html", submissions=submissions, company=company, TC=TC, city=city, transacted=transacted)


@app.route("/submit_salary", methods=["GET", "POST"])
def submit_salary():
    if request.method == "POST":

        # Error check form first:
        if not request.form.get("city"):
            return ("ERROR: Please enter in a city.")

        elif not request.form.get("company"):
            return ("ERROR: Please enter in a company name.")

        elif not request.form.get("jcategory"):
            return ("ERROR: Please select a job category.")

        elif not request.form.get("jsubcategory"):
            return ("ERROR: Please select a job sub-category.")

        elif not request.form.get("jdiffer"):
            return ("ERROR: Please select a job differentiator.")

        elif not request.form.get("title"):
            return ("ERROR: Please enter in a job title.")

        elif not request.form.get("yoe"):
            return ("ERROR: Please enter in valid year(s) of experience.")
        elif not request.form.get("yoe").isdigit() or int(request.form.get("yoe")) < 0:
            return ("ERROR: Please enter in valid year(s) of experience.")

        elif not request.form.get("base_salary"):
            return ("ERROR: Please enter a base salary.")
        elif not request.form.get("base_salary").isdigit() or int(request.form.get("base_salary")) < 0:
            return ("ERROR: Please enter a valid base salary")

        elif not request.form.get("bonus"):
            return ("ERROR: Please enter a bonus amount.")
        elif not request.form.get("bonus").isdigit() or int(request.form.get("bonus")) < 0:
            return ("ERROR: Please enter a valid bonus")

        elif not request.form.get("rsu"):
            return ("ERROR: Please enter Restricted Share Unit vest fair market value per year (if applicable).")
        elif not request.form.get("rsu").isdigit() or int(request.form.get("rsu")) < 0:
            return ("ERROR: Please enter a valid FMV for RSU")

        # Declare variable for ease of reference
        else:
            city = request.form.get("city")
            company = request.form.get("company")
            jcategory = request.form.get("jcategory")
            jsubcategory = request.form.get("jsubcategory")
            jdiffer = request.form.get("jdiffer")
            title = request.form.get("title").lower()
            yoe = request.form.get("yoe")
            base_salary = request.form.get("base_salary")
            bonus = request.form.get("bonus")
            rsu = request.form.get("rsu")

            # Update database
            db.execute("""
                       INSERT INTO info (city, company, jcategory, jsubcategory, jdiffer, title, yoe, base_salary, bonus, rsu)
                       VALUES (:city, :company, :jcategory, :jsubcategory, :jdiffer, :title, :yoe, :base_salary, :bonus, :rsu)
                       """,
                       city=city, company=company, jcategory=jcategory, jsubcategory=jsubcategory, jdiffer=jdiffer,
                       title=title, yoe=yoe, base_salary=base_salary, bonus=bonus, rsu=rsu
                      )

            return redirect("/")

    else:
        return render_template("submit_salary.html")

@app.route("/estimate_salary", methods=["GET", "POST"])
def estimate_salary():
    """Estimate Salary page"""
    if request.method == "POST":

        # Declare variable for ease of reference
        city = request.form.get("city")
        jcategory = request.form.get("jcategory")
        jsubcategory = request.form.get("jsubcategory")
        jdiffer = request.form.get("jdiffer")
        yoe = request.form.get("yoe")

        # Need to get AVG salary
        # AVG: SUM(base_salary + bonus + rsu) / COUNT(*) AS average_salary
        database = db.execute("""
                              SELECT COUNT(id) AS count_num, SUM(base_salary + bonus + rsu) / COUNT(*) AS average_salary
                              FROM info
                              WHERE city = :city
                              AND jcategory = :jcategory
                              AND jsubcategory = :jsubcategory
                              AND jdiffer = :jdiffer
                              AND yoe = :yoe
                              """,
                              city=city, jcategory=jcategory, jsubcategory=jsubcategory, jdiffer=jdiffer, yoe=yoe
                             )

        average_salary = database[0]["average_salary"]
        count = database[0]["count_num"]

        return render_template("estimatedsalary.html", average_salary=average_salary, count=count)

    else:
        return render_template("estimate_salary.html")

@app.route("/about")
def about():
    """ About page"""
    return render_template("about.html")
