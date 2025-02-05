import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for, get_flashed_messages, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology
from datetime import datetime, timedelta
from cs50 import SQL
import csv
from io import StringIO
import time

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

db = SQL("sqlite:///doom.db")

@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    if session.get("user_id") is None:
        pass
    else:
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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

@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Check if username is too long
        if len(request.form.get("username")) > 32:
            return apology("username too long")
        # Check if password is too long
        elif len(request.form.get("password")) > 64:
            return apology("password too long")
        # Check if password is too short
        elif len(request.form.get("password")) < 8:
            return apology("password too short")

        # Check if username is provided
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Check if passwords are provided and match
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide identical passwords", 400)

        # check if username is taken, if not store username and password
        try:
            db.execute("INSERT INTO users (username, hash, created) VALUES (?, ?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")), int(time.time()))
        except ValueError:
            return apology("that username already exists", 400)

        # redirect user to login page
        flash("Registration successful")
        return redirect('login')

    # prompt user to register page
    else:
        return render_template("register.html")


@app.route("/homepage", methods=["GET","POST"])
def homepage():
    return render_template("homepage.html")

@app.route("/rules", methods=["GET","POST"])
def rules():
    return render_template("rules.html")

@app.route("/privacy", methods=["GET","POST"])
def privacy():
    return render_template("privacy.html")

@app.route("/account", methods=["GET","POST"])
@login_required
def account():

    userid = session["user_id"]
    gamesplayed = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ?", userid)

    if gamesplayed[0]["count"] < 1:
        return apology("Must play games before account page creation", 403)

    sevendays = 60*60*24*7

    # Data for first part of table
    signup = db.execute("SELECT created FROM users WHERE id = ?", userid)
    signup = signup[0]["created"]
    formatted = datetime.fromtimestamp(signup).strftime("%Y-%m-%d")
    gamescorrect = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ? AND correct = 1", userid)
    if gamesplayed[0]["count"] == 0:
        correctpercent = 0
    else:
        correctpercent = gamescorrect[0]["count"]/gamesplayed[0]["count"]

    averagetime = db.execute("SELECT AVG(timer) AS avg FROM plays WHERE userid = ?", userid)

    # Same but for last 7 days
    sevengamesplayed = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ? AND time > ?", userid, int(time.time()) - sevendays)
    sevengamescorrect = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ? AND time > ? AND correct = 1", userid, int(time.time()) - sevendays)

    if sevengamesplayed[0]["count"] == 0:
        sevencorrectpercent = 0
    else:
        sevencorrectpercent = sevengamescorrect[0]["count"]/sevengamesplayed[0]["count"]

    sevenaveragetime = db.execute("SELECT AVG(timer) AS avg FROM plays WHERE userid = ? AND time > ?", userid, int(time.time()) - sevendays)

    # Month statistics:
    # % correct per month
    # Average time per month (corrects only)
    monthpercent = [0] * 12
    monthtime = [0] * 12
    for i in range(12):
        thismonthcorrect = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ? AND correct = 1 AND month = ?", userid, i + 1)
        thismonthtotal  = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ? AND month = ?", userid, i + 1)
        thismonthtime = db.execute("SELECT AVG(timer) AS avg FROM plays WHERE userid = ? AND month = ? AND correct = 1", userid, i + 1)

        if thismonthtotal[0]["count"] > 0:
            monthpercent[i] = thismonthcorrect[0]["count"]/thismonthtotal[0]["count"]
            if thismonthtime[0]["avg"] is not None:
                monthtime[i] = thismonthtime[0]["avg"]
            else:
                monthtime[i] = 0
        else:
            monthpercent[i] = 0
            monthtime[i] = 0

    # Century statistics
    # 1800,1900,2000,2100 % correct and average time (corrects only)
    century = [1800,1900,2000,2100]
    centurypercent = [0] * 4
    centurytime = [0] * 4

    for k in range(4):
        thiscenturycorrect = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ? AND correct = 1 AND year >= ? AND year < ?", userid, century[k], century[k] + 100)
        thiscenturytotal = db.execute("SELECT COUNT(*) AS count FROM plays WHERE userid = ? AND year >= ? AND year < ?", userid, century[k], century[k] + 100)
        thiscenturytime = db.execute("SELECT AVG(timer) AS avg FROM plays WHERE userid = ? AND correct = 1 AND year >= ? AND year < ?", userid, century[k], century[k] + 100)

        if thiscenturytotal[0]["count"] > 0:
            centurypercent[k] = thiscenturycorrect[0]["count"]/thiscenturytotal[0]["count"]
            if thiscenturytime[0]["avg"] is not None:
                centurytime[k] = thiscenturytime[0]["avg"]
            else:
                centurytime[k] = 0
        else:
            centurypercent[k] = 0
            centurytime[k] = 0

    # Pass a list of month names and century names for ease
    monthnames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    centurynames = ["1800 to 1899", "1900 to 1999", "2000 to 2099", "2100 to 2199"]

    return render_template("account.html", formatted=formatted, gamesplayed=gamesplayed[0]["count"], 
                           correctpercent=correctpercent, averagetime=averagetime[0]["avg"],
                           sevengamesplayed=sevengamesplayed[0]["count"],
                           sevencorrectpercent=sevencorrectpercent, sevenaveragetime=sevenaveragetime[0]["avg"],
                           monthpercent=monthpercent, monthtime=monthtime, centurypercent=centurypercent,
                           centurytime=centurytime, monthnames=monthnames, centurynames=centurynames)

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    currenttime = int(time.time())
    timer = data.get('timer')
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    dayofweek = data.get('dayofweek')
    answer = data.get('answer')

    # Checks values are valid
    try:
        int(timer)
        int(year)
        int(month)
        int(day)
        int(dayofweek)
        int(answer)
    except:
        return jsonify({'status': 'error', 'message': 'Error'}), 400
    
    if int(timer) < 0:
        return jsonify({'status': 'error', 'message': 'Error'}), 400
    if int(timer) > 120000: # Throws away results longer than 2 minutes
        return jsonify({'status': 'error', 'message': 'Inactive timer'}), 400
    
    # Year can't be below 1600 (Gregorian Calendar)
    if int(year) < 1600 or int(year) > 10000:
        return jsonify({'status': 'error', 'message': 'Incorrect year'}), 400
    
    if int(month) < 1 or int(month) > 12:
        return jsonify({'status': 'error', 'message': 'Incorrect month'}), 400

    if int(day) < 1 or int(day) > 31:
        return jsonify({'status': 'error', 'message': 'Incorrect day'}), 400
    
    if int(dayofweek) < 0 or int(dayofweek) > 6:
        return jsonify({'status': 'error', 'message': 'Incorrect day of week'}), 400

    if int(answer) < 0 or int(answer) > 6:
        return jsonify({'status': 'error', 'message': 'Incorrect answer'}), 400
    
    # Record answer, 1 for correct, 0 for false
    if int(answer) == int(dayofweek):
        correct = 1
    else:
        correct = 0

    # Put it all into sqlite database
    try:
        db.execute("INSERT INTO plays (userid, time, timer, year, \
                    month, day, dayofweek, answer, correct) VALUES (?, ?, ?, ?, ?, ?, ?, ? ,?)", session["user_id"], currenttime,
                    timer, year, month, day, dayofweek, answer, correct)
    except:
        return jsonify({'status': 'error', 'message': 'Error'}), 400

    return jsonify({'status': 'success', 'message': 'Successfully saved data'}), 200

@app.route('/download', methods=['POST'])
@login_required
def download():

    # This function (download) has been mostly generated using ChatGPT Model 4o

    userid = session["user_id"]

    data = db.execute("SELECT * FROM plays WHERE userid = ?", userid)

    headers = data[0].keys()

    csvoutput = StringIO()
    csvwrite = csv.writer(csvoutput)

    csvwrite.writerow(headers)
    csvwrite.writerows([row.values() for row in data])

    csvoutput.seek(0)
    file = make_response(csvoutput.getvalue())
    file.headers["Content-Disposition"] = "attachment; filename=data.csv"
    file.headers["Content-type"] = "text/csv"
    return file

@app.route('/changepassword', methods=['POST', 'GET'])
@login_required
def changepassword():

    if request.method == "POST":

        userid = session["user_id"]

        # Check if current password is too long
        if len(request.form.get("current")) > 64:
            return apology("current password is invalid")
        # Check if password is too long
        elif len(request.form.get("password")) > 64:
            return apology("password too long")
        # Check if password is too short
        elif len(request.form.get("password")) < 8:
            return apology("password too short")

        # Check if current password is provided
        if not request.form.get("current"):
            return apology("must provide existing password", 400)

        # Check if passwords are provided and match
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide identical passwords", 400)

        # check if current password hash matches and if so change the password with the provided
        currenthash = db.execute("SELECT hash FROM users WHERE id = ?", userid)
        currenthash = currenthash[0]["hash"]

        currentpassword = request.form.get("current")

        if check_password_hash(currenthash, currentpassword):
            db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(request.form.get("password")), userid)
        else:
            return apology("Existing password not entered correctly", 400)

        # redirect user to account page
        flash("Password change successful")
        return redirect('account')

    # prompt user to password change page
    else:
        return render_template("changepassword.html")
    
@app.route('/deleteaccount', methods=['POST', 'GET'])
@login_required
def deleteaccount():

    if request.method == "POST":

        userid = session["user_id"]

        # Check if current password is too long
        if len(request.form.get("current")) > 64:
            return apology("current password is invalid")
        # Check if confirmation is too long
        elif len(request.form.get("confirmation")) > 64:
            return apology("password too long")

        # Check if current password is provided
        if not request.form.get("current"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)
        elif request.form.get("current") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        # check if current password hash matches
        currenthash = db.execute("SELECT hash FROM users WHERE id = ?", userid)
        currenthash = currenthash[0]["hash"]

        currentpassword = request.form.get("current")

        if check_password_hash(currenthash, currentpassword):
            db.execute("DELETE FROM plays WHERE userid = ?", userid)
            db.execute("DELETE FROM users WHERE id = ?", userid)
        else:
            return apology("Existing password not entered correctly", 400)

        # redirect user to home page
        session.clear()
        flash("Account has been deleted")
        return redirect('/')

    # prompt user to password change page
    else:
        return render_template("deleteaccount.html")