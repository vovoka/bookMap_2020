### Booklib
Pet project for learning purposes.

initial setup:
* copy the repository
* create virtual environment`venv` with `python3 -m venv venv && source venv/bin/activate`
* create file `.env` file with secrets values (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET) like `export GOOGLE_CLIENT_ID = "102561523463-...r5ohi8ej22307.apps.googleusercontent.com" ...` to enable google OAuth.
* install modules `pip install --upgrade pip && pip install -r requrements.txt`
* initialise db (if you want to use db migrations later) `flask db init && flask db migrate -m "initial tables" && flask db upgrade` or visit `http://127.0.0.1:5000/populate_db` to create all tables and populate them with a sample data. It generates test-users with names like `ddd`, `hhh`, `kkk` with some test-books and book-instances.
* run the app with `flask run`

here is a lot of bugs, I know ;)


###### TODO (unsorted ideas):
* email notifications as html (now txt only)
* email notifications as thread
* email notifications 'You got a new message '
* Docker
* Clasterize book instances by location
* try to switch to GraphQL (what for?)
* Add a service to visit goodreads and parse an info of searched book.
* Find a way to exclude unused modules from requrements.txt (all related to graphql etc.)
* add {% include '_book_instance_2_column.html' %} to add_book_instance?
* Add AdminPanel
* Connect oauth2_tokens with User.tokens to not re-authorize each time with google auth server.
