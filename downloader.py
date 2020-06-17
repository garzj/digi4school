import requests
from pathlib import Path
from bs4 import BeautifulSoup
from time import sleep

# get some options from the user
print('')
bookUrl = input('Paste your book url: ')
pageNo = int(input('Start downloading from page (1): ') or 1)

# Starting message
print('')
print('>>> Starting book download...')

# extract a valid bookId from the url
bookId = -1
for tile in bookUrl.split('/'):
    try:
        bookId = int(tile)
    except ValueError:
        pass
if bookId == -1:
    print("<<< Error: The book url you provided seems to be invalid.")
    exit()

# setup directory for the book
bookDir = f'./downloads/book-{bookId}/'
Path(bookDir).mkdir(parents=True, exist_ok=True)

# setup an authorized session for the download (we need to make some requests here to get a valid token)
session = requests.Session()
def getFormData(html):
    form = BeautifulSoup(html, features='lxml').findAll('form')[0]
    formdata = {}
    for field in form:
        if (field.has_attr('name') and field.has_attr('value')):
            formdata[field['name']] = field['value']
    return formdata
r = session.get(f'https://digi4school.at/token/{bookId}')
r = session.post('https://kat.digi4school.at/lti', data=getFormData(r.content))
r = session.post('https://a.digi4school.at/lti', data=getFormData(r.content))

# loop as long as a valid pages are found
ddosMessageShown = False
lastWasPage = True
while lastWasPage:
    try:
        # download the page
        pageSvgUrl = f'https://a.digi4school.at/ebook/{bookId}/1/{pageNo}/{pageNo}.svg'
        r = session.get(pageSvgUrl)
        lastWasPage = (r.status_code == 200 and 'image/svg' in r.headers['content-type'])
        if lastWasPage:
            filePath = f'./{bookDir}/page-{pageNo}.svg'
            with open(filePath, 'wb') as f:
                f.write(r.content)
                print(f'Downloaded page {pageNo}.')
                pageNo += 1
    except requests.exceptions.RequestException as e:
        # handle DDOS protection errors
        if not ddosMessageShown:
            print("")
            print("Oops! Looks like have been temporarily blocked by the digi4school server's DDOS protection.")
            print("This normally happens when you send too many requests (download large books).")
            print("")
            print(f"If you want to try it again later, here's the next page to be downloaded: {pageNo}")
            print("")
            print("The thread will automatically retry every 10 seconds ...")
            print("")
            ddosMessageShown = True
        else:
            print("Error, retrying...")
        sleep(10)

# Success message
print(f'<<< Downloaded {pageNo - 1} pages.')