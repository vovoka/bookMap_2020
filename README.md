### Booklib
Pet project for learning purposes.

initial setup:
* copy the repository
* create virtual environment`venv` with `python3 -m venv venv && source venv/bin/activate`
* create file `.env` file with secrets values (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET) like `export GOOGLE_CLIENT_ID = "102561523463-...r5ohi8ej22307.apps.googleusercontent.com" ...` to enable google OAuth.
* install modules `pip install --upgrade pip && pip install -r requrements.txt`
* initialise db (if you want to use db migrations later) `flask db init && flask db migrate -m "initial tables" && flask db upgrade` or visit `http://127.0.0.1:5000/populate_db` to create all tables and populate them with a sample data. It generates test-usersHas isbn with some test-books and book-instances.
* run the app with `flask run`

here is a lot of bugs, I know ;)


###### TODO (unsorted ideas):
* 'It's not my book' button --> delete tmp_cover, only then redirect back to 'add_book' or add handler which will clear tmp folder. But how not to delede needed tmp? Think about.
* Docker
* Clasterize book instances by location
* Add a service to visit goodreads / Google API and parse an info of new / searched book.
* Add AdminPanel
* Connect oauth2_tokens with User.tokens to not re-authorize each time with google auth server.
* replace http://127.0.0.1:5000 with DOMAIN_NAME
* If noone or only you have BI then you can manage the related Book. how to? add book.is_editable
* Add 'blame for the book (incorrect/ violent data)'
* Add offer book cover (if no bookcover currently) -> 'Offer better book cover'(?)

* Data caching? For example do not show 'new book' button for urers who not allow_to_create_a_book()
* try to switch to GraphQL (what for?)


# Gmail allows to send 100-150 messages daily.
# If out of the limit -> look at SendGrid или MailChimp.
