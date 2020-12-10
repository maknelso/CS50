import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    portfolio = db.execute("""SELECT symbol, SUM(shares) AS total_shares
                              FROM transactions
                              WHERE user_id = :user_id
                              GROUP BY symbol
                              HAVING total_shares > 0
                              ORDER BY symbol""",
                              user_id=session["user_id"])

    # Initialize an empty dictionary
    holdings = []
    grand_total = 0

    for row in portfolio:
        # Use lookup function, lookup the symbol from portfolio tbl and store dict in a variable named stock
        stock = lookup(row["symbol"])
        # Append dict into holdings - key value pairs
        holdings.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "shares": row["total_shares"],
            "price": usd(stock["price"]),
            "total": usd(stock["price"] * row["total_shares"])
        })
        grand_total += stock["price"] * row["total_shares"]

    rows = db.execute("SELECT cash FROM users WHERE id = :id",
                       id=session["user_id"])
    cash = rows[0]["cash"]
    grand_total += cash

    # holdings=holdings is for the loop in index.html
    return render_template("index.html", holdings=holdings, cash=usd(cash), grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # Error checking:
        quoted = lookup(request.form.get("symbol"))
        if quoted == None:
            return apology("Please enter a valid ticker symbol.")
        elif not request.form.get("shares"):
            return apology("Please enter number of shares you desire to purchase.")
        elif not request.form.get("shares").isdigit() or int(request.form.get("shares")) < 1:
            return apology("Please enter a valid number of shares you desire to purchase - whole numbers only (no fractional shares).")

        # Query cash from users tbl to ensure user has enough cash to purchase desired number of shares
        cash_balance = db.execute("SELECT cash FROM users WHERE id = :id",
                                   id=session["user_id"])

        # Purchase power required is equal to # of shares * price of a share
        purchase_price = int(request.form.get("shares")) * quoted["price"]

        # Cannot just int a list. Require going into cash_balance[0] - first row, from first row, get the value of "cash"
        if int(cash_balance[0]["cash"]) < purchase_price:
            return apology("You do not have sufficient funds to purchase the specified share at desired number of shares.")

        else:
            # Update users table cash balance
            db.execute("UPDATE users SET cash = cash - :purchase_price WHERE id = :id",
                        purchase_price=purchase_price,
                        id=session["user_id"])

            # Added transactions table (self-created) in finance.db
            # Timestamp is auto filled in
            db.execute("""
                INSERT INTO transactions (user_id, symbol, shares, price)
                VALUES (:user_id, :symbol, :shares, :price)
                """,
                user_id=session["user_id"],
                symbol=quoted["symbol"],
                shares=request.form.get("shares"),
                price=quoted["price"]
                )
            # Shows Bought! message bar on top
            flash("Bought!")

            return redirect("/")

    # User selected GET (get form)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        # Store dictionary in a variable called quoted. Inside finance dictionary code (helpers.py) a function is implemented named lookup.
        quoted = lookup(request.form.get("symbol"))
        # Ensure user typed in a valid symbol
        if quoted == None:
            return apology("Please enter a valid ticker symbol.")

        else:
            return render_template("quoted.html", company_name=quoted["name"], ticker_symbol=quoted["symbol"],
                                   price_per_share=quoted["price"])

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check for username input
        if not request.form.get("username"):
            return apology("Please provide username.")

        # Check for password input
        elif not request.form.get("password"):
            return apology("Please provide password.")

        # Check for password confirmation input
        elif not request.form.get("confirmpass"):
            return apology("Please provide confirmation password.")

        # Check if password and confirmation password are the same
        elif request.form.get("password") != request.form.get("confirmpass"):
            return apology("Passwords do not match.")

        # Check if username is already registered.
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # If there is one row (username is unique)
        if len(rows) == 1:
            return apology("Sorry, username is already registered.")

        # If pass all error checking conditions, insert new user to the users table
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                    username=request.form.get("username"),
                    hash=generate_password_hash(request.form.get("password")))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # else, the user reached route via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        # First, store the symbol input dictionary in a variable named 'looked'
        looked = lookup(request.form.get("symbol"))

        rows = db.execute("SELECT symbol, shares FROM transactions WHERE user_id = :user_id",
                          user_id=session["user_id"])

        holdings = []

        proceeds = 0

        for row in rows:
            holdings.append({
                "symbol": rows["symbol"],
                "shares": rows["shares"]
            })

        # Ensure user has the symbol
        if request.form.get("symbol") in holdings["shares"]:
            return apology("You do not own this stock.")

        # Make sure we are in the correct row where we have the same symbol
        elif request.form.get("symbol") in holdings["shares"] and request.form.get("shares") > holdings["shares"]:
            return apology("You do not currently own enough shares to sell desired amount.")

        # If error checking conditions are all passed
        else:
            # Subtract shares in tracker table
            db.execute("UPDATE transactions SET shares = shares - :shares WHERE user_id = :user_id AND symbol = :symbol",
                       shares=request.form.get("shares"),
                       user_id=session["user_id"],
                       symbol=request.form.get("symbol")

            # need to figure out the error
            proceeds = int(request.form.get("shares")) * looked["price"]

            # Update cash in users table
            db.execute("UPDATE users SET cash = cash + :proceeds WHERE id = :id",
                        proceeds=proceeds)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
