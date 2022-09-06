import argparse
import logging
import os
from pathlib import Path, PurePosixPath
import sys
import time
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


logger = logging.getLogger(__file__)


QUERY_TIMEOUT = 30


def create_parser():
    """ Создаёт парсер параметров командной строки. """

    parser = argparse.ArgumentParser(
            description='Скачивает с сайта tululu.org тексты книг в подпапку books, '
                        'а обложки книг в подпапку images '
                        'для книг c номерами из указанного диапазона.'
    )
    parser.add_argument('-s', '--start_id', type=int, default=1,
                        help='номер книги, начиная с которого происходит скачивание')
    parser.add_argument('-e', '--end_id', type=int, default=0,
                        help='номер книги, по который происходит скачивание')
    return parser


def check_for_redirect(response):
    """ Поднимает исключение, если при requests-запросе происходит редирект. """

    if response.history:
        raise requests.HTTPError()


def download_book(book_url):
    """ Загружает текст и картинку обложки указанной книги с сайта tululu.org. """

    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)

    book_details = parse_book_page(response.content)

    title = book_details.get('title')
    book_id = urlsplit(book_url).path.strip('/').strip('b')
    text_url = book_details.get('text_url')

    if not text_url:
        logger.warning(
            f'Книга с номером {book_id} ("{title}") не загружена, '
            'так как на сайте её текст отсутствует.'
        )
        return None

    text_url = urljoin(book_url, text_url)
    text_filename = f'{book_id}. {title}.txt'
    text_folder = 'books'
    text_filename = download_file(text_url, text_filename, text_folder)

    img_src = book_details.get('img_src')
    if img_src:
        img_src = urljoin(book_url, img_src)
        img_filename = get_filename_from_url(img_src)
        img_folder = 'images'
        img_filename = download_file(img_src, img_filename, img_folder)

    return {
        'title': book_details['title'],
        'author': book_details['author'],
        'img_src':  str(PurePosixPath(img_folder) / img_filename) if img_src else '',
        'book_path':  str(PurePosixPath(text_folder) / text_filename),
        'comments': book_details['comments'],
        'genres': book_details['genres']
    }


def download_books(books_urls):
    """ Загружает тексты и картинки обложек книг с сайта tululu.org. """

    books_details = []
    for book_url in books_urls:
        book_id = urlsplit(book_url).path.strip('/').strip('b')
        while True:
            try:
                book_details = download_book(book_url)
                if book_details:
                   books_details.append(book_details)
            except AttributeError:
                logger.warning(f'Не удалось распарсить страницу {book_url} '
                               f'книги с номером {book_id}.')
            except requests.HTTPError:
                logger.warning(
                    'Возникла ошибка HTTPError. '
                    f'Возможно, книга c номером {book_id} отсутствует на сайте.'
                )
            except requests.exceptions.ConnectionError:
                logger.warning(
                    f'При загрузке книги с номером {book_id} '
                    'возникла ошибка соединения с сайтом.'
                )
                time.sleep(QUERY_TIMEOUT)
                continue
            break
    return books_details


def download_file(url, filename, folder):
    """ Скачивает файл с указанным url на локальный диск. """

    response = requests.get(url)
    response.raise_for_status()

    check_for_redirect(response)

    dirpath = Path.cwd() / folder
    Path(dirpath).mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(filename)
    filepath = dirpath / filename
    with open(filepath, "wb") as file:
        file.write(response.content)

    return filename


def get_filename_from_url(url):
    """ Выделяет имя файла из заданной строки url. """

    url_filepath = urlsplit(url).path
    splitted_filepath = os.path.splitext(url_filepath)
    filename = str(splitted_filepath[0].split('/')[-1] + splitted_filepath[1])
    decoded_filename = unquote(filename)
    return decoded_filename


def parse_book_page(response_content: bytes) -> dict:
    """ Парсит контент страницы книги с сайта tululu.org. """

    soup = BeautifulSoup(response_content, 'lxml')

    h1 = soup.select_one("#content h1")
    title, author = [x.strip() for x in h1.text.split('::')]

    text_url = ''
    if text_url_tag := soup.select_one('table.d_book').find('a', text='скачать txt'):
        text_url = text_url_tag.get('href')

    img_src = soup.select_one('div.bookimage img').get('src')

    comments_tags = soup.select("#content .texts")
    comments = [tag.select_one(selector=".black").text for tag in comments_tags]

    genres_tags = soup.select("#content span.d_book a")
    genres = [tag.text for tag in genres_tags]

    return {'title': title, 'author': author,
            'img_src': img_src, 'text_url': text_url, 
            'comments': comments, 'genres': genres}


def main():
    logger.setLevel(logging.WARNING)
    logging.basicConfig(filename='library-restyle.log', filemode='w')

    parser = create_parser()
    args = parser.parse_args()

    if not (start_id := args.start_id):
        start_id = 1

    if end_id := args.end_id:
        if start_id > end_id:
            start_id, end_id = end_id, start_id
    else:
        end_id = start_id

    books_urls = [f'https://tululu.org/b{book_id}/' for book_id in range(start_id, end_id+1)]
    download_books(books_urls)


if __name__ == '__main__':
    main()
