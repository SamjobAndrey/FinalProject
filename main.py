import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

bot = telebot.TeleBot("5624995924:AAHP35cOODpjAcHh-0jmf1aDIsXCnqpz1Oc")
url_habr = "https://habr.com/ru/all/"
url_onliner = "https://tech.onliner.by/"
url_kurs = "https://kurs.onliner.by/"
#-----------------1--------------
response_habr = requests.get(url_habr)
response_habr.raise_for_status()
#-----------------2--------------
response_onliner = requests.get(url_onliner)
response_onliner.raise_for_status()

#-----------------1_1---------------
soup_onliner = BeautifulSoup(response_onliner.text, "lxml")
tag_onliner = soup_onliner.find_all("div", class_="news-tidings__list")

#-----------------2_1---------------
soup_habr = BeautifulSoup(response_habr.text, "lxml")
tag_habr = soup_habr.find_all("div", class_="tm-articles-list")
#-----------------3_1-------------
soup_kurs = BeautifulSoup(response_habr.text, "lxml")
tag_kurs = soup_habr.find_all("tr", class_="text-center h4")

#---------------------Основное меню----------------------
@bot.message_handler(commands=["start"])
def start(message):
    stic = open('stic.jpg', 'rb')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_habr = types.KeyboardButton('Новости Habr')
    btn_onl = types.KeyboardButton('Новости Onliner')
    btn_kurs = types.KeyboardButton('Финансы')

    markup.add(btn_habr, btn_onl, btn_kurs)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}! \nЯ новостной бот. Смотри что могу:\n'
                                          '\n1. Вывести последних 5 свежих новостей c сайта Habr\n'
                                          '2. Вывести последних 5 свежих новостей c сайта Onliner\n'
                                          '3. Имеется возможность узнать актуальный курс валют USD\n'
                                          '4. Быстро рассчитать необходимое кол-во денежных средств при операциях покупки/продажи валюты'.format(message.from_user),
                         reply_markup=markup)
    bot.send_sticker(message.chat.id, stic)

@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "Новости Habr"):
        # -----------------------------Парсинг сайта Habr--------------------------------
        response_habr = requests.get(url_habr)
        response_habr.raise_for_status()
        soup_habr = BeautifulSoup(response_habr.text, "lxml")
        tag_habr = soup_habr.find_all("article", class_="tm-articles-list__item")
        for i in range(0, 5):
            title = tag_habr[i].find("h2").find("span").text
            urlOut = "https://habr.com" + tag_habr[i].find("h2").find("a").get("href")
            bot.send_message(message.chat.id, title + ": " + urlOut)
    elif (message.text == "Новости Onliner"):
        # -----------------------------Парсинг сайта Onliner--------------------------------
            response_onliner = requests.get(url_onliner)
            response_onliner.raise_for_status()
            soup_onliner = BeautifulSoup(response_onliner.text, "lxml")
            tag_onliner = soup_onliner.find_all("div", class_="news-tidings__subtitle")
            for i in range(0, 5):
                title = tag_onliner[i].find("a").find("span").text
                print(title)
                urlOut = "https://tech.onliner.by" + tag_onliner[i].find("a").get("href")
                bot.send_message(message.chat.id, title + ": " + urlOut)

    elif (message.text == "Финансы"):
            markup_kurs = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_kurs = types.KeyboardButton('🇺🇸  Курс валют')
            btn_kursUSD = types.KeyboardButton('  Купить USD')
            btn_kursBY = types.KeyboardButton('🇺🇸  Продать USD')
            back = types.KeyboardButton('Назад')
            markup_kurs.add(btn_kurs, btn_kursUSD, btn_kursBY, back)
            bot.send_message(message.chat.id, "Финансы", reply_markup=markup_kurs)
    elif (message.text == "🇺🇸  Курс валют"):
       pars_hml(message)
    elif message.text == 'Продать USD':
        msg = bot.send_message(message.chat.id, 'Введите сумму в долларах')
        bot.register_next_step_handler(msg, calc_usd_pokupka)
    elif message.text == 'Купить USD':
        msg = bot.send_message(message.chat.id, 'Введите сумму в рублях')
        bot.register_next_step_handler(msg, calc_usd_prodaja)
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка! Введите корректные данные')
        bot.register_next_step_handler(msg, func)
    if message.text == 'Назад':
        bot.send_message(message.chat.id, "/start")

def calc_usd_pokupka(message):
    try:
        r = requests.get("https://banki24.by/minsk/kurs/usd").text
        soup = BeautifulSoup(r, 'lxml')
        tag_kurs = soup.find_all("td", align="center")
        print(tag_kurs)
        b = tag_kurs[0].text.rpartition(' / ')[0].replace(',', '.')
        print(b)
        res = float("{0:.2f}".format(float(message.text) * float(b)))
        #res = round(float(message.text) * float(b))
        bot.send_message(message.chat.id, f'У вас получилось на {float(message.text)} долларов США = {res} рублей')
    except ValueError:
        bot.send_message(message.chat.id, 'Введите число')

def calc_usd_prodaja(message):
    try:
        r = requests.get("https://banki24.by/minsk/kurs/usd").text
        soup = BeautifulSoup(r, 'lxml')
        tag_kurs = soup.find_all("td", align="center")
        print(tag_kurs)
        b = tag_kurs[0].text.rpartition(' / ')[2].replace(',', '.')
        print(b)
        #res = float("{0:.2f}".format(float(message.text) / float(b)))
        res = round(float(message.text) / float(b))
        print(res)
        bot.send_message(message.chat.id, f'У вас получилось на {float(message.text)} рублей = {res} доллара США ')
    except ValueError:
        bot.send_message(message.chat.id, 'Введите число')

def pars_hml(message):

    r = requests.get("https://banki24.by/minsk/kurs/usd").text
    soup = BeautifulSoup(r, 'lxml')
    tag_kurs = soup.find_all("td", align="center")
    print(tag_kurs)
    b_usd = tag_kurs[0].text.rpartition(' / ')[0]
    b_usd_1 = tag_kurs[0].text.rpartition(' / ')[2]
    b_eur = tag_kurs[1].text.rpartition(' / ')[0]
    b_eur_1 = tag_kurs[1].text.rpartition(' / ')[2]
    dollar = f'🇺🇸    1 USD   банк покупает    {b_usd}     /     банк продаёт {b_usd_1}'
    euro   = f'🇪🇺    1 EUR   банк покупает     {b_eur}    /    банк продаёт {b_eur_1}'
    b = tag_kurs[0].text.rpartition(' / ')[0]
    print(b)
    bot.send_message(message.chat.id, f'*Курсы валют Нацбанка РБ на сегодня:* \n \n {dollar} \n {euro} \n')
    return b

def pars_hml_new(message):
    r = requests.get("https://banki24.by/minsk/kurs/usd").text
    soup = BeautifulSoup(r, 'lxml')
    tag_kurs = soup.find_all("table", class_="table table-condensed table-striped table-hover")
    print(tag_kurs)
bot.polling(none_stop=True, interval=0)