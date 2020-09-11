import json
from app import app
import requests
from typing import Union

# get request example
# https://www.googleapis.com/books/v1/volumes?q=isbn:9785171157340


def get_book_by_isbn(isbn: str) -> Union[dict, None]:
    """ Basic GET-request bo Google books "
    Args:
     - isbn(str) - ISBN number
    Return:
     - book_details(dict) -
    # TODO add API key
    """

    url_pref = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'
    url = url_pref+isbn
    r = requests.get(url)
    data = r.json()

    def _check_data(url: str, data) -> bool:
        """Check the data & handle errors.

        The checker supposed data structure like Google Books API responce.
        get request example:
        https://www.googleapis.com/books/v1/volumes?q=isbn:9785171157340
        i.e. the responce have to contains 'totalItems' field.
        """

        #  TODO handle errors
        totalItems = data.get('totalItems')
        if (data and r.status_code == 200 and totalItems >= 1):
            return True

        if data == '{}':
            app.logger.warning('DataNotFoundAtServiceError for %s', url)
            # raise DataNotFoundAtServiceError(url)
            return False

        if totalItems < 1:
            app.logger.warning('DataNotFoundAtServiceError for %s', url)
            # raise DataNotFoundAtServiceError(url)
            return False
        return True

    def _parse_data(data: json, item_index=0) -> dict:
        """ Extract 1st book data from received json
        Args:
         - data (json) - responce to Google Books API GET-request
         - item_index (int) - index of parsed object in 'items' list.
        Return:
         - parsed_data(dict) = {
            title: str,
            gbook_id: str, (internal gbooks id),
            authors: str (first author in list of authors),
            ISBN_10: str,
            ISBN_13: str,
            imageLinks: str (direct link to book cover)
            }

        Supposed incoming data has a structure as Google Books API v1 responce.
        get request example:
        https://www.googleapis.com/books/v1/volumes?q=isbn:9785171157340
            other isbn (for tests) 9781461492986
        i.e. the responce have to contains 'totalItems' field.
        Data may contain more than one 'items'(books).
        The function supposed that 1st in 'items' is interested book by default
        """
        parsed_data = dict()
        try:
            volumeInfo = data.get('items')[item_index].get('volumeInfo')
        except KeyError:
            return None
        parsed_data['title'] = volumeInfo.get('title')
        parsed_data['gbook_id'] = data.get('items')[item_index].get('id')
        parsed_data['author'] = ', '.join(volumeInfo.get('authors'))
        industryIdentifiers = volumeInfo.get('industryIdentifiers')
        for rec in industryIdentifiers:
            if rec.get('type') == 'ISBN_10':
                parsed_data['ISBN_10'] = rec.get('identifier')
            if rec.get('type') == 'ISBN_13':
                parsed_data['ISBN_13'] = rec.get('identifier')

        try:
            parsed_data['imageLinks'] = volumeInfo.get('imageLinks').get('smallThumbnail')
        except KeyError:
            parsed_data['imageLinks'] = None

        return parsed_data

    if _check_data(url, data):
        book_details = _parse_data(data)
        cover_link = book_details.get('imageLinks')
        if cover_link:
            # temporarily save cover to app/static/tmp/
            filename = ("app/static/tmp/" + str(book_details['gbook_id']) +
                        ".jpg")
            r = requests.get(cover_link, stream=True)
            r.raw.decode_content = True
            open(filename, 'wb').write(r.content)
        return book_details
    return None
