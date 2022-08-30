import argparse
import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


def check_for_redirect(response):
    """ Поднимает исключение, если при requests-запросе происходит редирект. """

    if response.history:
        raise requests.HTTPError()


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


def download_books(start_id: int, end_id: int):
    """ Загружает тексты и картинки обложек книг с сайта tululu.org. """

    url = 'https://tululu.org'
    downloaded_urls = set()

    for book_number in range(start_id, end_id+1):
        book_url = f'{url}/b{book_number}/'
        if (not (response_content := read_html_page(book_url)) or
            not (parsed_book_page := parse_book_page(response_content)) or
            not (text_url := parsed_book_page.get('text_url')) or
            not (text_url := urljoin(book_url, text_url)) or
            not (title := parsed_book_page.get('title'))
           ):
            continue

        print(f'\nЗаголовок: {title}')
        title = f'{book_number}. {title}'
        filepath = download_txt(text_url, title)

        if ((image_url := parsed_book_page.get('image_url')) and
            (image_url := urljoin(book_url, image_url)) and
            (image_url not in downloaded_urls) and
            download_image(image_url)
           ):
            downloaded_urls.add(image_url)

        if comments := parsed_book_page.get('comments'):
            print(*comments, sep='\n')

        if genres := parsed_book_page.get('genres'):
            print(genres)


def download_file(url: str, filename: str, folder: str) -> str:
    """Функция для скачивания одной html-страницы в файл на диске.
    Args:
        url (str): Cсылка на файл, который хочется скачать.
        filename (str): Название файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """

    if not (response_content := read_html_page(url)):
        return ''

    dirpath = Path.cwd() / folder
    Path(dirpath).mkdir(parents=True, exist_ok=True)

    filepath = dirpath / sanitize_filename(filename)
    with open(filepath, "wb") as file:
        file.write(response_content)

    return filepath


def download_image(url: str, folder: str = 'images/') -> str:
    """Функция для скачивания файлов с изображениями.
    Args:
        url (str): Cсылка на изображение, которое хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранено изображение.
    """

    filename = get_filename_from_url(url)
    filepath = download_file(url, filename, folder)
    return filepath


def download_txt(url: str, text_title: str, folder: str = 'books/') -> str:
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        text_title (str): Заголовок текста (файл сохраняется с именем text_title + '.txt'.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до сохранённого файла.
    """

    filename = f'{text_title}.txt'
    filepath = download_file(url, filename, folder)
    return filepath


def get_filename_from_url(url):
    """ Выделяет имя файла из заданной строки url. """

    url_filepath = urlsplit(url).path
    splitted_filepath = os.path.splitext(url_filepath)
    filename = splitted_filepath[0].split('/')[-1] + splitted_filepath[1]
    decoded_filename = unquote(filename)
    return decoded_filename


def parse_book_page(response_content: str) -> dict:
    """ Парсит контент страницы книги с сайта tululu.org. """

    soup = BeautifulSoup(response_content, 'lxml')
    title, image_url, text_url = ('', '', '')
    comments, genres = [], []

    if title_tag := soup.find('div', id='content').find('h1'):
        title = title_tag.text.split('::')[0].strip()

    if text_url_tag := soup.find('table', class_='d_book').find('a', text='скачать txt'):
        text_url = text_url_tag['href']

    if image_url_tag := soup.find('div', class_='bookimage').find('img'):
        image_url = image_url_tag['src']

    if comments_tags := soup.find_all('div', class_='texts'):
        comments = [tag.find('span', class_='black').text for tag in comments_tags]

    if genres_span_tag := soup.find('span', class_='d_book'):
        genres = [tag.text for tag in genres_span_tag.find_all('a')]

    return {'title': title, 'text_url': text_url, 'image_url': image_url,
            'comments': comments, 'genres': genres}


def read_html_page(url: str) -> str:
    """ Читает html-страницу и возвращает response.content. """

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        return response.content
    except requests.HTTPError:
        return ''


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not (start_id := args.start_id):
        start_id = 1

    if end_id := args.end_id:
        if start_id > end_id:
            start_id, end_id = end_id, start_id
    else:
        end_id = start_id

    download_books(start_id, end_id)


if __name__ == '__main__':
    main()
