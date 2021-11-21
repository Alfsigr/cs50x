from cs50 import SQL
from datetime import datetime
from calendar import month_abbr

db = SQL("sqlite:///gifts.db")

# test date
date = "1990-12-31"

def parse_date(my_date):
    # list of months
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    # find the month, keep as string to concatenate not add
    month_str = my_date[5] + my_date[6]

    # cast to int
    month_int = int(month_str)

    # find in months list
    month = months[month_int - 1]

    # variable for month postfix
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

####
print(parse_date(date))