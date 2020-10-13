# BookMap

Pet project for learning purposes.  
  
__General idea__ - create P2P book marketplace focused on users location (to make easy to get).  


[Demo](https://bookmap-2020.herokuapp.com/) refresh if 'internal server error', free Heroku plan is not reliable for the load.
Main view:  
![GitHub Logo](screenshots/1.png)  
Book Page:  
![GitHub Logo](screenshots/2.png)  
Add a book instance (book is found by isbn at google books) :  
![GitHub Logo](screenshots/3.png)  

## Tech stack
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Postgresql](https://www.postgresql.org/)
* [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/)
* [Bootstrap3](https://getbootstrap.com/docs/3.3/)
* [Folium](https://python-visualization.github.io/folium/)
* [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/)
* [dotenv](https://pypi.org/project/python-dotenv/)


## Development
* Rename *.env.dev-sample* to *.env.dev*.
* Rename *Docker.dev* to *Docker*.
* Update the environment variables in the *docker-compose.yml* and *.env.dev* files.
*  
    ```sh
    docker-compose up -d --build  # Build the images and run the containers
    docker-compose exec web python manage.py create_db # Create new empty database
    docker-compose exec web python manage.py seed_db # Fill db with fake users, books, book instances
    ```

hint: if you want to have Admin access quick then login  with your google account (via browser) 
before `seed_db`. This way your User has id=1 and Admin access.

## Production (not fully tested)

Uses gunicorn + nginx.

* Rename *.env.prod-sample* to *.env.prod* and *.env.prod.db-sample* to *.env.prod.db*. 
* Update the environment variables.
* Build the images and run the containers:

    ```sh
    $ docker-compose -f docker-compose.prod.yml up -d --build
    $ docker-compose -f docker-compose.prod.yml exec web python manage.py create_db
    $ docker-compose -f docker-compose.prod.yml exec web python manage.py seed_db
    ```

    Test it out at [http://localhost:1337](http://localhost:1337). No mounted folders. To apply changes, the image must be re-built.



## Notes
* Main objects are `Book` (has `title`, `author`, `isbn` etc.) and derived object `BookInstance` (i.e. instance of a `Book`, it has it's own `price`, `condition`, owner location). For example `Book` 'Tom Sawyer' might has some `BookInstance` offered from different `Users`, with different `price`, `condition` and location.  
* When a user wants to add new `Book` the script:  
    * checks by isbn if such `Book` is already exist in local DB,
    * check (by [google books API](https://developers.google.com/books/docs/v1/using)) if Google Books has an informatinon about the book with the `isbn`. If Google books has the information that the info (`isbn`, `title`, `authors`, `cover`) offered to the `User` for use. 
    * Otherwise `User` is welcomed to add a `Book` in fully manual mode. When `Book` is created in DB, `User` can to add `BookInstance`.  
* `.env` also contains mail settings vars. It's used to send email-notifications to Users. Currently a notification sent in two cases:
    * User got a private message from other User; 
    * Users BookInstance reach 'expired' state (30 days from publishing by deafault) and have to be re-activated manually by User.  
* Google's SMTP server requires the configuration of "less secure apps". See https://support.google.com/accounts/answer/6010255?hl=en
* BookInstance expiration check is made as cron task with  `BackgroundScheduler()`  
* Map view is centered by User location which is received by IP from `ipapi` service.  
* Users with Adiministrator privileges able to manage the DB data with Flask-Admin interface.  
* First created User (User.id == 1) has Admin access (i.e. has access to http://127.0.0.1:5000/admin/). It's for dev conviniency only. Fix it with modified 'create_db' by adding new admin?  

  
### TODO (unsorted ideas possible next steps and known bugs):
* Refactor to made the code more concise :)
* Add change user_name during initializating new account only?
* Clasterize book instances by location with [h3](https://h3geo.org/)?
* If noone or only you (as `User`) is a `BookInstance` owner then you can manage the related `Book` attributes (title, cover etc.). How to? -> add `book.is_editable`
* Add cron job to  clear tmp folder (if many files found there).
* Add _'blame for the book (incorrect/ violent data)'_
* Add _'offer book cover'_ (if no bookcover currently) -> _'Offer better book cover'_(?)
* Data caching? 
    * Do not render _map.html for each User, render it with Scheduller in thread only if Book were added/removed ... or by time. 
    * Hide 'new book' button for users who are not `allow_to_create_a_book()` any more (Limits included already). Store var 'show_add_new_book' in session?
* Gmail allows to send 100-150 messages daily. If out of the limit -> look at SendGrid или MailChimp.
* Add footer
* Messages view as threads (it's about indentation in html)
* Separate css from html (now some mess is there).
* Rename `BookInstance.Description` to `BookInstance.Comment`. It's better name for it.
* Cover with tests.

