
from flask import render_template, flash, redirect, url_for
from app import app
from app import db
from app  import db_handlers
from app.forms import RegistrationForm, LoginForm, EditProfileForm, AddBookForm, BookInstanceForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Book, BookInstance, make_db_data, clear_db_data
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime
import folium

@app.route('/')
@app.route('/index')
def index():
    books = Book.query.all()
    book_instances = db_handlers.get_all_book_instances()
    return render_template('index.html', title='Home', books=books, book_instances=book_instances)


import json
import requests
@app.route('/location')
def location():
    """ Show all users on a map (for dev reseaches only) """
    start_coords = (50.4547, 30.524)
    folium_map = folium.Map(location=start_coords, zoom_start=12)
    m = folium_map
    
    # url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    # vis1 = json.loads(requests.get(f'{url}/vis3.json').text)
    # folium.Marker(
    #     location=[50.4547, 30.520],
    #     popup=folium.Popup(max_width=450).add_child(
    #     folium.Vega(vis1, width=450, height=250)),
    #     icon=folium.Icon(icon='cloud')
    # ).add_to(m)
    
    users = User.query.all()
    for user in users:
        print(f'{user.username}  location=[{user.longitude}, {user.latitude}]', flush=True)
        folium.Marker(
            location=[user.latitude, user.longitude],
            popup=user.username,
            icon=folium.Icon(color='green')
        ).add_to(m)

    # folium.Marker(
    #     location=[50.4547, 30.524],
    #     popup='Timberline Lodge',
    #     icon=folium.Icon(color='green')
    # ).add_to(m)
    
    # m.save('./maps/map.html')
    # return render_template('testmap.html', title='Home')
    
    return folium_map._repr_html_()


@app.route('/location/<book_id>')
def book_location(book_id):
    """ Show all the book locations """
    # TODO get all markers with one query
    # TODO replace start_coords with user preferences location

    start_coords = (50.4547, 30.524)
    folium_map = folium.Map(location=start_coords, zoom_start=12)
    m = folium_map
    
    # ? DEBUG code:
    # number of users who have such a book
    users = (db.session.query(User, Book, BookInstance)
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.details == Book.id)
        .count()
    )
    print(f'found book?? instances: {users}', flush=True)
    
    # get all books by id
    book = Book.query.get(book_id)
    print(f'found book: {book}', flush=True)
    
    # get all instances of the Book:
    for bi in book.BookInstance:
        print(f'bi = {bi.id}', flush=True)
        user = (User.query
                .filter(User.id == bi.owner_id)
                .first_or_404())
        
        # ? DEBUG print 
        # if user:
        #     print(f'user found #{user.id} name {user.username}', flush=True)
        #     print(f'user.latitude: {user.latitude} \nuser.longitude {user.longitude}', flush=True)
        # else:
        #     print(f'user NOT found ', flush=True)
        
        folium.Marker(
            location=[user.latitude, user.longitude],
            popup='"' + book.title + '"</br>from <b>' + user.username + '</b></br>' + str(bi.price) + ' uah',
            icon=folium.Icon(color='green')
        ).add_to(m)
    return folium_map._repr_html_()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/populate_db')
def populate_db():
    make_db_data(db)
    flash('Congratulations, db is populated')
    return redirect(url_for('index'))


@app.route('/unpopulate_db')
def unpopulate_db():
    clear_db_data(db)
    flash('Congratulations, db is empty now')
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    book_instances = db_handlers.get_book_instances_by_user_id(user.id)
    # TODO not added to html template. Delete?
    books = db_handlers.get_books_by_user_id(user.id)
    return render_template(
        'user.html',
        user=user,
        book_instances=book_instances,
        total_instances=len(book_instances)
    )

@app.route('/b/<book_id>')
@login_required
def book(book_id):
    """ Shows book detailed info """

    book = Book.query.filter_by(id=book_id).first_or_404()
    return render_template(
        'book_page.html',
        book=book
    )

@app.route('/bi/<book_instance_id>')
@login_required
def book_instance(book_instance_id):
    book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    editable = (book_instance.owner_id == current_user.id)
    return render_template(
        'book_instance_page.html',
        book_instance=book_instance,
        editable=editable
    )

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        title = form.title.data
        author = form.author.data
        if not db_handlers.book_exist(title, author):
            db_handlers.create_book(title, author)
        book_id = db_handlers.get_book_id(title, author)
        return redirect(url_for('book', book_id=book_id))
    return render_template('add_book.html', title='add_book', form=form)


@app.route('/add_book_instance', methods=['GET', 'POST'])
@login_required
def add_book_instance():
    form = BookInstanceForm()
    if form.validate_on_submit():
        title=form.title.data
        author=form.author.data
        price=form.price.data
        condition=form.condition.data
        description=form.description.data
        owner_id=current_user.id
        book_id = db_handlers.get_book_id(title, author)

        if not book_id:
            # create Book
            book = Book(title=title, author=author)
            db.session.add(book)
            db.session.commit()
        book_id = db_handlers.get_book_id(title, author)
        book_instance=BookInstance(
            details=book_id,
            owner_id=current_user.id,
            price=price,
            condition=condition,
            description=description
        )
        db.session.add(book_instance)
        db.session.commit()
        return redirect(url_for('book_instance', book_instance_id=book_instance.id))
    return render_template('add_book_instance.html', title='add_book_instance', form=form)


@app.route('/edit_book_instance/<book_instance_id>', methods=['GET', 'POST'])
@login_required
def edit_book_instance(book_instance_id):
    """ Delete current BookInstance row and create new one.

    If "title" or "author" is changed then look for the Book or create it.
    It seems not optimal to overwrite whole row. I didn't success with updating
    book_instance.details. So, decide to overwrite whole row."""
    # TODO: check book_instance_id, current_user.username that is a real book owner
    form = BookInstanceForm()
    # form prefill
    book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    print(f'book_instance_description  = {book_instance.details}', flush=True)
    
    form.title.data = book_instance.title
    form.author.data = book_instance.author
    form.price.data = book_instance.price
    form.condition.data = book_instance.condition
    form.description.data = book_instance.description

    if form.validate_on_submit():
        result = request.form
        title = result.get('title')
        author = result.get('author')
        price=result.get('price')
        condition=result.get('condition')
        description=result.get('description')
        book_id = db_handlers.get_book_id(title, author)
        if not book_id:
            # create Book
            book = Book(title=title, author=author)
            db.session.add(book)
            db.session.commit()
        book_id = db_handlers.get_book_id(title, author)

        book_instance_new=BookInstance(
            details=book_id,
            owner_id=current_user.id,
            price=price,
            condition=condition,
            description=description
        )
        db.session.add(book_instance_new)
        BookInstance.query.filter_by(id=book_instance_id).delete()
        db.session.commit()
        return redirect(url_for('book_instance', book_instance_id=book_instance_new.id))
    return render_template('edit_book_instance.html', title='edit_book_instance', form=form)


@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', title='User list', users=users)
