### Booklib
Pet project for learning purposes.

to run:
* copy the repository
* create `venv` with `python3 -m venv venv && cd venv/ && source  bin/activate && cd ..`
* install modules `pip install --upgrade pip && pip install flask flask-wtf flask-login flask-migrate folium`
* initialise db `flask db init && flask db migrate -m "initial tables" && flask db upgrade`
* visit `http://127.0.0.1:5000/populate_db` to populate db with a sample data

here is a lot of bugs, I know ;)
