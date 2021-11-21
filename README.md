# GiftTracker

## Video Demo:  https://www.youtube.com/watch?v=nF4mbKgKQr8

## My project and the Birthdays lab
My project at the moment behaves much like an extension to the 'Birthdays' lab (week 9). In fact, I began the cs50 course in 2020, before the Birthdays lab was introduced, and came up with my final project at this time. Life got in the way, full time work etc., and so by the time I restarted the course and finished off my project, the Birthdays lab already existed.

## application.py
This is the file from which the application runs. First, the various outside libraries are imported. These contain functionalities which are essential to the running of the program. 
The internal file 'helpers.py' is also imported; this contains specific functions which will be explained later.
The decorator `function login_required(f)` is also contained within helpers.py. This function is identical to that implemented in finance, requiring that any user whom is not registered (there is no user_id in session) will be redirected back to the login/registration page. Most of the backend functions are also decorated with `login_required`, to prevent unauthorised users doing anything besides registering.
This file contains the functions for `login()`, `logout()` , `register()` and `change_password()`, all of which are self-explanatory and similar to those found in Finance.
If a user has registered and logged in, their individual user id will be stored in the `session` variable, and they will have access to the entire functionality of the app and can edit details, store information etc.
A variable `db` is defined to access the `gifts` database 'gifts.db' using SQL, giving access to the various tables used.

- ### index(): The function of the default route.
  The default route is only ever accessed using the GET method.
  This function accesses the 'friends' table from the 'gifts' database, and selects the data (name and birthday) for this specific user's friends, storing as a list of dicts in the `rows` variable. For each friend (`row in rows`), the `parse_date` function contained within helpers.py (see 'helpers.py' below) changes their birthday data (if present) to a readable format.
  The friends' interests are accessed from the 'interests' table and stored in the `interests_dict` variable (NOTE this is not named quite correctly as it's actually a list of dicts but changing it now would be madness). The friend's interests are stored in a list `interests` , then made into a comma-seperated string `interest_string` to be displayed together on the index page. Numbered values are then generated for each friend/row, to be stored under the values `show_id` and `div_id`. These will be used when rendering index.html so that the interests can be shown/hidden at will (see 'index.html').
  Finally, the 'index.html' template is rendered, and the `rows` variable passed in for use in the front end.

- ### index.html
  This page displays a table containing all the current user's friends, their birthdays, interests, and links to their gift history and the edit/delete option.
  The `rows` variable is accessed using Jinja, and the data is filled in. The 'Gift History' and edit/delete options are handled using separate routes; see the corresponding route's info below for details.
  The friends' interests are initially hidden and can be shown if the user desires. The show/hide button for the interests and the div containing the interests use as ids the `show_id` and `div_id` values passed in from the `rows` variable.
  There is also an option to add new friends to the user's database (see 'add_friend' below).

- ### index.html JavaScript
The JavaScript code goes through each friend, and builds variables for both the button and the div which match the ids they already have. An event listener is added to the button which enables the div to be displayed or hidden. This would be useful if one friend has many interests which could crowd the table if constantly displayed.

- ### add_friend(): Add a new entry to the user's friends.
This route is accessed via the GET method by default, when the user clicks on the 'Add Friend' button in 'index.html'. No variables are passed to the front end. This renders the template 'add-friend.html', within which is a form to input the friend's name, birthday and three initial interests. On submitting from here, the POST method is used, which adds the new friend's details to the 'gifts' database. The function contains error checking for cases in which a name is not provided, or the name exactly matches one of the user's existing friends. The new friend's unique `user_id` (auto-generated), name and birthday (if provided) are inserted into the 'friends' table, and the friend's interests (if provided) into the 'interests' table in the database. A message is flashed to the user at the top of the screen on redirect to confirm successful addition of the new friend entry.

- ### edit(): Edit an individual friend's details or delete.
  This route is only ever called using the POST method, as the edit button is a form from which the intended friend's id is collected via hidden input data on the 'index.html' page, each friend having a separate button on their own row. The friend's details are then selected from the 'gifts' database (SQL) and stored in the `friend` variable, and the birthday data parsed for display using `parse_date`.
  The friend's interests are selected from the database and stored as `interests_dict` (again, actually a list of dicts), then transformed into a list `interests` . A separate version `interest_values`  without any whitespace (e.g. if a single interest has more than one word) is created for use as html values. The interests are transformed into a comma-separated string `interest_string` and added to the `row` variable for this friend (as `friend["interests"]`)
  A variable `dict_int` is created to associate the original interests (with possible whitespace) with the new ones (e.g. 'fly fishing' : 'fly_fishing'), one for the values and one to display to the user.
  Finally the 'edit.html' template is rendered, passing the friend data, a comma-separated string of their current interests, and the `dict_int` variable.

- ### edit.html
  This page displays a table containing the selected friend's details. There are options to update each of these individually, confirming changes at the end. There are also options to cancel (return to homepage), or delete this friend from the database entirely. The 'Confirm Changes' and 'Delete Friend' buttons are contained within forms which call the `/update_friend` and `/delete_friend` routes respectively, with hidden inputs containing data which will be required by the back end.

- ### edit.html JavaScript
The `parse_date` function is used if the user wants to update a friend's birthdate, returning the new birthday data (received in numerical string format) in a readable format to be displayed to the user before confirming changes.
The old interests are collected from the displayed html as one string `oldInterests`, and the `split()` method is used to divide them into substrings which are stored in the array `oldInterestsList`.
String variables (empty) are defined for required data `name` and `birthday`. A list `newInterestsList` is defined to store any added interests, and an html-friendly version `htmlInterestsList` for displaying to the user with the appropriate spaces.
A variable `updated` is also defined to keep track of whether anything has been updated; this is initialised to zero. This could have also been achieved with a boolean value for the same result.
Event listeners are added to the 'Update' buttons in the 'Name' and 'Birthday' columns which collect the appropriate updated data, displaying it on the page and storing in variables (`name`, `birthday`). Error checking is present if the user tries to update a value without entering any new data.
Interests are added in a similar way, with additional error checking that the interest does not already exist on the list, and neither has it been currently added twice. There is also functionality to check whether the new interest is the first new one AND some old interests already exist. In this case a display list is constructed of the new interests and the old ones to display in html, making it clear to the user which interests are new and which were already stored.
To delete interests, the user chooses which old interest to remove from a drop-down menu; the interest is removed from the menu and stored in the `removed` list variable. The displayed html is changed to reflect this.
The `updated` variable is incremented whenever any updates are made.
Finally an event listener is added to the 'Confirm Changes' button (confusingly called the `update-btn` here) which adds all the updated values to the form data hidden values and calls the `/update_friend` route.

- ### update_friend(): Confirm the updates to the friend's details
This route is only ever called using the POST method, as it never needs to render a template, just retrieve and update form data.
The form data is collected from the 'Confirm Changes' button (form) hidden input values.
If there have been no values updated (`updated_number == "0"`, string as it's coming from html in string form), the user is informed that no changes will be made. Otherwise, the values are updated in the SQL database and interests added/deleted.
The route then redirects to the default route, rendering index.html with the updated information displayed.

- ### delete_friend(): Delete selected friend from database
  This route is also only accessed using POST. The friend's id is obtained from the delete button's hidden form input data. The friend's details are then retrieved from the database, and a warning message is constructed using the friend's name to confirm data deletion.
  The 'confirm.html' template is rendered, and the friend id and user warning message passed in.

- ### confirm.html
This page confirms friend deletion using the warning message created in the '/delete_friend()' route. If the user chooses the 'Yes' option, the 'confirm_delete' route is called and the friend id passed through as form data. The 'No' option navigates back to the index page without any changes being made.

- ### confirm_delete(): Actually delete the friend
This route just retrieves the form data from 'confirm.html', the friend id. This friend is then deleted from the 'friends' table in the database, and the default route is called which navigates the user back to the index page.

- ### gift_history(): Show the friend's gift history
  This route is called via the 'Explore/Edit' button on the 'index.html' page. It is only ever called using the POST method, as it always requires form data.
  When called, the specific friend id is extracted from the form. This is used to access the friend's data from the database, and store the friend's name in the `friend_name` variable.
  The dates are transformed to a readable format and the prices converted to GBP.
  This friend's specific gift data; names, dates, comments, price etc. are retrieved and stored in the 'rows' variable. There may be any number of gifts/rows at this point as multiple gifts may have been given to one friend. A new field, 'html_gifts', is created and stored in the rows variable; this removes whitespace for html labelling.
  Lastly, the 'gift_history.html' template is rendered, passing in the friend_id, the `rows` variable and the friend name.

- ### gift_history.html
  This page displays a table containing the selected friend's gifting history. Gift, date, price, comments and delete gift option.

 - ### gift_history.html JavaScript
This function simply returns a modal dialogue to confirm deletion of a specific gift.

- ### add_gift(): Record a new gift for this friend
  This route is called from the 'Add Gift' button in gift_history.html. Like some previous routes, it is only ever called using the POST method. The friend id is obtained from the form, and the friend's name selected from the database.
  The 'add_gift.html' template is rendered, with the friend's id and name passed in.

- ### add_gift.html
  A form is displayed with fields to add the new gift's name, date, price and comments. 

- ### add_gift.html JavaScript
This is essentially error checking; if no new gift name is provided, the info cannot be updated at all. If some optional values are missing, the missing values are stored in an array `missing` which is converted to a readable string `missingItems`; the user is informed and asked to confirm before submission.

- ### confirm_gift(): Add gift record to database
This is the route in which the new gift is added to the SQL database. The values for the specific friend's id, plus the information on the specific gift, are collected from the html form on 'add_gift.html'.  Redirects then back to 'gift_history()'.

- ### delete_gift(): Deletes the selected gift
Only accessed via POST, deletes the selected gift from the SQL database; the user has already confirmed deletion of this gift via the modal dialogue in the script of 'gift_history.html'. Once deleted, the user is informed via flash then returns to the updated 'gift_history.html'.

- ### ideas():
  Only accessed via POST, from the 'gift_history.html' page 'Gift Ideas' button. This route uses a word association API to obtain gift ideas for a specific friend.
  Firstly, this route gets the friend id `friend_id`, and from that the friend row and name `friend_name`.
  The friend's interests are also selected from the database and added to the `interests` list.
  A `while True:` loop is used to pick an interest with associations; a random interest `rand_interest` is initially selected from the `interests` list, and the twinword word association API is used to find associations for `rand_interest`. If the API cannot find any associations for this interest, it is removed from the `interests` list. If the `interests` list is empty, this means all interests have already been tried and an error message is returned to the user.

  Once an interest with associations has been found, one association is picked at random and stored in the `rand_assoc` variable. This is passed in to 'ideas.html' when the template is rendered, along with the interest it came from, the friend's name, and a list of the rest of their interests for use by the script contained within 'ideas.html'.

- ### ideas.html:

  This page displays a dialogue to the user, telling them which of the friend's interests has been used and what gift idea has been suggested by the API. If the user likes this idea and clicks 'Yes', a link is opened to ebay which searches for gifts based on this idea. One possible improvement would be to use e.g. an official ebay API for this task. There are also options for the user to reject this idea and use either a new idea based on the same interest, or to start again using a new interest entirely.

- ### ideas.html Javascript

  A couple of functions are defined. `getAssocs(word)` takes a word (interest) as a parameter, and returns either an array of ideas obtained from the twinword API (limited to 15 associations) or returns 1 if no associations could be found for the passed interest.

  `getValidInterest(interestArray)` takes an array of the friend's interests `interestArray`, selects one at random `interest` and uses the `getAssocs` function to see if associations can be found for the interest. If so, the function returns a list of the associations `assocs`, with `interest` added to the list as well. If associations cannot be found for this interest (`assocs != 1`), the interest is removed from the array and the function recursively calls itself to try again with another interest. If `interestArray` is emptied without finding any associations, the function returns 1.

  

  After the functions are defined, some variable are declared. 

  `interests` is defined as the `interests` list passed in via Jinja from 'application.py', transformed to json format for readability. The `interests` variable is then parsed back into a valid javascript array.

  `interest` and `idea` are the randomly selected interest and idea passed in from 'application.py'.

  An empty array `ideas` is defined to store new ideas if the user opts to change them.

  A boolean variable ` ideaPressed` is declared to determine whether the user has requested to search using a new idea; this is initially set to `false`.

  

  An event listener is added to the 'new-idea' button, which if clicked selects a new idea to use, obtained from the current interest. First, the `getAssocs` function is used to obtain associations (ideas) for the current interest. The `ideaPressed` variable is changed to `true`, meaning that if the button is clicked for a second time the `ideas` list is not refreshed by calling `getAssocs` again. The `index` variable stores the array index of the current idea; this is then removed from the `ideas` array so that the same idea is not repeated. If the `ideas` array is emptied without the user selecting one to search with, the html on the page is changed to inform the user that they have run out of ideas to use.

  Once the current idea has been removed, the variable `newIdea` is defined as a randomly selected idea from the shortened `ideas` array. The global variable `idea` is updated with this new idea. The html displayed to the user is changed to show the new idea, and the html ebay search button is updated with it as well.

  An event listener is also added to the 'new-interest' button, which if clicked selects a whole new interest from the friend's `interests` list, and obtains a new `idea` based on this interest. The current, unwanted `interest` is firstly removed from the `interests` array to avoid repetition. The variable `interestAndIdeas` is created, defined as the return value of `getValidInterest` called on the `interests` list - this value contains the current interest and associated ideas. If `getValidInterest` has returned 1, e.g the interest list has been emptied, either with no associated ideas found or they have all been rejected, the user is informed via `window.confirm` and given the option to reload the interests and start the process again. The page's html buttons are reset if they have been disabled etc. by the user previously emptying the ideas list.

  A variable `newInterest` is defined, the value for this is obtained from `interestAndIdeas` via `shift`. The global variables `interest`, `ideas` and `newIdea` are updated to contain the new values; the `ideas` variable is obtained by `slice`ing the interest off the `interestAndIdeas` variable.

  The html is updated so the new interest and idea are displayed to the user, and the ebay link is updated to search for the new idea obtained from the new interest.

## helpers.py

* #### login_required(f)

  This function and the **error(message)** function are the same as the ones used in the Finance pset; login_required is a decorator function which is used to wrap most of the routes in 'application.py', making sure that unregistered users do not have access to the app. error(message) is used in conjunction with 'error.html' to render an apology message to the user if there is a foreseeable error such as passwords not matching etc.

* #### parse_date(my_date)

  This function takes as a parameter the user's birthdate (day, month, year) in numerical string form, and returns a string containing the birthdate in a readable format for display, e.g. '16th January 1985'. The month is obtained using a hard-coded list in string format, which is accessed at the appropriate point. The correct 'postfix', 'th', 'st' etc. is added to the day, and the year is purely numerical so does not need any special processing.

  Provisions are made at the end of the function for days 1-9 to avoid leading zeros e.g. '01st'.

