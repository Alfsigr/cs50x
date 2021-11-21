from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from cs50 import SQL

db = SQL("sqlite:///gifts.db")

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def error(message):
    def escape(s):

        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    print (message)
    return render_template("error.html", message=message)

def parse_date(my_date):
    # list of months
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    # find the month, keep as string to concatenate not add
    month_str = my_date[5] + my_date[6]

    # cast to int
    month_int = int(month_str)

    # above could have been done in one step possibly/probably

    # find in months list
    month = months[month_int - 1]

    # variable for day postfix
    postfix = ""

    # get int for day
    day_str = my_date[8] + my_date[9]
    day = int(day_str)

    # set postfix according to day
    if day in [1, 21, 31]:
        postfix = "st"
    elif day in [2, 22]:
        postfix = "nd"
    elif day in [3,23]:
        postfix = "rd"
    else:
        postfix = "th"

    # get year variable from date string
    year = my_date[:4]

    # using the int day to cut off leading 0's, recasting to string so it concatenates
    birth_string = str(day) + postfix + " " + month + " " + year

    return birth_string

def gbp(value):
    """Format value as gbp."""
    return f"£{value}"
