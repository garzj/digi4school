FROM python:3.8-rc-alpine AS lxml-builder

RUN apk add --no-cache g++
RUN apk add --no-cache libxml2-dev libxslt-dev
RUN pip3 install --user --no-cache-dir lxml==4.5.*


FROM python:3.8-rc-alpine

WORKDIR /app

# Lxml
RUN apk add --no-cache libxml2 libxslt
COPY --from=lxml-builder /root/.local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/

# Cairo SVG
RUN apk add --no-cache \
        build-base cairo-dev cairo cairo-tools \
        jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev && \
    pip3 install flask==1.0.1 cairosvg==2.1.3

# Other packages
RUN pip3 install requests bs4

COPY ./ ./

CMD ["python3", "downloader.py"]
