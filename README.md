# BookMap

Pet project for learning purposes.  
  
__General idea__ - create a marketplace for P2P selling books optimized by users location. It's much easier to buy used book if it's owner lives nearby.  

Main view:  
![GitHub Logo](screenshots/1.png)  
Book Page:  
![GitHub Logo](screenshots/2.png)  
Add a book instance (book is found by isbn at google books) :
![GitHub Logo](screenshots/3.png)  

## Tech stack
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Postgresql](https://www.postgresql.org/)
* [Bootstrap3](https://getbootstrap.com/docs/3.3/)
* [Folium](https://python-visualization.github.io/folium/)
* [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/)
* [dotenv](https://pypi.org/project/python-dotenv/)

## Install
1) create and activate virtual environment `venv`
2) `pip install -r requirements.txt`
3) `flask run`  
  
To play with sample data - visit `http://127.0.0.1:5000/populate_db`. It populate db with the data.  
To clear db - visit `http://127.0.0.1:5000/unpopulate_db`  
To be able to register/login (via OAuth2) you have to create `.env` 

`.env` example:
```
export GOOGLE_CLIENT_ID = "1444443463-4730kg6jtq5umgt8vlwf5ohi8ej22307.apps.googleusercontent.com"  
export GOOGLE_CLIENT_SECRET = "s7WSqwgvE__hwtuvHq7JkqECqwf"  
export MAIL_SERVER=smtp.gmail.com  
export MAIL_PORT=465  
export MAIL_USERNAME=email@gmail.com  
export MAIL_PASSWORD=email_password  
```
Note that Google's SMTP server requires the configuration of "less secure apps". See https://support.google.com/accounts/answer/6010255?hl=en
  
The main objects are `Book` (object with `Title`, `Author`, `isbn` etc.) and derived object `BookInstance` (i.e. instance of a `Book`, have it's own `price`, `condition`, owner location). For example `Book` 'Tom Sawyer' might have some `BookInstance` from different `Users`, with different `price`, `condition` and location.  
  
When user wants to add new `Book` scrypt firstly checks by isbn if  such a `Book` already in local DB, secondly check if Google Books 
(by [google books API](https://developers.google.com/books/docs/v1/using))
 has an informatinon about the book with the `isbn`. If Google books has the information that the info (`isbn`, `title`, `authors`, `cover`) offered to the `User` for use. Otherwise `User` is able to add a `Book` in fully manual mode. When `Book` created in DB `User` is able to add `BookInstance` of it.  
  
`.env` also contains mail settings vars. It's used to send email notification to Users. Currently a notification sent in two cases:
* User got a private message from other User; 
* Users BookInstance reach 'expired' state (30 days from publishing) and have to be re-activated manually by User.  
Checking expired BookInstance made as cron task with `BackgroundScheduler()`
  
  
Map view is centered by User location which is received by IP from `ipapi` service.
Users with Adiministrator privileges able to manage the DB with Flask-Admin interface.


### TODO (unsorted ideas possible next steps and known bugs):
* Less mess! :)
* Add change name during initializating new account only.
* Clasterize book instances by [location](https://geoalchemy-2.readthedocs.io/) ?
* Connect oauth2_tokens with User.tokens to not re-authorize each time with google auth server.
* If noone or only you (as user) is `book_instance` owner then you can manage the related Book (title, cover etc.). How to? -> add `book.is_editable`
* Add job to  clear tmp folder (if many files found there).
* Add 'blame for the book (incorrect/ violent data)'
* Add 'offer book cover' (if no bookcover currently) -> 'Offer better book cover'(?)
* Data caching? For example hide 'new book' button for users who not `allow_to_create_a_book()` Store var 'show_add_new_book' in session?
* Try to switch to GraphQL _(what for? models are not heavy... yet)_?
* Gmail allows to send 100-150 messages daily. If out of the limit -> look at SendGrid или MailChimp.
* Add footer


### Note
First created User (User.id == 1) has Admin access (i.e. has access to http://127.0.0.1:5000/admin/). Fix it with bash-psql script for safety reasons?
