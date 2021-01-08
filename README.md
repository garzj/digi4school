# digi4school-downloader

Download your books from https://digi4school.at!

## Requirements

- Docker

## Usage

1. Just run one command to start the program
   - On Windows: `docker run -it -v "%cd%\data:/app/data" --name digi4school-downloader --rm garzj/digi4school-downloader`
   - On Linux / MacOS: `docker run -it -v "$pwd/data:/app/data" --name digi4school-downloader --rm garzj/digi4school-downloader`
2. Follow the steps
3. Your book gets saved into the folder ./data/downloads/

### Obtaining the book url

- Login to `https://digi4school.at/` in your browser
- Search your book
- Right click it and choose 'Copy link address'

**Important:** You'll need the url that leads to the book, not the url of the opened book itself.
