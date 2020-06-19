import requests
from pathlib import Path
from bs4 import BeautifulSoup
from time import sleep
import cairosvg_

# get some options from the user
print('')
bookUrl = input('Paste your book url: ')
startPageNo = int(input('Start downloading from page (default => 1): ') or 1)
pageFileExtension = input('Choose a file extension for the pages: png/pdf/ps/svg (default => png): ') or 'png'

# Starting message
print('')
print('>>> Starting book download...')

# extract a valid bookId from the url
bookIds = []
for tile in bookUrl.split('/'):
    try:
        id = int(tile)
        bookIds.append(id)
    except ValueError:
        pass
if len(bookIds) == 0:
    print("<<< Error: The book url you provided seems to be invalid.")
    exit()

# extrace the book suburl from the given ids
bookSubUrl = ''
for bookId in bookIds:
   bookSubUrl += '/' + str(bookId)

# setup an authorized session for the download (we need to make some requests here to get a valid token)
try:
    session = requests.Session()
    def getFormData(html):
        form = BeautifulSoup(html, features='lxml').findAll('form')[0]
        formdata = {}
        for field in form:
            if (field.has_attr('name') and field.has_attr('value')):
                formdata[field['name']] = field['value']
        return formdata
    r = session.get(f'https://digi4school.at/token/{bookIds[0]}')
    r = session.post('https://kat.digi4school.at/lti', data=getFormData(r.content))
    r = session.post('https://a.digi4school.at/lti', data=getFormData(r.content))
except IndexError:
    print("<<< Error: The book url you provided seems to be invalid.")
    exit()

# mkdir a directory for the book
if len(bookIds) == 1:
    bookDir = f'./downloads/book-{bookIds[0]}/'
elif len(bookIds) == 2:
    bookDir = f'./downloads/archive-{bookIds[0]}/book-{bookIds[1]}/'
else:
    bookDir = f'./downloads{bookSubUrl}/'
Path(bookDir).mkdir(parents=True, exist_ok=True)

# go on and keep downloading the pages ´til there's a 404
pageNo = startPageNo
while True:
    # download the page, convert it to the given file extension
    pageSvgUrl = f'https://a.digi4school.at/ebook{bookSubUrl}/{pageNo}/{pageNo}.svg'
    fileSavePath = f'./{bookDir}/page-{pageNo}.{pageFileExtension}'
    try:
        if pageFileExtension in cairosvg_.svg2:
            cairosvg_.svg2[pageFileExtension](url=pageSvgUrl, write_to=fileSavePath, session=session, fillBG=True)
            print(f'Downloaded page {pageNo}.')
            pageNo += 1
        else:
            print("<<< Error: Please enter a valid file extension.")
            exit()
            break
    except cairosvg_.exceptions.NotFoundException:
        # 404 -> we're done
        break

# Done message
print(f'<<< Downloaded {pageNo - startPageNo} pages.')