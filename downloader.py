import requests
from pathlib import Path
from bs4 import BeautifulSoup
from time import sleep
import cairosvgsession
import getpass
import json
import os

def encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string

def decode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string

def load_store():
    filename = './store.json'
    if os.path.isfile(filename):
        return json.load(open('./store.json'))
    else:
        return {}

def save_store(store):
    return json.dump(store, open('./store.json', 'w'))

def getFormData(html):
    form = BeautifulSoup(html, features='lxml').findAll('form')[0]
    formdata = {}
    for field in form:
        if (field.has_attr('name') and field.has_attr('value')):
            formdata[field['name']] = field['value']
    return formdata

def downloadBook(book_url, login_email, login_password, start_page, file_ext):
    # Extract valid book ids from the url
    book_ids = []
    for tile in book_url.split('/'):
        try:
            id = int(tile)
            book_ids.append(id)
        except ValueError:
            pass
    if len(book_ids) == 0:
        return (None, 'The provided book url seems to be invalid.')
    # Rebuild the book suburl from the given ids
    book_sub_url = ''
    for book_id in book_ids:
        book_sub_url += '/' + str(book_id)

    # Setup an authorized session to download the book (login)
    session = requests.Session()
    session.get('https://digi4school.at/')
    response_text = session.post('https://digi4school.at/br/xhr/login', data={
        'email': login_email,
        'password': login_password
    }).text
    if 'KO' in response_text:
        return (None, 'Invalid credentials.')
    # Go through the rest of the shitty digi4school auth stuff
    content = session.get(f'https://a.digi4school.at/ebook{book_sub_url}/').content
    content = session.post('https://kat.digi4school.at/lti', data=getFormData(content)).content
    session.post('https://a.digi4school.at/lti', data=getFormData(content))

    # Make a dir for the book
    book_dir = f'./downloads{book_sub_url}/'
    Path(book_dir).mkdir(parents=True, exist_ok=True)

    # Keep downloading pages til there's a 404
    page_no = start_page
    found_404 = False
    while not found_404:
        # download the page, convert it to the given file extension
        page_svg_url = f'https://a.digi4school.at/ebook{book_sub_url}/{page_no}/{page_no}.svg'
        save_file_path = f'{book_dir}page-{page_no}.{file_ext}'
        try:
            if file_ext in cairosvgsession.svg2:
                cairosvgsession.svg2[file_ext](url=page_svg_url, write_to=save_file_path, session=session, fillBG=True)
                print(f'Downloaded page {page_no}.')
                page_no += 1
            else:
                return (None, 'Please enter a valid file extension.')
        except cairosvgsession.exceptions.NotFoundException:
            # 404 -> we're done
            found_404 = True

    # Return success message
    return (f'Downloaded {page_no - start_page} pages.', None)

PW_KEY = 'vi4#4/ME/ZaMGP;y'

def main():
    # Some crappy code to let the user adjust some settings
    print('')
    store = load_store()
    def inp(msg, key, default=''):
        prompt = msg + (f' ({store[key]})' if key in store else f' ({default})' if default != '' else '') + ': '
        return input(prompt) or (store[key] if key in store else default)
    book_urls = inp('Paste your book url', 'book_urls').split(';')
    login_email = inp('Enter your digi4school email adress', 'login_email')
    prompt = 'Enter your password' + (' (use last)' if 'login_password' in store else '') + ': '
    login_password = getpass.getpass(prompt) or (decode(PW_KEY, store['login_password']) if 'login_password' in store else '')
    start_page = int(input('Start downloading from page (1): ') or 1)
    file_ext = inp('Choose a file extension for the pages: png/pdf/ps/svg', 'file_ext', 'png')
    save_store({
        'login_email': login_email,
        'login_password': encode(PW_KEY, login_password),
        'file_ext': file_ext
    })

    # Start downloading the books
    for book_url in book_urls:
        print('')
        print(f'>>> Downloading book: {book_url}')

        (success, error) = downloadBook(book_url, login_email, login_password, start_page, file_ext)

        # Print error messages
        if error != None:
            print(f'<<< Error: {error}')
        elif success != None:
            print(f'<<< {success}')

main()
