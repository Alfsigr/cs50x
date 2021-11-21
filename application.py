from __future__ import print_function

import sys

#Print to console:
#print('Hello world!', file=sys.stderr)

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from functools import wraps
import requests
import random
import json

from helpers import error, login_required, parse_date, gbp

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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gifts.db")

@app.route("/")
@login_required
def index():

    # get user's friend info
    rows = db.execute("SELECT * FROM friends WHERE user_id = :user_id", user_id=session["user_id"])

    # how many friends (for index)
    fr_len = len(rows)

    # e.g. for each friend of this user
    for row in rows:
        # if the friend has a birthday logged, turn it into a nice readable format and stick in in
        if row["birthday"]:
            row["birthday"] = parse_date(row["birthday"])
        # select the interests of this friend
        interests_dict = db.execute("SELECT interest FROM interests WHERE friend_id = :friend_id", friend_id=row["id"])

        # empty list variable for this friend
        interests = []

        # add in each of their interests
        for i in interests_dict:
            interests.append(i["interest"])
        # transform into comma-separated string
        interest_string = ", ".join(interests)
        # insert in row (in rows) variable for this friend
        row["interests"] = interest_string

        # HERE BE MONSTERS
        #str_f_id = str(row["id"])

        # variables to use as names for (hidden) form input values (hard-coded) to pass friend id to routes
        # values are made available for use from rows variable
        # (named as in the name for explore not as in for explore the name)
        #row["explore_name"] = "explore_" + str_f_id
        #row["edit_name"] = "edit_" + str_f_id

    # and for show/hide button and div ids for javascript
    for i in range(fr_len):

        rows[i]["show_id"] = "show_" + str(i)
        rows[i]["div_id"] = "interestdiv_" + str(i)

    return render_template("index.html", rows=rows);

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # Post method, we are already displaying register.html
    if request.method == "POST":

        # Check username was submitted
        if not request.form.get("username"):
            return error("Please provide a username")

        # Check for provided username in existing users table
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # If there are not no users by that username, ie username is already in use
        if len(rows) != 0:
            return error("That username already exists")

        # Check password was provided
        if not request.form.get("password"):
            return error("Please provide a password")

        # Check password confirmation is provided
        if not request.form.get("confirmation"):
            return error("Please confirm your password")

        # Get the username and password and confirm password strings
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check password confirmation matches
        if confirmation != password:
            return error("Passwords do not match; please re-enter")

        phash = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :phash)", username=username, phash=phash)

        # Redirect user to home page
        flash("Successfully registered! Log in using the link at the top right of the page.")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = request.form.get("username")

        # Ensure username was submitted
        if not name:
            return error("Please provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("Please provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=name)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return error("Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        flash_message = "Welcome Back, " + name + "!"

        # Redirect user to home page
        flash(flash_message)
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

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user's password"""

    if request.method == "POST":

        # Get form info:
        old_pass = request.form.get("old_pass")
        new_pass = request.form.get("new_pass")
        confirm = request.form.get("confirmation")

        # Parameters not provided:
        if not old_pass:
            return error("Please provide your current password")
        if not new_pass:
            return error("Please choose a new password")
        if not confirm:
            return error("Please confirm your new password")

        # Compare to stored hash value for user:
        rows = db.execute("SELECT hash FROM users WHERE id = :id", id=session["user_id"])
        if not check_password_hash(rows[0]["hash"], old_pass):
            return error("Old password is incorrect, please re-enter")

        # Check confirmation matches:
        if confirm != new_pass:
            return error("New password does not match confirmation, please re-enter")

        # Hash new password and update users table:
        new_hash = generate_password_hash(new_pass)
        db.execute("UPDATE users SET hash = :new_hash WHERE id = :id", new_hash=new_hash, id=session["user_id"])

        flash("Password changed!")
        return redirect("/")

    else:
        return render_template("password.html")

@app.route("/add_friend", methods=["GET", "POST"])
@login_required
def add_friend():
    """Add new friend"""

    if request.method == "POST":

        # if friend name not provided:
        if not request.form.get("name"):
            message="Please provide your friend's name"
            return render_template("error.html", message=message, source="add_friend")

        # get name of friend from form
        name = request.form.get("name")

        # if friend name exactly matches one of user's other friend names:
        conflict_friends = db.execute("SELECT name FROM friends WHERE user_id = :user_id AND UPPER(name) = :name", user_id=session["user_id"], name=name.upper())

        # there is another friend of the same name on your list:
        if len(conflict_friends) != 0:
            message="You already have a friend named \"" + name + "\". Please choose another identifier such as \"" + name + " (work)\""
            return render_template("error.html", message=message, source="add_friend")

        # get friend's birthday if it exists
        birthday = request.form.get("birthday")

        # insert friend into friend table *GENERATES ID FOR INTERESTS TABLE*
        db.execute("INSERT INTO friends (user_id, name, birthday) VALUES (:user_id, :name, :birthday)", user_id=session["user_id"], name=name, birthday=birthday)

        friend_id = db.execute("SELECT id FROM friends WHERE user_id = :user_id AND name = :name", user_id=session["user_id"], name = name)[0]["id"]

        # get all 3 of friend's interests from form
        for i in range(3):
            interest = request.form.get("interest" + str(i + 1))
            if interest:
                db.execute("INSERT INTO interests (friend_id, interest) VALUES (:friend_id, :interest)", friend_id=friend_id, interest=interest)

        flash("Friend successfully added!")
        return redirect("/")

    else:
        return render_template("add_friend.html")

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():

    if request.method == "POST":
        # get the specific friend's id from the form (index.html)
        friend_id = request.form.get("edit")

        # get the friend's info from sql
        friend = db.execute("SELECT * FROM friends WHERE id = :id", id=friend_id)
        # there should be only one friend per request
        friend = friend[0]
        #parse birthday if it exists
        if friend["birthday"]:
            friend["birthday"] = parse_date(friend["birthday"])

        interests_dict = db.execute("SELECT interest FROM interests WHERE friend_id = :friend_id", friend_id=friend["id"])

        # empty list variable for this friend
        interests = []

        interest_values = []


        # add in each of their interests
        for i in interests_dict:
            interests.append(i["interest"])
            # making a version with no whitespace for the html values (they hate it)
            interest_values.append((i["interest"]).replace(" ", "_"))
        # transform into comma-separated string
        interest_string = ", ".join(interests)
        # insert in row (in rows) variable for this friend
        friend["interests"] = interest_string

        ## make dict HERE so it's UPDATED and the VALUES will not be CHOPEPD off
        dict_int = {

        }

        for i in range(len(interests)):
        # so also the same length as interest_values
            # just sort of using a dict as 2 associated lists here to link the (possibly) space-seperated interest name
            # with the underscore one for html values
            dict_int[interests[i]] = interest_values[i]

        return render_template("edit.html", friend = friend, interests = interests, dict_int = dict_int)
    else:
        return

@app.route("/update_friend", methods=["GET", "POST"])
@login_required
def update_friend():
    # 'post' method to receive form data
    if request.method == "POST":
        friend_id = request.form.get("friend-id")
        name = request.form.get("name")
        birthday = request.form.get("birthday")
        removed = request.form.get("removed-interests")
        added = request.form.get("added-interests")
        updated_number = request.form.get("updated-number")

        # if there have been no updates
        if updated_number == "0":
            message = "You have not updated any information. Nothing will fundamentally change."
            return render_template("error.html", message=message, source="update_friend")
        else:

            # if friend name was changed, change in database
            if (name):
                db.execute("UPDATE friends SET name = :name WHERE id = :id", name=name, id=friend_id)
            # same with birthday
            if (birthday):
                db.execute("UPDATE friends SET birthday = :birthday WHERE id = :id", birthday=birthday, id=friend_id)
            # removed interests
            if (removed):
                # split string into handy list
                remove_us = removed.split(",")
                for thing in remove_us:
                    db.execute("DELETE FROM interests WHERE friend_id = :friend_id AND UPPER(interest) = :interest", friend_id=friend_id, interest=thing.upper())
            # and added interests
            if (added):
                add_us = added.split(",")
                for thing in add_us:
                    db.execute("INSERT INTO interests (friend_id, interest) VALUES (:friend_id, :interest)", friend_id=friend_id, interest=thing)

            return redirect("/")
    else:
        return redirect("/")

@app.route("/delete_friend", methods=["GET", "POST"])
@login_required
def delete_friend():
    if request.method == "POST":
        friend_id = request.form.get("delete-btn")
        friend = db.execute("SELECT * FROM friends WHERE id = :id", id=friend_id)
        name = friend[0]['name']
        message = "Are you sure you want to permanently delete " + name + " and their gift history?"

        return render_template("confirm.html", friend_id=friend_id, message=message)
    else:
        return redirect("/")

@app.route("/confirm_delete", methods=["GET", "POST"])
@login_required
def confirm_delete():
    if request.method =="POST":
        friend_id = request.form.get("confirm-btn")

        db.execute("DELETE FROM friends WHERE id = :id", id=friend_id)
        db.execute("DELETE FROM interests WHERE friend_id = :friend_id", friend_id=friend_id)

        return redirect("/")
    else:
        return redirect("/")

@app.route("/gift_history", methods=["GET", "POST"])
@login_required
def gift_history():
    if request.method == "POST":
        friend_id = request.form.get("gift-history")
        friend_row = db.execute("SELECT name FROM friends WHERE id = :id", id=friend_id)
        friend_name = friend_row[0]["name"]

        rows = db.execute("SELECT * FROM gifts WHERE friend_id = :friend_id", friend_id=friend_id)

        # space-free gift name for form values
        html_gifts = [];

        #for i in interests_dict:
        #    interests.append(i["interest"])
        #    # making a version with no whitespace for the html values (they hate it)
        #    interest_values.append((i["interest"]).replace(" ", "_"))

        for row in rows:
            if (row["date"]):
                row["date"] = parse_date(row["date"])
            if (row["price"]):
                row["price"] = gbp(row["price"])
            row["htmlGift"] = (row["gift"]).replace(" ", "_")

        #####
        print(html_gifts)

        return render_template("gift_history.html", friend_id=friend_id, rows=rows, name=friend_name)

    else:
        return redirect("/")

@app.route("/add_gift", methods=["GET", "POST"])
@login_required
def add_gift():
    if request.method == "POST":
        friend_id = request.form.get("friend-id")
        name_row = db.execute("SELECT name FROM friends WHERE id = :friend_id", friend_id=friend_id)
        name = name_row[0]["name"]

        return render_template("add_gift.html", friend_id=friend_id, name=name)

    else:

        return redirect("/")

@app.route("/confirm_gift", methods=["GET", "POST"])
@login_required
def confirm_gift():
    if request.method == "POST":
        friend_id = request.form.get("friend-id")
        gift = request.form.get("gift")
        date = request.form.get("date")
        price = request.form.get("price")
        comments = request.form.get("comments")

        friend_row = db.execute("SELECT name FROM friends WHERE id = :friend_id", friend_id=friend_id)
        name = friend_row[0]["name"]

        db.execute("INSERT INTO gifts (friend_id, gift, date, price, comments) VALUES (:friend_id, :gift, :date, :price, :comments)", friend_id=friend_id, gift=gift, date=date, price=price, comments=comments)

        flash("Gift successfully added!")

        return redirect("/gift_history")

    else:
        return redirect("/gift_history")

@app.route("/delete_gift", methods=["GET", "POST"])
@login_required
def delete_gift():
    if request.method == "POST":
        gift_id = request.form.get("gift-id")
        db.execute("DELETE FROM gifts WHERE id = :gift_id", gift_id=gift_id)

        flash("Gift successfully deleted!")

        return redirect("/gift_history")

    else:
        return redirect("/gift_history")

@app.route("/ideas", methods=["GET", "POST"])
@login_required
def ideas():
    if request.method == "POST":

        friend_id=request.form.get("friend-id")
        friend_row = db.execute("SELECT name FROM friends WHERE id = :friend_id", friend_id=friend_id)

        # get friend's name for displaying on page
        friend_name = friend_row[0]["name"]

        # get row of friend's interests (list of dicts all with key "interest")
        interest_row = db.execute("SELECT interest FROM interests WHERE friend_id = :friend_id", friend_id=friend_id)

        # make list and append this friend's interests
        interests = []
        for i in range(len(interest_row)):
            interests.append(interest_row[i]["interest"])

        while True:

            ## random interest for initial render
            rand_interest = random.choice(interests)

            #####
            print(rand_interest)

            ## where i get my word associations from
            url = "https://twinword-word-associations-v1.p.rapidapi.com/associations/"

            ## querying the random interest from earlier to get a list of associated ideas
            querystring = {"entry":rand_interest}

            ## api key, host etc
            headers = {
                'x-rapidapi-key': "04c1a8be93msh30596fd533a7913p148671jsn7bebee3f1eed",
                'x-rapidapi-host': "twinword-word-associations-v1.p.rapidapi.com"
                }

            ## response
            response = requests.request("GET", url, headers=headers, params=querystring)

            # convert into dict with json
            assoc_dict = json.loads(response.text)

            # if the interest has associations, proceed
            if "associations_array" in assoc_dict:
                break
            # if not, remove it from the list and try again with another one
            else:
                interests.remove(rand_interest)
            # once interests list is empty, exit
            if not interests:
                return error(friend_name + " has no interests which have associations. Try another friend or add more interests.")
        # find the interest's associations
        assoc_array = assoc_dict["associations_array"]

        rand_assoc = random.choice(assoc_array[:15])



        #####
        print(assoc_dict)
        print(rand_assoc)
        test_var = "test"
        print(interests)

        return render_template("ideas.html", testVar=test_var, friend_name=friend_name, interests=interests, rand_interest=rand_interest, rand_idea=rand_assoc)

    else:

        return render_template("ideas.html")
