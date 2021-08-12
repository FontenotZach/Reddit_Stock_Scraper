FROM amancevice/pandas:1.3.1-alpine
RUN apk add --no-cache python3 python3-dev python3-tkinter py3-pip git screen g++ gcc make

RUN addgroup -S wsb && adduser -S wsb -G wsb

RUN mkdir /scraper
WORKDIR /scraper

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN mkdir -p Log
RUN chown -R wsb:wsb /scraper

USER wsb

CMD ["python3", "WSB_Scraper.py"]
