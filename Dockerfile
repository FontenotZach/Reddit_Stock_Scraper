FROM alpine:latest
RUN apk add --no-cache g++ python3-dev py3-pip postgresql-client postgresql-dev

RUN addgroup -S wsb && adduser -S wsb -G wsb

RUN mkdir /scraper
WORKDIR /scraper

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R wsb:wsb /scraper
RUN chmod u+x /scraper/await_postgres.sh

USER wsb

CMD ["./await_postgres.sh", "python3", "Main.py"]
