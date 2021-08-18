FROM amancevice/pandas:1.3.1-alpine
RUN apk add --no-cache python3-dev py3-pip g++ gcc make postgresql-libs postgresql-dev

RUN addgroup -S wsb && adduser -S wsb -G wsb

RUN mkdir /scraper
WORKDIR /scraper

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN chown -R wsb:wsb /scraper

USER wsb

CMD ["python3", "WSB_Scraper.py"]
