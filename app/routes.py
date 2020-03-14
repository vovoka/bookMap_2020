
from flask import render_template, flash, redirect, url_for, request
from app import app
from app import db
from app  import db_handlers
from app.forms import RegistrationForm, LoginForm, EditProfileForm, AddBookForm, BookInstanceForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Book, BookInstance, make_db_data, clear_db_data
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
import folium
import os

@app.route('/')
@app.route('/index')
def index():
    books = Book.query.all()
    book_instances = db_handlers.get_all_book_instances()
    return render_template('index.html', title='Home', books=books, book_instances=book_instances)


@app.route('/location')
def test_index():
    start_coords = (50.4547, 30.524)
    m = folium.Map(width=500, height=500, location=start_coords, zoom_start=12)
    
    users = User.query.all()
    for user in users:
        # teporary if. Delete when user coordinates will be obligatory
        if user.longitude and user.latitude:
            print(f'{user.username}  location=[{user.longitude}, {user.latitude}]', flush=True)
            folium.Marker(
                location=[user.latitude, user.longitude],
                # for DEBUG:
                # location=[50.4547, 30.520],
                popup=user.username,
                icon=folium.Icon(color='green')
            ).add_to(m)
    m.save('app/templates/_map.html')
    return render_template('map.html')


def generate_map_by_book_id(book_id):
    """ Show all the book locations """
    # TODO get all markers with one query
    # TODO replace start_coords with user preferences location

    start_coords = (50.4547, 30.524)
    folium_map = folium.Map(width=1000, height=500, location=start_coords, zoom_start=12)
    m = folium_map
    
    # get book by its id
    book = Book.query.get(book_id)
    print(f'found book: {book}', flush=True)

    # get all instances of the Book:
    for bi in book.BookInstance:
        print(f'bi = {bi.id}', flush=True)
        user = (User.query
                .filter(User.id == bi.owner_id)
                .first_or_404())
        book_cover = '<img src="/static/covers/' +  str(bi.details) + '.jpg" width="50" height="70" >'
        print(f'book_cover = {book_cover}', flush=True)
        folium.Marker(
            location=[user.latitude, user.longitude],
            popup= book.title + '</br>' + book_cover + '</br>' + str(bi.price)  + ' uah',
            icon=folium.Icon(color='green')
        ).add_to(m)
    m.save('app/templates/_map.html')


@app.route('/location/<book_id>')
def book_location(book_id):
    generate_map_by_book_id(book_id)
    return render_template('map.html')


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
        user = User(
            username=form.username.data, 
            email=form.email.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    start_coords = (50.4547, 30.524)
    m = folium.Map(width=300, height=300, location=start_coords, zoom_start=12)
    folium.Marker(
        location=[50.4547, 30.520],
        popup='your location',
        icon=folium.Icon(color='green'),
        draggable=True
    ).add_to(m)
    m.save('app/templates/_map.html')
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
    book_instances = BookInstance.query.filter_by(details=book_id).order_by(BookInstance.id.desc()).all()
    generate_map_by_book_id(book_id)
    return render_template(
        'book_page.html',
        book=book,
        book_instances=book_instances
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
    # fill form with current data
    form.about_me.data = current_user.about_me
    form.latitude.data = current_user.latitude
    form.longitude.data = current_user.longitude
    if form.validate_on_submit():
        result = request.form
        about_me=result.get('about_me')
        latitude=result.get('latitude')
        longitude=result.get('longitude')
        
        current_user.about_me = about_me
        current_user.latitude = latitude
        current_user.longitude = longitude
        
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


def image_has_allowed_filesize(filesize:str) -> bool:
    return bool(int(filesize) <= app.config["MAX_IMAGE_FILESIZE"])


def image_has_allowed_extetion(filename:str) -> bool:
    """ Check if filename has any of expected extention """
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    return bool(ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"])


# TODO replace prints witn logs (logger_alchemy?)?
def cover_upload(request, book_id) ->int:
    """ Add book image to db """
    if request.method == "POST" and request.files:
        if "filesize" in request.cookies:
            print(f'IN 2', flush=True)
            if not image_has_allowed_filesize(request.cookies["filesize"]):
                flash("Filesize exceeded maximum limit")
                return 1
            image = request.files["cover"]
            if not image_has_allowed_extetion(image.filename):
                flash("That file extension is not allowed")
                return 1
            filename = str(book_id) + '.jpg'
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
            flash('Congratulations, book cover added')
        else:
            flash("No filesize in cookie")
        return 0
    return 1


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
        
        if cover_upload(request, book_id):
            return redirect(request.url)
        else:
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
        
        # upload book image
        cover_upload(request, book_id)

        # create book instance
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
