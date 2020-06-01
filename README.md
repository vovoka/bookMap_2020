### Booklib
Pet project for learning purposes.

initial setup:
* copy the repository
* create `venv` with `python3 -m venv venv && source venv/bin/activate`
* install modules `pip install --upgrade pip && pip install -r requrements.txt`
* initialise db `flask db init && flask db migrate -m "initial tables" && flask db upgrade`
* visit `http://127.0.0.1:5000/populate_db` to populate db with a sample data

generated user name/logins are like 'ddd/ddd', 'hhh/hhh', 'kkk/kkk'
* visit `http://127.0.0.1:5000/unpopulate_db` to clean un the db

here is a lot of bugs, I know ;)
