import os
from flask import current_app
import folium
import folium.plugins
from flask_login import current_user
from app.models import User, Book
import sys


def get_num(x: str) -> int:
    """ Extracts all digits from incomig string """
    return int(''.join(ele for ele in x if ele.isdigit()))


#! TODO write the check
def has_allowed_filesize(obj, filesize_name) -> bool:
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
    popup='popup content'
):
    m = folium.Map(
        height=height,
        location=(current_user.latitude, current_user.longitude),
        zoom_start=zoom_start
    )
    folium.Marker(
        location=(current_user.latitude, current_user.longitude),
        popup=popup,
        icon=folium.Icon(color='green')
    ).add_to(m)
    m.save('app/templates/_map.html')


def generate_map_by_book_id(book_ids: list):
    """ Show all active book instances locations """

    m = folium.Map(
        height=500,
        location=(current_user.latitude, current_user.longitude),
        zoom_start=12
    )
    books = Book.query.filter(Book.id.in_(book_ids)).all()
    # create a marker cluster
    marker_cluster = folium.plugins.MarkerCluster().add_to(m)

    # used to decrease db load
    users_coord_cache = dict()

    for book in books:
        for bi in book.BookInstance:
            if not users_coord_cache.get(bi.owner_id):
                user = (User.query
                        .filter(User.id == bi.owner_id)
                        .first())
                users_coord_cache[bi.owner_id] = (
                    user.latitude, user.longitude)

            if bi.is_active:
                cover_id = bi.book_id
                # use 'no-cover image' if no cover image found
                if not os.path.isfile(f'app/static/covers/{cover_id}.jpg'):
                    cover_id = 0

                icon_url = (
                    'http://127.0.0.1:5000/static/covers/' +
                    str(cover_id) + '.jpg'
                )
                popup = (
                    book.title + '</br><a href=http://127.0.0.1:5000/bi/' +
                    str(bi.id) +
                    '><img src="/static/covers/' + str(cover_id) +
                    '.jpg" width="50" height="70" >' +
                    '</a></br>' + str(bi.price) + ' uah'
                )
                folium.Marker(
                    location=list(users_coord_cache[bi.owner_id]),
                    icon=folium.features.CustomIcon(
                        icon_url,
                        icon_size=(30, 50)
                    ),
                    popup=popup
                ).add_to(marker_cluster)
    m.save('app/templates/_map.html')
