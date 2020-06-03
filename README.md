### Booklib
Pet project for learning purposes.

initial setup:
* copy the repository
* create `venv` with `python3 -m venv venv && source venv/bin/activate`
* install modules `pip install --upgrade pip && pip install -r requrements.txt`
* initialise db `flask db init && flask db migrate -m "initial tables" && flask db upgrade`. This step might be skipped. However some errors might be generated during next step then.
* visit `http://127.0.0.1:5000/populate_db` to populate db with a sample data
It generated user name/logins are like `ddd/ddd`, `hhh/hhh`, `kkk/kkk`
* optional, for DEV purposes: export `FLASK_DEBUG=1`
* run the app with `flask run`
* visit `http://127.0.0.1:5000/unpopulate_db` to clean un the db

here is a lot of bugs, I know ;)


###### TODO (unsorted):
* Add routines (Celery/rabbitMQ?) for automatic book instances deactivation by expiration datetime.
* Google auth
* email notifications
* image resizer / cropper(?)
* Docker
* try to switch to GraphQL
* Add a service to visit goodreads and parse an info of searched book.