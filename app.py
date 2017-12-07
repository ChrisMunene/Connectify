from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import spotipy
import spotipy.util as util
import operator

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("postgres://wdlklxifcvahpo:0ee892364c6603d8db41cab721ea59d8c631b7fe8dd40398dde9fa3bca792721@ec2-54-235-123-153.compute-1.amazonaws.com:5432/dbnl1nukk7qkqt")


@app.route("/spotifylogin", methods=["GET", "POST"])
@login_required
def spotify():
    # username = request.form.get("username")
    if request.method == "POST":
    # Redirect user to Spotify Authorization Page
            auth_url = util.redirect_user()
            return redirect(auth_url)
    else:
        # Store url and get token from it
        response = request.url
        token = util.get_token(response=response)
        if token:
            sp = spotipy.Spotify(auth=token)
            # Get user's 50 most recently played tracks as a JSON object
            results = sp.current_user_recently_played(limit=50)
            # Iterate through JSON object to get track name and artist and store in connectify database
            for item in results['items']:
                track = item['track']
                result = db.execute("INSERT INTO songs (name, artist, userid) VALUES (:name, :artist, :id)",
                                    name=track['name'], artist=track['artists'][0]['name'], id=session["user_id"])
                print (track['name'] + ' - ' + track['artists'][0]['name'])
        else:
            return apology("Can't connect to Spotify", 405)

    return redirect("/home")


@app.route("/")
@login_required
def index():
    """Show intermediary homepage"""
    return render_template("index.html")


@app.route("/home", methods=["GET"])
@login_required
def home():
    """Show homepage
       Contains table with list of 50 most recently played tracks for current user
       and a list of users with whom the current user is matched.
    """
    # Get current user's username
    user = db.execute("SELECT username FROM users WHERE userid = :id", id=session["user_id"])
    # delete any duplicates in the table
    rows = db.execute("DELETE FROM songs WHERE userid = :id AND rowid NOT IN (SELECT min(rowid) FROM songs WHERE userid = :id GROUP BY name, artist)", id=session["user_id"])
    # get tracks from database without duplicates
    rows = db.execute("SELECT DISTINCT name, artist FROM songs WHERE userid = :id ORDER BY songid DESC LIMIT 50", id=session["user_id"])

    return render_template("home.html", rows=rows, user=user[0])

@app.route("/match", methods=["GET", "POST"])
def match():
    """Match the current user with users in the database who have the same songs
       in their 50 most recently played tracks list.
    """
    if request.method == "POST":
        # sets to store songs from current users and from other users
        c_set = set()
        o_set = set()
        # dict to store matched users and their % matches
        matched = dict()
        # variable to store True or False for Matches
        match_success = False
        # count how many users are there
        select = db.execute("SELECT COUNT(username) FROM users")
        print(f"Select is {select}")
        count = int(select[0]['COUNT(username)'])
        print(f"Count is {count}")
        # get list of current users recently played tracks
        current = db.execute("SELECT DISTINCT name, artist FROM songs WHERE userid = :id ORDER BY songid DESC LIMIT 50", id=session["user_id"])
        # create a list of song names and artists for current user as strings
        for x in current:
            c_string = ""
            c_string += str(x['name'] + " by " + x['artist'])
            c_set.add(c_string)
        # iterate through each other user
        for i in range(count):
            if i != session["user_id"]:
                # Get username of user being matched
                user = db.execute("SELECT username FROM users WHERE userid = :id", id=i)
                # get list of other users recently played tracks
                rows = db.execute("SELECT DISTINCT name, artist FROM songs WHERE userid = :id ORDER BY songid DESC LIMIT 50", id=i)
                # create a list of song names and artists for other user as strings
                for x in rows:
                    o_string = ""
                    o_string += str(x['name'] + " by " + x['artist'])
                    o_set.add(o_string)
                # get % match based on similar songs
                value = round(((len(c_set.intersection(o_set)))/len(c_set)) * 100, 2)
                # add match to matched dictionary if match is not 0
                if value > 0:
                    match_success = True
                    matched.update({str(user[0]['username']): value})
        sorted_matches = sorted(matched.items(), key=operator.itemgetter(1), reverse=True)
        return render_template("matched.html", matches=sorted_matches, Bool=match_success)
    else:
        return render_template("match.html")



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
        rows = db.execute("SELECT username, hash, userid FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username", 405)
        # elif not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #     return apology("invalid password", 405)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userid"]

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
    """Register user"""
    if request.method == "POST":
        # Check that fields are not left blank
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("cpassword") or not request.form.get("email"):
            return apology("Missing username/email and/or password!", 400)
        # Check that passwords match
        if request.form.get("password") != request.form.get("cpassword"):
            return apology("Passwords Don't Match!", 400)
        # Hash the password to secure it
        hpassword = generate_password_hash(request.form.get("password"))
        # Store username and password in the database
        result = db.execute("INSERT INTO users (username, hash, email) VALUES (:username, :hash, :email)",
                            username=request.form.get("username"), hash=hpassword, email=request.form.get("email"))
        # Check that username does not already exist
        if not result:
            return apology("Sorry! Username already exists!", 400)
        # login the registered user
        session["user_id"] = result
        # Take the user to the index page
        return redirect("/")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)