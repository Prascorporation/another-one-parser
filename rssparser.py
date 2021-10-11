import feedparser
import re
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
import requests
newsline = feedparser.parse("http://www.kspu.edu/RssAggregator.ashx?id=1484")
finder = r'\/FileDownload.+/>'
finder2 = r'\?id=.{8}-.{4}-.{4}-.{4}-.{13}'
newscards = newsline.entries
# soup = BeautifulSoup(data, "html.parser")
cluster = MongoClient('mongodb+srv://yourlogin:yourpassword@cluster0.47q9x.mongodb.net/ksu24?retryWrites=true&w=majority')
db = cluster.ksu24
collection = db.newscards  # name of collection in mongo!


def get_image(newscard):
    stepOne = newscard.description
    stepTwo = re.findall(finder, stepOne)
    stepThree = ''.join(stepTwo)
    stepFour = re.findall(finder2, stepThree)
    stepFive = ''.join(stepFour)[0:-1]
    stepSix = "http://www.kspu.edu/FileDownload.ashx" + stepFive
    img_data = requests.get(stepSix).content
    stepSeven = "images/"+stepFive[1:] + ".jpg"
    with open(stepSeven, 'wb') as handler:
        handler.write(img_data)
    stepEight = "C:/parser/" + stepSeven
    return stepEight


def get_title(newscard):
    return newscard.title


def get_text(newscard):
    stepOne = newscard.description
    stepTwo = ''.join(stepOne)
    soup = BeautifulSoup(stepTwo, 'html.parser')
    stepThree = soup.find('strong').get_text()
    stepFour = stepThree.replace("\xa0", "")
    return stepFour


def clear_text(text):  # use this function only if you use feedparser
    re1 = text.replace("&ndash;", " - ")
    re2 = re1.replace("&laquo;", "«")
    re3 = re2.replace("&raquo;", "»")
    re4 = re3.replace("&nbsp;", "")
    return re4


def get_link(newscard):
    return newscard.link


def fill_base(): #use this function only once if you need to populate database
    items = []
    for i in newscards:
        getItem(i)
        items.append({
            "title": get_title(i),
            "img": get_image(i),
            "text": get_text(i),
            "link": get_link(i)
        })
    for i in items:
        print(i)
    collection.insert_many(items)


#fill_base() #use this function only once if you need to populate database

while True:
    try:
        i = newscards[0]
        item = {
            "title": get_title(i),
            "img": get_image(i),
            "text": get_text(i),
            "link": get_link(i)
        }
        print(item["link"], " - last item in rss")
        current_news = collection.find().sort('_id', -1).limit(1)[0]['link'];
        print(current_news, " - last item in mongo ")
        print(item)
        if item["link"] != current_news:
            collection.insert_one(item)
            print("new news added to the database")
        time.sleep(120)
    except IndexError:
        print("Timeout exceeded. repeated request after 2 minutes")

    time.sleep(120)
