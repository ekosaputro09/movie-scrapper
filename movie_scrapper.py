#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs
load_dotenv()


def sent_telegram_chat(message):
    bot_token = os.getenv("BOT_API_KEY")
    chat_id = os.getenv("CHAT_ID")
    apiURL = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chat_id, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)


def movie_scraping():
    print("Starting Movie Scrapper on %s\n" % (datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")))

    # get and parse data from website
    page = 1
    next = True

    session = requests.Session()
    movie_links = []
    while next:
        resp = session.get(os.getenv("MOVIE_URL").format(str(page)))
        doc = bs(resp.text, "html.parser")

        # check pagination
        pagination = doc.find("div", class_="paggingcont")
        pages = pagination.find_all("li")
        pages = [page.text for page in pages]

        # Find the parts containing the movie data
        movies = doc.find_all("div", class_="item movie")

        # Extract all link from the movies
        for movie in movies:
            try:
                title = movie.find("h2")
                link = title.find("a", href=True)
                movie_links.append(link['href'])
            except AttributeError:
                pass

        if "Next" not in pages:
            next = False
        else:
            page += 1

    # extract all movie attributes
    messages = []
    for link in movie_links:
        response = requests.get(link)
        soup = bs(response.text, "html.parser")

        text = "==========================\nMovie\n==========================\n"

        # get title
        title = soup.find("h1")
        text = text + "\nTitle : %s" % title.text.replace("Tayang hari ini", "")

        # attribute
        details_key = soup.find_all("span", class_="sjdl")
        details_value = soup.find_all("span", class_="sisi")
        for key, value in zip(details_key, details_value):
            text = text + "\n%s : %s" % (key.text, value.text)

        # trailer & sinopsis
        try:
            trailer_sinopsis = soup.find_all("div", class_="col-sm-8")[1]
            trailer = trailer_sinopsis.find("iframe", src=True)
            text = text + "\nTrailer : %s" % trailer['src']
        except TypeError:
            try:
                trailer_sinopsis = soup.find_all("div", class_="col-sm-8")[1]
                trailer = trailer_sinopsis.find("source", src=True)
                text = text + "\nTrailer : %s" % trailer['src']
            except TypeError:
                text = text + "\nTrailer : NO TRAILER"

        sinopsis = trailer_sinopsis.find("p")
        text = text + "\nSinopsis : %s" % sinopsis.text

        keterangan = trailer_sinopsis.find("p", class_="hlite")
        text = text + "\n\n" + keterangan.text + "\n"

        text = text + "\n---------------------------\n"

        messages.append(text)

    # print(text)
    return messages

if __name__=="__main__":
    messages = movie_scraping()
    sent_telegram_chat(message="Starting Movie Scrapper on %s\nTotal Movies : %s\n" % (datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), str(len(messages))))
    for message in messages:
        sent_telegram_chat(message=message)