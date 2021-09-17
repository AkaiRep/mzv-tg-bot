# -*- coding: utf-8 -*-
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import time
from time import sleep
import dateutil.parser as dparser
from datetime import datetime, tzinfo
import os
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(os.environ.get('BOT_KEY'), parse_mode="HTML")


url1 = "https://www.mzv.cz/moscow/ru/vizy_i_konsulskaja/novosti"

class last_article:
    header = "header 1"
    text = "text 1"
    data = ""
    def store_if_fresh(self, newheader,newtext,newdata):
        if newheader != self.header:
            self.header = newheader
            self.text = newtext
            self.data = newdata
            return True
        return False



while True:
    i = 1
    datas = []
    sorted_dates = []
    response = requests.get(url1)
    soup = BeautifulSoup(response.text, 'html5lib')
    items = soup.find_all('div', class_='article_content')
    while i<len(items): #sorting and parsing dates
        try:
            data = dparser.parse(items[i].find('span', class_='time').text.replace("\n",""),fuzzy=True,dayfirst=True)
            if len(list(str(data.hour))) == 2 and len(list(str(data.minute))) == 2:
                datas.append(str(data.day)+"-"+str(data.month)+"-"+str(data.year)+" "+str(data.hour)+":"+str(data.minute))
            else:
                if len(list(str(data.hour))) == 1 and len(list(str(data.minute))) != 1:
                    datas.append(str(data.day)+"-"+str(data.month)+"-"+str(data.year)+" 0"+str(data.hour)+":"+str(data.minute))
                elif len(list(str(data.hour))) != 1 and len(list(str(data.minute))) == 1:
                    datas.append(str(data.day)+"-"+str(data.month)+"-"+str(data.year)+" "+str(data.hour)+":0"+str(data.minute))
                else:
                    datas.append(str(data.day)+"-"+str(data.month)+"-"+str(data.year)+" 0"+str(data.hour)+":0"+str(data.minute))
        except AttributeError:
            datas.append("none")
        i+=1
    
    sorted_dates = list(datas)
    sorted_dates.sort(key=lambda date: datetime.strptime(date, "%d-%m-%Y %H:%M"))
    newdata = sorted_dates[19]
    number = datas.index(newdata)+1
    header = items[number].find('h2', class_='article_title').text
    href = items[number].find('a').get('href')
    try:
        text = items[number].find("p", class_='article_perex').text
    except AttributeError:
        text = ""
    
    if last_article.store_if_fresh(last_article, header ,text, newdata):
        bot.send_message(os.environ.get('CHAT_ID'),"<b>"+last_article.header+"</b> \n"+last_article.text+"\n",reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text='Прочитать', url="mzv.cz"+href)]]))
        print("["+time.asctime()+"] Actual!")
    else:
        print("["+time.asctime()+"] Not actual :(")
    sleep(5)

