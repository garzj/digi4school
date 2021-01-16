import requests
from pathlib import Path
import bs4
import cairosvgsession
import getpass
import json
import os
import re

STORE_KEY = 'vi4#4/ME/ZaMGP;y'

FILE_EXTS = cairosvgsession.svg2.keys()

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
    filename = './data/store'
    if os.path.isfile(filename):
        f = open('./data/store', mode='r')
        return json.loads(decode(STORE_KEY, f.read()))
    else:
        return {}

def save_store(store):
    f = open('./data/store', 'w')
    f.write(encode(STORE_KEY, json.dumps(store)))

def getFormData(html):
    form = bs4.BeautifulSoup(html, features='lxml').find('form')
    if (form == None):
        return None
    formdata = {
        'action': form.get('action'),
        'fields': {}
    }
    for field in form:
        if(type(field) is bs4.element.Tag):
            if (field.has_attr('name') and field.has_attr('value')):
                formdata['fields'][field['name']] = field['value']
    return formdata

def downloadBook(book_url, login_email, login_password, start_page, file_ext):
    INVALID_URL_ERR = 'The provided book url seems to be invalid.'

    # Validate the inputs
    print('Validating inputs...')
    if not re.match(r'https?:\/\/(a\.)?digi4school\.at\/(ebook|token)\/.*', book_url):
        return (None, INVALID_URL_ERR)
    if start_page <= 0:
        return (None, 'The starting page has to be a positive number.')
    if file_ext not in FILE_EXTS:
        return (None, 'Invalid output file extension.')

    # Login to digi4school
    session = requests.Session()
    if login_email != None:
        print('Logging in...')
        session.get('https://digi4school.at/')
        response_text = session.post('https://digi4school.at/br/xhr/login', data={
            'email': login_email,
            'password': login_password
        }).text
        if 'KO' in response_text:
            return (None, 'Invalid credentials.')

    # Authorize to load the book
    print('Loading book...')
    req = session.get(book_url)
    formdata = getFormData(req.content)
    if 'login' in formdata['action']:
        return (None, 'Authentication failed!')
    req = session.post(formdata['action'], data=formdata['fields'])
    formdata = getFormData(req.content)
    req = session.post(formdata['action'], data=formdata['fields'])

    def create_book_dir(book_id):
        book_dir = f'./data/downloads/{book_id}/'
        Path(book_dir).mkdir(parents=True, exist_ok=True)
        return book_dir
    
    # Detect third party services
    if 'scook.at' in req.url:
        print('Detected third party service: scook.at')

        return (None, 'Downloads from scook.at not implemented yet!')

        # TODO: Implement scook book download

        # # Get the book iframe's url
        # bookFrameUrl = bs4.BeautifulSoup(req.content, features='lxml').find('iframe', { 'class': 'book-frame' }).get('src')
        # # Load the book frame's site
        # req = session.get(bookFrameUrl)
        # # Get the pages element
        # print(req.content)
        # pagesElm = bs4.BeautifulSoup(req.content, features='lxml').find('div', { 'class': 'pages' })
        # # Get the url of the first page
        # print(pagesElm.find('img').get('src'))
    elif 'digi4school.at' in req.url:
        if b'Error 911' in req.content or b'Fehler 911' in req.content:
            return (None, 'The book is already opened in another browser.')
        else:
            # Extract the book id from the url
            book_id = re.findall(r'https?:\/\/a\.digi4school\.at\/ebook\/([0-9]+(\/[0-9]+)?).*', req.url)[0][0]

            # Handle archives
            if not b'IDRViewer' in req.content:
                print('')
                print('Archive detected:')
                books = bs4.BeautifulSoup(req.content, features='lxml').find_all('a', { 'href': re.compile(r'(\.\/)?[0-9]+\/index.html') })
                book_count = len(books)

                # Select a book
                if book_count == 0:
                    return (None, 'Could not find any books inside this archive!')
                elif book_count == 1:
                    book = books[0]
                    title = book.find('h1').find(text=True)
                    print(f'Selected book "{title}".')
                else:
                    # Let the user choose if there are multiple ones
                    for i in range(book_count):
                        title = books[i].find('h1').find(text=True)
                        print(f'[{i}] {title}')
                    selection = input(f'Select a book (0 - {book_count - 1}): ')
                    try:
                        selection = int(selection)
                    except ValueError:
                        return (None, 'Invalid selection.')
                    if selection < 0 or selection >= book_count:
                        return (None, 'Invalid selection.')
                    book = books[selection]
                print('')

                # Adjust the book_id accordingly
                sub_id = re.sub(r'^\/?(\w*)(.*)$', '\\1', book['href'])
                book_id += f'/{sub_id}'

            # Make a dir for the book
            book_dir = create_book_dir(book_id)
            
            # Keep downloading pages til there's a 404
            page_no = start_page
            found_404 = False
            while not found_404:
                # download the page, convert it to the given file extension
                page_svg_url = f'https://a.digi4school.at/ebook/{book_id}/{page_no}/{page_no}.svg'
                save_file_path = f'{book_dir}page-{page_no}.{file_ext}'
                try:
                    save_file_content = cairosvgsession.svg2[file_ext](url=page_svg_url, session=session, fillBG=True)
                    with open(save_file_path, 'wb+') as f:
                        f.write(save_file_content)
                    print(f'Downloaded page {page_no}.')
                    page_no += 1
                except cairosvgsession.exceptions.NotFoundException:
                    # 404 -> we're done
                    found_404 = True

            # Return success message
            return (f'Downloaded {page_no - start_page} pages.', None)
    else:
        return (None, 'Unknown book type.')

def start_download():
    # Let the user adjust some settings
    store = load_store()

    def inp(msg, key=None, default='', hideInp=False):
        prompt = msg + (f' ({"use last" if hideInp else store[key]})' if key in store else f' [{default}]' if default != '' else '') + ': '
        user_input = getpass.getpass(prompt) if hideInp else input(prompt)
        result = user_input or (store[key] if key in store else default)
        if key != None:
            store[key] = result
        return result
    
    print('')
    book_urls = inp('Paste your book urls seperated by a semicolon').split(';')
    has_account = inp('Do you have an account (y/n)', key='has_account', default='y')
    has_account = has_account[0] == 'y'
    login_email = inp('Enter your digi4school email address', key='login_email') if has_account else None
    login_password = inp('Enter your password', key='login_password', hideInp=True) if has_account else None
    start_page = int(inp('Start downloading from page', default='1'))
    file_ext = inp(f'Choose a file extension for the pages ({"/".join(FILE_EXTS)})', key='file_ext', default='png')

    save_store(store)

    # Start downloading the books
    for book_url in book_urls:
        print('')
        print(f'>>> Downloading book: {book_url}')

        try:
            (success, error) = downloadBook(book_url, login_email, login_password, start_page, file_ext)
        except Exception as exception:
            error = type(exception).__name__
            if error == 'KeyboardInterrupt':
                print('')

        # Print error messages
        if error != None:
            print(f'<<< Error: {error}')
        elif success != None:
            print(f'<<< {success}')
    print('')

def main():
    try:
        while True:
            start_download()
            if input('Do you wanna download another book (y/n): ') != 'y':
                break
    except KeyboardInterrupt:
        print('')
        pass

main()
