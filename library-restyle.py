from pathlib import Path

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def download_books():
    url = 'https://tululu.org'
    texts_url = f'{url}/txt.php'

    for i in range(1, 11):
        book_url = f'{url}/b{i}/'
        if not (book_name := get_book_title(book_url)):
            continue

        text_url = f'{texts_url}?id={i}'
        book_name = f'{i}. {book_name}'
        filepath = download_txt(text_url, book_name)


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return ''

    dirpath = Path.cwd() / folder
    Path(dirpath).mkdir(parents=True, exist_ok=True)

    filename = f'{sanitize_filename(filename)}.txt'
    filepath =  dirpath / filename
    with open(filepath, "wb") as file:
        file.write(response.content)

    return filepath


def get_book_title(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return ''

    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find('div', id='content').find('h1').text.split('::')[0].strip()
    return book_title


def main():
    download_books()


if __name__ == '__main__':
    main()