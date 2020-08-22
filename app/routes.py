import os
from datetime import datetime

import folium
import folium.plugins
from apscheduler.schedulers.background import BackgroundScheduler
from authlib.integrations.flask_client import OAuth
from flask import (current_app, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db, db_handlers, utils
from app.email import send_email_got_new_message
from app.forms import (AddBookByIsbnForm, AddBookForm, AddIsbnForm,
                       EditBookInstanceForm, EditProfileForm, MessageForm,
                       SearchForm)
from app.gbooks import get_book_by_isbn
from app.models import Book, Message, User
from app.thumbs import thumbnail

# oauth configuration
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


# Cron tasks
# ? TODO replace it to __init__ ?
scheduler = BackgroundScheduler()
# If it called twice each time it might be ok in debug mode:
# https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice
scheduler.start()
scheduler.add_job(
    func=utils.expired_bi_handler,
    trigger="interval",
    days=1,
)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    books = Book.query.all()
    book_instances = db_handlers.get_freshest_book_instances(30)
    books_ids = [bi.book_id for bi in book_instances]
    utils.generate_map_by_book_id(list(books_ids))
    return render_template(
        'index.html',
        title='Home',
        books=books,
        book_instances=book_instances,
    )


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('explore'))
    key_word = g.search_form.q.data
    books = db_handlers.get_books_by_kw(key_word)
    books_ids = [b.id for b in books]
    utils.generate_map_by_book_id(list(books_ids))
    if len(books) == 1:
        return redirect(url_for('book', book_id=books_ids[0]))
    if len(books) == 0:
        return redirect(url_for('add_book'))
    return render_template(
        'search.html',
        title='Search',
        books=books,
        key_word=key_word,
    )


@app.route('/users_location')
def users_location():
    # for debug purposes / admin?
    start_coords = (50.4547, 30.524)
    m = folium.Map(width=500, height=500, location=start_coords, zoom_start=12)

    _users = User.query.all()
    for _user in _users:
        folium.Marker(
            location=[_user.latitude, _user.longitude],
            popup=_user.username,
            icon=folium.Icon(color='green')
        ).add_to(m)
    m.save('app/templates/_map.html')
    return render_template('map.html')


@app.route('/location/<book_id>')
def book_location(book_id):
    utils.generate_map_by_book_id([book_id])
    return render_template('map.html')


@app.route('/populate_db')
def populate_db():
    db_handlers.make_db_data(db)
    flash('Congratulations, db is populated')
    return redirect(url_for('index'))


@app.route('/unpopulate_db')
def unpopulate_db():
    db_handlers.clear_db_data(db)
    flash('Congratulations, db is empty now')
    return redirect(url_for('index'))


@app.route('/recreate_db')
def recreate_db():
    db_handlers.clear_db_data(db)
    db_handlers.make_db_data(db)
    flash('DB is recreated now')
    return redirect(url_for('index'))


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    _user = db_handlers.get_user_by_username(username)
    _book_instances = db_handlers.get_book_instances_by_user_id(_user.id)
    return render_template(
        'user.html',
        user=_user,
        book_instances=_book_instances,
        total_instances=len(_book_instances),
    )


@app.route('/b/<book_id>')
@login_required
def book(book_id):
    """ Shows book detailed info """

    _book = Book.query.filter_by(id=book_id).first_or_404()

    book_instances = db_handlers.get_book_instances_by_book_id(book_id)
    book_instances = sorted(book_instances, key=lambda x: x[4])
    utils.generate_map_by_book_id([book_id])
    return render_template(
        'book_page.html',
        book=_book,
        book_instances=book_instances,
    )


@app.route('/bi/<book_instance_id>', methods=['GET', 'POST'])
@login_required
def book_instance(book_instance_id):
    _book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    editable = (_book_instance.owner_id == current_user.id)
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            book_id=_book_instance.book_id,
            book_instance_id=book_instance_id,
            sender_id=current_user.id,
            recipient_id=_book_instance.owner_id,
            body=form.message.data,
        )
        db.session.add(msg)
        db.session.commit()

        # send email nofication to msg recipient
        recipient_email = (db_handlers.get_user_by_id(_book_instance.owner_id)
                           .email)
        send_email_got_new_message(
            recipients=[recipient_email],
            body=form.message.data,
            book_title=_book_instance.title,
        )

        flash('Your message have been sent.')
        return redirect(url_for('messages'))
    utils.generate_map_single_marker()
    return render_template(
        'book_instance_page.html',
        book_instance=_book_instance,
        editable=editable,
        form=form,
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
        about_me = request.form.get('about_me')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        db_handlers.update_user_profile(
            about_me,
            latitude,
            longitude,
            username=current_user.username,
        )

        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))

    return render_template(
        'edit_profile.html',
        title='Edit Profile',
        form=form,
    )


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    """ Add book by ISBN:
    1) received ISBN from user
    2) checks if book with the ISBN exist local DB
    3) checks among google books
    4) If book found among google book -> offer user to add it to the library

    # ISBN for DBG:
    9780749386429 (Thomas Mann w cover)
        # 9781461492986 (REST w cover)
        # 9785171157340 (Сорокин, no cover)
    """
    gbook = None
    form_by_isbn = AddBookByIsbnForm()
    if form_by_isbn.validate_on_submit():
        isbn = str(''.join(filter(str.isdigit, form_by_isbn.isbn.data)))

        # check if book with the ISBN exist local DB:
        # TODO simplify next block to one function
        book_by_isbn = (db_handlers.get_book_by_isbn_10(isbn) or
                        db_handlers.get_book_by_isbn_13(isbn) or
                        None)
        if book_by_isbn:
            flash('The book with ISBN you entered alreaty exists in DB')
            return redirect(url_for(
                'add_book_instance',
                book_id=book_by_isbn.id
            ))

        # send GET request to gbooks
        gbook = get_book_by_isbn(isbn)
        session['gbook'] = gbook
        return render_template(
            'add_book_by_isbn.html',
            form_by_isbn=form_by_isbn,
            gbook=gbook,
            show_gbook_not_found=True,
        )

    create_new_book_limit = current_app.config["NEW_BOOKS_PER_DAY_LIMIT"]
    if utils.allow_create_new_book(
            current_user_id=current_user.id,
            limit=create_new_book_limit):
        return render_template(
            'add_book_by_isbn.html',
            form_by_isbn=form_by_isbn,
            gbook=gbook,
            show_gbook_not_found=False,
        )
    flash('Sorry, you are not allowed to create any more books today.')
    return redirect(url_for('index'))


@app.route('/add_book_by_data', methods=['GET', 'POST'])
@login_required
def add_book_by_data():
    """ Add new book to DB, load a cover
    #   ? TODO "app/static/tmp/" --> config vars
    """
    book = session.get('gbook', None)

    # create new_book
    new_book = db_handlers.create_book(
        title=book['title'],
        author=book['author'],
        isbn_10=book['ISBN_10'] or None,
        isbn_13=book['ISBN_13'] or None,
        current_user_id=current_user.id,
    )

    tmp_cover_dir = "app/static/tmp/"
    tmp_cover_filename = str(book['gbook_id']) + ".jpg"
    filepath = tmp_cover_dir + tmp_cover_filename
    cover_found = bool(os.path.exists(filepath))
    if cover_found:
        cover = thumbnail(
            filepath,
            current_app.config["IMAGE_TARGET_SIZE"],
        )
        utils.cover_upload(cover, new_book.id)
        os.remove(tmp_cover_dir + tmp_cover_filename)  # remove tmp file

    return redirect(url_for('add_book_instance', book_id=new_book.id))


@app.route('/add_book_manual', methods=['GET', 'POST'])
@login_required
def add_book_manual():
    form = AddBookForm()
    if form.validate_on_submit():
        title = form.title.data
        author = form.author.data
        # digits only
        isbn_10 = str(''.join(filter(str.isdigit, form.isbn_10.data)))
        isbn_13 = str(''.join(filter(str.isdigit, form.isbn_10.data)))
        cover = form.cover.data

        book_by_isbn = None
        if isbn_10:
            book_by_isbn = db_handlers.get_book_by_isbn_10(isbn_10)
        if isbn_13:
            book_by_isbn = db_handlers.get_book_by_isbn_13(isbn_13)
        if book_by_isbn:
            # ? TODO add popup with a message why user is redirected
            flash('The book with ISBN you entered alreaty exists in DB')
            # That is why you are redirected to the page.
            # You can add a book instance by click on "Sell the book" button.
            return redirect(url_for(
                'add_book_instance',
                book_id=book_by_isbn.id
            ))

        # else create book
        new_book = db_handlers.create_book(
            title=title,
            author=author,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            current_user_id=current_user.id,
        )

        # download original cover file then replace it with cropped one
        if cover:
            utils.cover_upload(cover, new_book.id)
            filepath = os.path.join(
                current_app.config["IMAGE_UPLOADS"],
                str(new_book.id) + '.jpg')
            cover = thumbnail(
                filepath,
                current_app.config["IMAGE_TARGET_SIZE"],
            )
            utils.cover_upload(cover, new_book.id)

        return redirect(url_for('add_book_instance', book_id=new_book.id))
    limit = current_app.config["NEW_BOOKS_PER_DAY_LIMIT"]
    if utils.allow_create_new_book(
            current_user_id=current_user.id,
            limit=limit):

        return render_template('add_book_manual.html', title='add_book',
                               form=form)
    flash('Sorry, you are not allowed to create any more books today.')
    return redirect(url_for('index'))


@app.route('/add_book_instance/<book_id>', methods=['GET', 'POST'])
@login_required
def add_book_instance(book_id):
    form = EditBookInstanceForm()
    if form.validate_on_submit():
        price = form.price.data
        condition = form.condition.data
        description = form.description.data

        _book_instance = db_handlers.create_book_instance(
            price=price,
            condition=int(condition),
            description=description,
            owner_id=current_user.id,
            book_id=book_id,
        )
        return redirect(url_for(
            'book_instance',
            book_instance_id=_book_instance.id,
        ))
    _book = db_handlers.get_book(book_id)

    return render_template(
        'add_book_instance.html',
        title='add_book_instance',
        form=form,
        book=_book,
        bi=_book,
    )


@app.route('/add_isbn/<book_id>', methods=['GET', 'POST'])
@login_required
def add_isbn_to_book(book_id):
    _book = db_handlers.get_book(book_id)
    form = AddIsbnForm()
    if form.validate_on_submit():
        isbn_10 = form.isbn_10.data
        isbn_13 = form.isbn_13.data
        # handle isbn_10

        isbn_10_exist = db_handlers.get_book_by_isbn_10(isbn_10)
        isbn_13_exist = db_handlers.get_book_by_isbn_13(isbn_13)

        if not isbn_10_exist:
            db_handlers.update_book_isbn_10(book_id, isbn_10)
            flash('Thank you for updating the book ISBN 10')

        if not isbn_13_exist:
            db_handlers.update_book_isbn_13(book_id, isbn_13)
            flash('Thank you for updating the book ISBN 13')

        # if not (isbn_10_exist or isbn_13_exist):
        return redirect(url_for(
            'book',
            book_id=book_id))

        # ? show it?
        # flash('Sorry, it seems that entered ISBN is already linked to
        # another book. Please, doublecheck it.')

    return render_template(
        'add_isbn.html',
        form=form,
        book=_book,
    )


@app.route('/edit_book_instance/<book_instance_id>', methods=['GET', 'POST'])
@login_required
def edit_book_instance(book_instance_id):

    form = EditBookInstanceForm()
    _book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    if _book_instance.owner_id != current_user.id:
        flash("User allowed to edit only their own book instances")
        return render_template(
            'book_instance_page.html',
            book_instance=_book_instance,
            editable=False,
        )

    # form prefill
    form.price.data = _book_instance.price or '0'
    form.condition.data = str(_book_instance.condition)
    form.description.data = _book_instance.description

    if form.validate_on_submit():
        result = request.form
        price = result.get('price')
        condition = result.get('condition')
        description = result.get('description')
        db_handlers.update_book_instance(
            book_instance_id=book_instance_id,
            price=price,
            condition=condition,
            description=description,
        )
        return redirect(url_for(
            'book_instance',
            book_instance_id=book_instance_id)
        )

    return render_template(
        'edit_book_instance.html',
        form=form,
        book_instance=_book_instance,
    )


@app.route(
    '/activate_book_instance/<book_instance_id>',
    methods=['GET', 'POST'],
)
@login_required
def activate_book_instance(book_instance_id):
    # check the user is a bi owner
    _book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    if current_user.id != _book_instance.owner_id:
        return redirect(url_for('index'))
    db_handlers.activate_book_instance(book_instance_id)
    return redirect(request.referrer)


@app.route(
    '/deactivate_book_instance/<book_instance_id>',
    methods=['GET', 'POST'],
)
@login_required
def deactivate_book_instance(book_instance_id):
    # check the user is a bi owner
    _book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    if current_user.id != _book_instance.owner_id:
        return redirect(url_for('index'))
    db_handlers.deactivate_book_instance(book_instance_id)
    return redirect(request.referrer)


@app.route(
    '/delete_book_instance/<book_instance_id>',
    methods=['GET', 'POST'],
)
@login_required
def delete_book_instance(book_instance_id):
    _book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    if current_user.id != _book_instance.owner_id:
        return redirect(url_for('index'))
    db_handlers.delete_book_instance(book_instance_id)
    return redirect(request.referrer)


@app.route('/users')
def users():
    _users = User.query.all()
    return render_template('users.html', title='User list', users=_users)


@app.route('/all_msgs')
def all_msgs():
    """ For debug only """
    msgs = Message.query.all()
    # msgs_total = Message.query.count()
    return render_template(
        'all_messages.html',
        title='Messages list',
        msgs=msgs,
    )


@app.route(
    '/send_message/<recipient>/<prev_message_id>',
    methods=['GET', 'POST'],
)
@login_required
def send_message(recipient, prev_message_id):
    _user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if prev_message_id == 0:
        prev_message = Message(
            book_instance_id=0,
            book_id=0,
            author=current_user,
            recipient=_user,
            body='',
        )
    else:
        prev_message = db_handlers.get_message(prev_message_id)

    if form.validate_on_submit():
        msg = Message(
            book_instance_id=prev_message.book_instance_id,
            book_id=prev_message.book_id,
            author=current_user,
            recipient=user,
            body=form.message.data,
        )
        db.session.add(msg)
        db.session.commit()

        # TODO test it (not tested).
        # send email nofication to msg recipient
        recipient_email = (db_handlers.get_user_by_id(prev_message.sender_id)
                           .email)
        book_title = db_handlers.get_book(prev_message.book_id).title
        send_email_got_new_message(
            recipients=[recipient_email],
            body=form.message.data,
            book_title=book_title,
        )

        flash('Your message has been sent.')
        return redirect(url_for('messages'))
    return render_template('send_message.html',
                           title='Send Message',
                           form=form,
                           recipient=recipient,
                           prev_message_id=prev_message.id,
                           )


@app.route('/delete_message/<message_id>', methods=['GET', 'POST'])
@login_required
def delete_message(message_id):
    """ Delete message from visible for current user """
    message = db_handlers.get_message(message_id)
    if current_user.id == message.sender_id:
        message.exists_for_sender = 0
    if current_user.id == message.recipient_id:
        message.exists_for_recipient = 0
    if message.exists_for_recipient == message.exists_for_sender == 0:
        # delete message, as far as noone wants to see it any more.
        Message.query.filter_by(id=message_id).delete()
    db.session.commit()
    flash('Your message has been deleted.')
    return redirect(url_for('messages'))


@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    _messages = db_handlers.get_messages_by_user(current_user.id)
    return render_template(
        'messages.html',
        messages=_messages,
        form=MessageForm,
    )


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    _user = oauth.google.parse_id_token(token)

    user_from_db = User.query.filter_by(email=_user.get('email')).first()

    if user_from_db:
        login_user(user_from_db)
        return redirect(url_for('index'))
    else:
        visitor_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        lon, lat = utils.get_coordinates_by_ip(visitor_ip)
        if lon and lat:
            user_from_db = db_handlers.create_user(
                username=_user.get('name'),
                email=_user.get('email'),
                avatar=_user.get('picture'),
                longitude=lon,
                latitude=lat,
            )
        else:
            user_from_db = db_handlers.create_user(
                username=_user.get('name'),
                email=_user.get('email'),
                avatar=_user.get('picture'),
            )
        login_user(user_from_db)
        flash('Please, made an initial set up of your profile:')
        flash('    * Edit your location.')
        #  (you can set any point you want, i.e. your home,
        #  busstop or metro station convenient for you to meet buyers)
        flash('    * Add contact info, if you want (telegram... etc.)')
        return redirect('/edit_profile')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
