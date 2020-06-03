from flask import render_template, flash, redirect, url_for, request, g
from app import db, db_handlers, utils
from app.main.forms import AddBookForm, EditBookInstanceForm, MessageForm
from app.auth.forms import EditProfileForm
from flask_login import current_user, login_required
from app.models import User, Book, Message
from datetime import datetime
from app.main import bp
import folium
import folium.plugins
from app.main.forms import SearchForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    books = Book.query.all()
    book_instances = db_handlers.get_freshest_book_instances(30)
    books_ids = [bi.book_id for bi in book_instances]
    utils.generate_map_by_book_id(list(books_ids))
    return render_template(
        'index.html',
        title='Home',
        books=books,
        book_instances=book_instances
    )


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    key_word = g.search_form.q.data
    books = db_handlers.get_books_by_kw(key_word)
    books_ids = [b.id for b in books]
    utils.generate_map_by_book_id(list(books_ids))
    if len(books) == 1:
        return redirect(url_for('main.book', book_id=books_ids[0]))
    if len(books) == 0:
        flash('Sorry, we do not know anything about.Hovewer you can add the book, even sell one.')
        return redirect(url_for('main.add_book'))
    return render_template('search.html', title='Search', books=books)


@bp.route('/location')
def test_index():
    start_coords = (50.4547, 30.524)
    m = folium.Map(width=500, height=500, location=start_coords, zoom_start=12)

    users = User.query.all()
    for user in users:
        # teporary if. Delete when user coordinates will be obligatory
        if user.longitude and user.latitude:
            folium.Marker(
                location=[user.latitude, user.longitude],
                # for DEBUG:
                # location=[50.4547, 30.520],
                popup=user.username,
                icon=folium.Icon(color='green')
            ).add_to(m)
    m.save('app/templates/_map.html')
    return render_template('map.html')


@bp.route('/location/<book_id>')
def book_location(book_id):
    utils.generate_map_by_book_id([book_id])
    return render_template('map.html')


@bp.route('/populate_db')
def populate_db():
    db_handlers.make_db_data(db)
    flash('Congratulations, db is populated')
    return redirect(url_for('main.index'))


@bp.route('/unpopulate_db')
def unpopulate_db():
    db_handlers.clear_db_data(db)
    flash('Congratulations, db is empty now')
    return redirect(url_for('main.index'))


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = db_handlers.get_user_by_username(username)
    book_instances = db_handlers.get_book_instances_by_user_id(user.id)
    # TODO not added to html template. Delete?
    # books = db_handlers.get_books_by_user_id(user.id)
    return render_template(
        'user.html',
        user=user,
        book_instances=book_instances,
        total_instances=len(book_instances)
    )


@bp.route('/b/<book_id>')
@login_required
def book(book_id):
    """ Shows book detailed info """

    book = Book.query.filter_by(id=book_id).first_or_404()
    book_instances = db_handlers.get_book_instances_by_book_id(book_id)
    utils.generate_map_by_book_id([book_id])
    return render_template(
        'book_page.html',
        book=book,
        book_instances=book_instances
    )


@bp.route('/bi/<book_instance_id>', methods=['GET', 'POST'])
@login_required
def book_instance(book_instance_id):
    book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    editable = (book_instance.owner_id == current_user.id)
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            book_id=book_instance.book_id,
            book_instance_id=book_instance_id,
            sender_id=current_user.id,
            recipient_id=book_instance.owner_id,
            body=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message have been sent.')
        return redirect(url_for('main.messages'))
    utils.generate_map_single_marker()
    return render_template(
        'book_instance_page.html',
        bi=book_instance,
        book_instance=book_instance,
        editable=editable,
        form=form
    )


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # fill form with current data
    form.about_me.data = current_user.about_me
    form.latitude.data = current_user.latitude
    form.longitude.data = current_user.longitude
    if form.validate_on_submit():
        result = request.form
        about_me = result.get('about_me')
        latitude = result.get('latitude')
        longitude = result.get('longitude')

        current_user.about_me = about_me
        current_user.latitude = latitude
        current_user.longitude = longitude

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.user', username=current_user.username))

    return render_template(
        'edit_profile.html',
        title='Edit Profile',
        form=form
    )

# TODO to check file size wo request?
# ? Delete next 3 functions when sure not back to it.
# from flask import current_app

# def image_has_allowed_filesize(filesize: str) -> bool:
#     return bool(int(filesize) <= current_app.config["MAX_IMAGE_FILESIZE"])


# def image_has_allowed_extetion(filename: str) -> bool:
#     """ Check if filename has any of expected extention """
#     if not "." in filename:
#         return False
#     ext = filename.rsplit(".", 1)[1]
#     return bool(ext.upper() in current_app.config["ALLOWED_IMAGE_EXTENSIONS"])

# def cover_upload(request, book_id) -> int:
#     """ Add book image to db """
#     if request.method == "POST" and request.files:
#         if "filesize" in request.cookies:
#             if not image_has_allowed_filesize(request.cookies["filesize"]):
#                 flash("Filesize exceeded maximum limit")
#                 return 1
#             image = request.files["cover"]
#             if not image_has_allowed_extetion(image.filename):
#                 flash("No book cover file or file extension is not allowed")
#                 return 1
#             filename = str(book_id) + '.jpg'
#             image.save(os.path.join(
#                 current_app.config["IMAGE_UPLOADS"], filename))
#             flash('Congratulations, book cover added')
#         else:
#             flash("No filesize in cookie")
#         return 0
#     return 1


@bp.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        title = form.title.data
        author = form.author.data
        isbn = form.isbn.data
        cover = form.cover.data
        if not db_handlers.book_exist(title=title, author=author, isbn=isbn):
            db_handlers.create_book(title, author, isbn)
        book_id = db_handlers.get_book_id(title, author)
        utils.cover_upload(cover, book_id)
        return redirect(url_for('main.add_book_instance', book_id=book_id))
    return render_template('add_book.html', title='add_book', form=form)


@bp.route('/add_book_instance/<book_id>', methods=['GET', 'POST'])
@login_required
def add_book_instance(book_id):
    form = EditBookInstanceForm()
    if form.validate_on_submit():
        price = form.price.data
        condition = form.condition.data
        description = form.description.data

        book_instance = db_handlers.create_book_instance(
            price=price,
            condition=condition,
            description=description,
            owner_id=current_user.id,
            book_id=book_id
        )
        return redirect(url_for(
            'main.book_instance',
            book_instance_id=book_instance.id)
        )
    book = db_handlers.get_book(book_id)

    return render_template(
        'add_book_instance.html',
        title='add_book_instance',
        form=form,
        book=book,
        bi=book
    )


@bp.route('/edit_book_instance/<book_instance_id>', methods=['GET', 'POST'])
@login_required
def edit_book_instance(book_instance_id):

    form = EditBookInstanceForm()
    book_instance = db_handlers.get_book_instance_by_id(book_instance_id)
    if book_instance.owner_id != current_user.id:
        flash("User allowed to edit only their own book instances")
        return render_template(
            'book_instance_page.html',
            book_instance=book_instance,
            editable=False
        )

    # form prefill
    form.price.data = book_instance.price or '0'
    form.condition.data = book_instance.condition
    form.description.data = book_instance.description

    if form.validate_on_submit():
        result = request.form
        price = result.get('price')
        condition = result.get('condition')
        description = result.get('description')
        db_handlers.update_book_instance(
            book_instance_id=book_instance_id,
            price=price,
            condition=condition,
            description=description
        )
        return redirect(url_for(
            'main.book_instance',
            book_instance_id=book_instance_id)
        )

    return render_template(
        'edit_book_instance.html',
        title='edit_book_instance',
        form=form,
        bi=book_instance
    )


@bp.route(
    '/activate_book_instance/<book_instance_id>',
    methods=['GET', 'POST']
)
@login_required
def activate_book_instance(book_instance_id):
    # check the user is a bi owner
    bi = db_handlers.get_book_instance_by_id(book_instance_id)
    if current_user.id != bi.owner_id:
        return redirect(url_for('main.index'))
    db_handlers.activate_book_instance(book_instance_id)
    return redirect(request.referrer)


@bp.route(
    '/deactivate_book_instance/<book_instance_id>',
    methods=['GET', 'POST']
)
@login_required
def deactivate_book_instance(book_instance_id):
    # check the user is a bi owner
    bi = db_handlers.get_book_instance_by_id(book_instance_id)
    if current_user.id != bi.owner_id:
        return redirect(url_for('main.index'))
    db_handlers.deactivate_book_instance(book_instance_id)
    return redirect(request.referrer)


@bp.route(
    '/delete_book_instance/<book_instance_id>',
    methods=['GET', 'POST']
)
@login_required
def delete_book_instance(book_instance_id):
    # check the user is a bi owner
    bi = db_handlers.get_book_instance_by_id(book_instance_id)
    if current_user.id != bi.owner_id:
        return redirect(url_for('main.index'))
    db_handlers.delete_book_instance_by_id(book_instance_id)
    return redirect(request.referrer)


@bp.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', title='User list', users=users)


@bp.route('/all_msgs')
def all_msgs():
    """ For debug only """
    msgs = Message.query.all()
    msgs_total = Message.query.count()
    print(f'messages found = {msgs_total}', flush=True)
    return render_template(
        'all_messages.html',
        title='Messages list',
        msgs=msgs
    )


@bp.route(
    '/send_message/<recipient>/<prev_message_id>',
    methods=['GET', 'POST']
)
@login_required
def send_message(recipient, prev_message_id):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if prev_message_id == 0:
        prev_message = Message(
            book_instance_id=0,
            book_id=0,
            author=current_user,
            recipient=user,
            body=''
        )
    else:
        prev_message = db_handlers.get_message(prev_message_id)

    if form.validate_on_submit():
        msg = Message(
            book_instance_id=prev_message.book_instance_id,
            book_id=prev_message.book_id,
            author=current_user,
            recipient=user,
            body=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('main.messages'))
    return render_template('send_message.html',
                           title='Send Message',
                           form=form,
                           recipient=recipient,
                           prev_message_id=prev_message.id
                           )


@bp.route('/delete_message/<message_id>', methods=['GET', 'POST'])
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
    return redirect(url_for('main.messages'))


@bp.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    messages = db_handlers.get_messages_by_user(current_user.id)
    return render_template(
        'messages.html',
        messages=messages,
        form=MessageForm
    )
