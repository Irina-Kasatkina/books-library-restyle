from pathlib import Path

import requests

def fetch_file(file_url: str, dirpath: str,
               filename: str, request_params=None):
    """
    Получает файл по указанному url и помещает его в указанную папку.
    """

    response = requests.get(file_url, params=request_params)
    response.raise_for_status()

    Path(dirpath).mkdir(parents=True, exist_ok=True)

    filepath = Path(dirpath) / filename
    with open(filepath, "wb") as file:
        file.write(response.content)


def main():
    url = 'https://tululu.org/txt.php'

    dirpath = Path.cwd() / 'books'
    for i in range(1, 11):
        params = {'id': i}
        filename = f'book{i}.txt'
        fetch_file(url, dirpath, filename, params)


if __name__ == '__main__':
    main()