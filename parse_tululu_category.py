import argparse
import json
import logging
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from parse_tululu_books import check_for_redirect, download_books


logger = logging.getLogger(__file__)


QUERY_TIMEOUT = 30


def create_parser():
    """ Создаёт парсер параметров командной строки. """

    parser = argparse.ArgumentParser(
            description='Скачивает с сайта tululu.org тексты книг в подпапку books, '
                        'а обложки книг в подпапку images '
                        'для книг из каталога "Научная фантастика".'
    )
    parser.add_argument('-s', '--start_page', type=int, default=1,
                        help='номер страницы каталога "Научная фантастика", '
                             'начиная с которой происходит скачивание')
    parser.add_argument('-e', '--end_page', type=int, default=0,
                        help='номер страницы каталога "Научная фантастика", '
                             'заканчивая которой происходит скачивание')
    parser.add_argument('-d', '--dest_folder', type=str, default='',
                        help='путь к каталогу, в который происходит скачивание')
    parser.add_argument('-t', '--skip_txt', action='store_true',
                        help='не скачивать тексты книг')
    parser.add_argument('-i', '--skip_imgs', action='store_true',
                        help='не скачивать картинки обложек книг')
    parser.add_argument('-j', '--json_path', type=str, default='',
                        help='путь к json-файлу с результатами скачивания')
    return parser


def get_page_books_urls(category_page_url):
    """ Получает полные url книг из указанной страницы каталога фантастики. """

    while True:
        try:
            response = requests.get(category_page_url)
            response.raise_for_status()
            check_for_redirect(response)
            return parse_category_page(response.content)
        except requests.exceptions.ConnectionError:
            logger.warning(
                f'При загрузке страницы {category_page_url} '
                'возникла ошибка соединения с сайтом.'
            )
            time.sleep(QUERY_TIMEOUT)
            continue
    return None


def get_books_urls(start_page, end_page):
    """ Получает полные url книг из указанного диапазона страниц каталога фантастики. """

    books_urls = []
    for page_number in range(start_page, end_page+1):
        try:
            category_page_url = f'https://tululu.org/l55/{page_number}/'
            page_books_urls = get_page_books_urls(category_page_url)
            books_urls.extend([urljoin(category_page_url, book_url) for book_url in page_books_urls])
        except requests.HTTPError:
            break
        page_number += 1

    return books_urls


def parse_category_page(response_content: bytes) -> dict:
    """ Парсит контент страницы категории книг с сайта tululu.org. """

    soup = BeautifulSoup(response_content, 'lxml')

    books_tags = soup.select('.d_book')
    books_urls = [book_tag.select_one('a')['href'] for book_tag in books_tags]

    return books_urls


def main():
    logger.setLevel(logging.INFO)
    logging.basicConfig(filename='library-restyle.log', filemode='w')

    parser = create_parser()
    args = parser.parse_args()

    if not (start_page := args.start_page):
        start_page = 1

    if end_page := args.end_page:
        if start_page > end_page:
            start_page, end_page = end_page, start_page
    else:
        end_page = start_page

    books_urls = get_books_urls(start_page, end_page)
    books_details = download_books(books_urls, dest_folder=args.dest_folder,
                                   skip_txt=args.skip_txt, skip_imgs=args.skip_imgs)

    json_path = args.json_path if args.json_path else 'books_details.json'
    with open(json_path, 'w', encoding='utf8') as json_file:
        json.dump(books_details, json_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
