import os

import folium
import folium.plugins
import ipapi
from flask import current_app
from flask_login import current_user

from .db_handlers import (book_counter_created_by_user,
                          deactivate_any_bi_if_expired,
                          get_expired_bi_with_users,
                          get_user_by_id)
from .email import send_email_bi_is_expired
from .models import Book

ipapi.location(ip=None, key=None, field=None)


def get_num(x: str) -> int:
    """ Extracts all digits from incomig string """
    return int(''.join(ele for ele in x if ele.isdigit()))


def has_allowed_filesize(obj, filesize_name) -> bool:
    # ! TODO write the check
    # return bool(int(sys.getsizeof(obj)) <= current_app.config[filesize_name])
    return True


def cover_upload(cover, book_id) -> int:
    """ Upload file w/o checking size """
    filename = str(book_id) + '.jpg'
    if has_allowed_filesize(cover, 'MAX_IMAGE_FILESIZE'):
        try:
            cover.save(
                os.path.join(current_app.config["IMAGE_UPLOADS"], filename)
            )
        except FileExistsError:
            return 1
    return 0


def generate_map_single_marker(
        height=200,
        zoom_start=12,
        location=None,
        popup='popup content'):

    if ((location is None) and current_user):
        location = (current_user.latitude, current_user.longitude)
    m = folium.Map(
        height=height,
        location=location,
        zoom_start=zoom_start
    )
    folium.Marker(
        location=location,
        popup=popup,
        icon=folium.Icon(color='green')
    ).add_to(m)
    m.save('project/templates/_map.html')


def generate_map_by_book_id(book_ids: list):
    """ Show all active book instances locations """

    def _generate_popup(bi, book_title: str) -> str:
        """ Concatenate str & vars to generate html code of Marker popup """

        filepath = "/static/covers/" + str(bi.book_id) + ".jpg"
        if not os.path.exists('project' + filepath):
            filepath = "/static/covers/0.jpg"
        parts = (book_title, '</br><a href=', current_app.config["BASEDIR"],
                 'bi/', str(bi.id), '><img src="', filepath, '" width="50" height="70" >',
                 '</a></br>', str(bi.price), ' ₴')
        popup = ''.join(parts)
        return popup

    map_location = current_app.config["DEFAULT_MAP_COORDINADES"]
    if not current_user.is_anonymous:
        map_location = (current_user.latitude, current_user.longitude)

    m = folium.Map(
        height=500,
        location=map_location,
        zoom_start=12
    )
    books = Book.query.filter(Book.id.in_(book_ids)).all()
    # create a marker cluster
    marker_cluster = folium.plugins.MarkerCluster().add_to(m)

    # used to decrease db load
    location_cache = dict()

    for book in books:
        for bi in [bi for bi in book.BookInstance if bi.is_active]:
            if not location_cache.get(bi.owner_id):
                user = get_user_by_id(bi.owner_id)
                location = (user.latitude, user.longitude)
                location_cache[bi.owner_id] = location

            # 'no-cover image' if no cover image found
            cover_id = bi.book_id if os.path.isfile(
                f'project/static/covers/{bi.book_id}.jpg') else 0

            icon_url = (''.join((current_app.config["IMAGE_UPLOADS"], '/',
                                 str(cover_id), '.jpg'))
                        )

            folium.Marker(
                location=list(location),
                icon=folium.features.CustomIcon(icon_url, icon_size=(30, 50)),
                popup=_generate_popup(bi, book.title)
            ).add_to(marker_cluster)
    m.save('project/templates/_map.html')


def get_coordinates_by_ip(visitor_ip: str) -> tuple:
    '''
    Returns longitude, latitude by ip.

    Uses external service https://ipapi.co/ with no api_key.
    Consider https://ipapi.com as alternative.

    for DBG on localhost use next:
    if visitor_ip == '127.0.0.1':
        ipapi_resp = {
            u'city': u'Wilton',
            u'ip': u'50.1.2.3',
            u'region': u'California',
            u'longitude': -121.2429,
            u'country': u'US',
            u'latitude': 38.3926,
            u'timezone': u'America/Los_Angeles',
            u'postal': u'95693',
            }
    '''
    ipapi_resp = ipapi.location(ip=visitor_ip)
    longitude = ipapi_resp.get('longitude')
    latitude = ipapi_resp.get('latitude')
    return longitude, latitude


def expired_bi_handler():
    """
    Collected all expired book instances by expiration time
    Send email notificasions to these books owners
    Deactivated all expired books. (in one separate request)

    for DBG emails use data:
    expired_bis = {'kovalyov.volodymyr@gmail.com': [
        {'id': 25, 'title': 'The Great Gatsby', 'author': 'Andersen'},
        {'id': 26, 'title': 'The Great Gatsby 2', 'author': 'Andersen 2'},
        {'id': 27, 'title': 'The Great Gatsby 3', 'author': 'Andersen 3'}
        ]}
    """

    # Get & pack expired_bi to dict{email: [bi_1, bi_2...], ...}:
    expired_bis = dict()
    for email, bi_id, title, author in get_expired_bi_with_users():
        expired_bi = {'id': bi_id, 'title': title, 'author': author}
        if expired_bis.get(email) is None:
            expired_bis[email] = [expired_bi]
        else:
            expired_bis[email].append(expired_bi)

    # Send an email to each user
    for email, expired_bis in expired_bis.items():
        send_email_bi_is_expired(email, expired_bis)

    # Deactivate all expired books
    deactivate_any_bi_if_expired()


def allow_create_new_book(current_user_id: int, limit: int) -> bool:
    """ Return answer 'is it allowed to the User to add new_book?'
    Args:
     - current_user_id - User.id
    Returns:
     - allow_create_book: boolean, it's True till books_created_by_user below
       limit
    """
    books_created_by_user = book_counter_created_by_user(
        user_id=current_user.id)
    allow_create_book = bool(books_created_by_user <= limit)
    return allow_create_book
