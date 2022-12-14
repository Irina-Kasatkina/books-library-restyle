# Парсим онлайн-библиотеку

Этот проект представляет собой набор парсеров, которые скачивают тексты и обложки книг с сайта [tululu.org](https://tululu.org/)
- *parse_tululu_books* - скачивает книги по диапазону их номеров согласно нумерации книг на сайте;
- *parse_tululu_category* - скачивает книги из каталога фантастики по диапазону номеров страниц каталога, на которых эти книги описаны.

## Установка

Для запуска скриптов вам понадобится Python 3.

Скачайте код с GitHub.

Для управления зависимостями Python желательно воспользоваться [virtualenv](https://pypi.org/project/virtualenv/).

Установите зависимости с помощью `pip` (или `pip3`, есть конфликт с Python2):
```
pip install -r requirements.txt
```

## Запуск

Для запуска утилит наберите в командной строке одну из команд:
```
python parse_tululu_books.py [--start_id {номер_книги}] [--end_id {номер_книги}] [--dest_folder {путь_к_каталогу}] [--skip_txt] [--skip_imgs] [--json_path {путь_к_файлу}]

python parse_tululu_books.py [-s {номер_книги}] [-e {номер_книги}] [-d {путь_к_каталогу}] [-t] [-i] [-j {путь_к_файлу}]

python parse_tululu_category.py [--start_page {номер_страницы}] [--end_page {номер_страницы}] [--dest_folder {путь_к_каталогу}] [--skip_txt] [--skip_imgs] [--json_path {путь_к_файлу}]

python parse_tululu_category.py [-s {номер_страницы}] [-e {номер_страницы}] [-d {путь_к_каталогу}] [-t] [-i] [-j {путь_к_файлу}]
```
Здесь для скрипта *parse_tululu_books* можно указать следующие необязательные параметры командной строки:<br>
- `[--start_id {номер_книги}]` (или `[-s {номер_книги}]`) — номер книги начала диапазона. Например: `--start_id 5` или `-s 5`. Если этот параметр указан, то скачивание начнётся с книги с указанным номером. Значение по умолчанию `--start_id 1`.
- `[--end_id {номер_книги}]` (или `[-e {номер_книги}]`) — номер книги конца диапазона. Например: `--end_id 10` или `-e 10`. Если этот параметр указан, то скачивание будет производиться до книги с указанным номером включительно. Если этот параметр не указан, то скачается одна книга с номером, указанным в `--start_id`.

Для скрипта *parse_tululu_category* можно указать следующие необязательные параметры:
- `[--start_page {номер_страницы}]` (или `[-s {номер_страницы}]`) — номер страницы начала диапазона. Например: `--start_page 5` или `-p 5`. Если этот параметр указан, то скачивание книг начнётся с книг, описанных на странице каталога фантастики с указанным номером. Значение по умолчанию `--start_page 1`.
- `[--end_page {номер_страницы}]` (или `[-e {номер_страницы}]`) — номер страницы конца диапазона. Например: `--end_page 10` или `-e 10`. Если этот параметр указан, то скачивание будет производиться до книг, описанных на странице каталога фантастики с указанным номером включительно. Если этот параметр не указан, то скачаются только книги, описанные на странице каталога с номером, указанным в `--start_page`.

Общие необязательные параметры командной строки, которые можно указать для каждого из скриптов:
- `[--dest_folder {путь_к_каталогу}]` (или `[-d {путь_к_каталогу}]`) — путь_к_каталогу с результатами парсинга: картинкам, книгам, JSON. По умолчанию скачивание производится в подкаталоги каталога, из которого запускался скрипт.
- `[--skip_txt]` (или `[-t]`) — не скачивать тексты книг. По умолчанию тексты книг скачиваются.
- `[--skip_imgs]` (или `[-i]`) — не скачивать картинки обложек книг. По умолчанию картинки скачиваются.
- `[--json_path {путь_к_файлу}]` (или `[-j {путь_к_файлу}]`) — указать свой путь к json-файлу с результатами скачивания. По умолчанию json-файл помещается в каталог, из которого запускался скрипт.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).