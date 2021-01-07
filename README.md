# digi4school

Downloads your books from https://digi4school.at.

## Installation

### Windows

- Download and install [Python 3](https://www.python.org/downloads/windows/)
- Download and install GTK+ [from here](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/)
- `pip3 install requests cairosvg bs4`

### Ubuntu

- `sudo apt install python3.8 libcairo2-dev`
- `pip3 install requests cairosvg bs4`

### Mac OS X

- `sudo brew install python@3.8 cairo pango`
- `pip3 install requests cairosvg bs4`

## Usage

First clone this directory and head into its folder.

Then go through the following steps to download your book.

### Getting the book url

- Login to `https://digi4school.at/` in your browser
- Choose your book
- Open it up
- Copy its URL

### Actual book download

- `py downloader.py`
- Paste the book url (or multiple urls seperated by a semicolon)
- Enter the credentials to your digi4school account
- Customize a few options
- The book gets downloaded and saved into a folder named 'downloads'

**Note:** It may take a little longer to download the first page.
