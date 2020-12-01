import os, types

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
    # Guidance from https://cs50.stackexchange.com/questions/30264/pset7-finance-index

    # Display HTML table summary, for user logged in: which stocks the user owns (ticker symbol), # of sh, CURRENT PRICE of each stock, total value of each stock
    # Also display cash balance and grand total
    # CREATE TABLE 'tracker' ('Username' PRIMARY KEY, 'Symbol' VARCHAR(10), 'Name' VARCHAR(10), 'Price' NUMERIC, 'Shares' INT, 'total' NUMERIC);

    # Query tracker database and put information in a variable called stocks
    stocks = db.execute("SELECT Symbol, Shares FROM tracker WHERE username = :username",
                       session["user_id"])

    # Py loop - iterate over stocks list:
    for stock in stocks:
        symbol = stocks["Symbol"]
        name = lookup(symbol)["name"]
        shares = stocks["Shares"]
        price = lookup(symbol)["price"]
        total = shares * price

    # Query user database for cash available
    cash_avail = db.execute("SELECT cash FROM users WHERE username = :username", username = session["user_id"])
    grand_total = SUM(total) + cash_avail

    return render_template("index.html", stocks=stocks, cash_avail=cash_avail, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (by submitting a form)
    if request.method == "POST":

    # Store the dictionary in variable called quoted
        ticker = lookup(request.form.get("symbol"))
        num_of_shares = request.form.get("shares")
        #** THIS MIGHT BE WRONG current_price = quoted["price"]
        total_cost = shares * current_price

    # Error checking:
    # Require input of a ticker symbol, render an apology if the input is blank or the symbol does not exist (as per the return value of lookup).
        if not request.form.get("symbol") or ticker == None:
            return apology("Please enter a valid ticker symbol", 403)

    # Require a user input a number of shares, implemented as a text field whose name is shares. Render an apology if the input is not a positive integer.
        elif not shares.isdigit() or num_of_shares < 1:
            return apology("Please enter a valid number of share(s)", 403)

    # SELECT how much cash the user currently has in users.
        cash_amount = db.execute("SELECT cash FROM users WHERE username = :username",
                                 session["user_id"])
        # Return apology if user cannot afford the number of shares at the current price
        if cash_amount < total_cost:
            return apology("You have insufficient funds to purchase desired number of shares at current price.")
        else:
            # Subtract amount purchased from user's cash
            db.execute("UPDATE users SET cash = cash - :cost WHERE username = :username", cost = cost, username = session["user_id"])

            # INSERT information into newly created 'tracker' tbl
            # Did not create the table yet => need to run in sqlite3
            # CREATE TABLE 'tracker' ('Username' PRIMARY KEY, 'Symbol' VARCHAR(10), 'Name' VARCHAR(10), 'Price' NUMERIC, 'Shares' NUMERIC, 'total' NUMERIC, 'Transacted' TEXT);
            db.execute("INSERT INTO tracker (Username, Symbol, Name, Shares, Price, Total, Transacted) VALUES (:username, :symbol, :name, :shares, :price, :total, :transacted)",
                        username=session["user_id"], symbol=ticker, name=lookup("name"), shares=num_of_shares, price=current_price, total=total_cost, transacted=CURRENT_TIMESTAMP))

        # Add one or more new tables to finance.db via which to keep track of purchase
        # Keep track of at least: what stock was bought, how many shares of stock bought, who bought that stock
        # CREATE TABLE 'tracker' ('Username' PRIMARY KEY, 'Symbol' VARCHAR(10), 'Name' VARCHAR(10), 'Price' NUMERIC, 'Shares' NUMERIC, 'total' NUMERIC, 'Transacted' TEXT);

        # Redict user back to the portfolio
        return redirect("/")

    # Else: user request method is GET - display form to buy stock
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT Symbol, Shares, Price, Transacted FROM tracker WHERE user = :username ORDER BY Transacted DESC",
                         username=session["user_id"])

    for history in historys:
        symbol = history["Symbol"]
        shares = history["Shares"]
        price = history["Price"]
        transacted = history["Transacted"]

    return render_template("history.html", symbol=symbol, shares=shares, price=price, transacted=transacted)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (by submitting a form)
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

        # Store the dictionary in variable called quoted
        quoted = lookup(request.form.get("symbol"))

        # If symbol is invalid (dictionary returns None), return apology
        if quoted == None:
            return apology("invalid symbol", 403)

        else:
            return render_template("quoted.html", name=quoted["name"], symbol=quoted["symbol"], price=(quoted["price"]))

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username is not empty
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password is not empty
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("retypepassword"):
            return apology("your passwords don't match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # If username exists, return error
        if len(rows) == 1:
            return apology("username already exists", 403)

        # If no errors, insert new user to users table - store hash of the user's password
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                            username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        # ****Start session
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                           username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST (by submitting a form)
    if request.method == "POST":

        # Query tracker table
        tracker = db.execute("SELECT * FROM tracker WHERE username=:username", username=session["user_id"])

        # Set variable for number of shares owned before selling
        shares_owned = db.execute("SELECT Shares FROM tracker where username = :username AND Symbol = :symbol",
                                    username=session["user_id"], symbol=request.form.get("symbol"))

        # ERROR CHECKING:
        # Render apology if user fails to select a stock
        if not request.form.get("symbol"):
            return apology("Please enter valid stock ticker symbol.")

        # Render apology if if the user does not own any of the stock - *** need a loop to check condition if symbol is in tracker??
        if request.form.get("symbol") not in tracker["Name"]:
            return apology("You do not currently own this stock.")

        # Render apology if user input is not a positive integer or if the user does not own that many shares of the stock
        if request.form.get("shares") < 1 or not request.form.get("shares").isdigits():
            return apology("Please enter valid number of shares (must be a positive integer).")

        # Render apology if user does not own enough of that stock
        if request.form.get("shares") > shares_owned:
            return apology("You do not have enough amount of shares of this stock to sell desired amount.")

        # Set variable for sold value
        sold_value = request.form.get("shares") * lookup(symbol)["price"]

        # After passing all error-checking conditions above:
        # Sell the specified number of shares
        db.execute("UPDATE ")

        # Update cash balance in user table
        db.execute("UPDATE users SET cash = cash + sold_value WHERE username = :username",
                    username=session["user_id"])

        # Update number of shares in tracker table
        db.execute("UPDATE tracker SET Shares = shares - request.form.get("shares") WHERE username = :username",
                    username=session["user_id"])

        # Update for history tbl

        # redirect user to home
        return redirect("/")

    # else: user reached route via GET
    # Display form to sell stock (what stock and how many shares)
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
