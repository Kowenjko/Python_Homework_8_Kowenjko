"""
Додати кнопки з вибором дня

Вивести інформацію:
макс темп
мін темп
поточну темп
вологість
сила і напрямок вітру
опис
попередження, якщо є

Прикріпити посилання на телеграм бота у файл readme.txt 

Як виконане завдання надіслати посилання на репозиторій з проектом
"""


import telebot
import config

from bs4 import BeautifulSoup
import requests

bot = telebot.TeleBot(config.TOKEN)
send_city = 'рівне'
direction = {
    'Південний': '⬆️',
    'Північний': '⬇️',
    'Східний': '⬅️',
    'Західний': '➡️',
    'Південно-східний': '↖️',
    'Південно-західний': '↗️',
    'Північно-східний': '↙️',
    'Північно-західний': '↘️',
    'Штиль': '⏺',
}

# --------------загрузка погоди-----------------------------------


def loadWather(url):
    request = requests.get(url)
    html = BeautifulSoup(request.content, 'html.parser')
    if request.status_code == 200:
        return html
    else:
        html = None
        return html
# -------------функція для виводу погоди для кнопок------------------------------------


def weatherOneDay(message, id_day, class_send, url):

    wather = loadWather(url)
    if wather == None:
        bot.send_message(message, 'Не знаю такого міста')
    else:
        tabsTop = wather.find('div', id=id_day)
        tbody = tabsTop.find('tbody')
        td = tbody.find_all('td', class_=class_send)

        wint = td[6].find('div', class_='wind').get(
            'data-tooltip').split(',')[0]

        city = wather.find('div', class_='cityName').find(
            'h1').find('strong').text

        min_temp = wather.select_one('.temperature .min').text.strip()
        max_temp = wather.select_one('.temperature .max').text.strip()
        desc = wather.select_one('.wDescription .description').text.strip()

        if id_day == 'bd1c':
            time = wather.select_one('.lSide .today-time').text.strip()
            info = time
        else:
            if class_send == 'p5':
                info = 'Погода o 12:00 '
            if class_send == 'p3':
                info = 'Погода o 15:00 '
        denger1 = 'Немає даних'
        denger2 = 'Немає даних'
        if wather.find('div', class_='oWarnings'):
            denger = wather.find('div', class_='oWarnings').find_all(
                'div', class_='description')
            if len(denger) == 1:
                denger1 = denger[0].text
            else:
                denger1 = denger[0].text
                denger2 = denger[1].text

        bot.send_message(
            message, f'🕒{info} - {city}\n🌡️{min_temp}\n🌡️{max_temp}\n\
            Вітер:{direction[wint]} - {td[6].text} м/с\n\
            Тиск- {td[4].text} мм \n\
            💧 - {td[5].text} %\
            🌧 - {td[7].text} %\
            \n📑{desc} \
            \n⚠️{denger1} \
            \n‼️{denger2} ')

# -------------------Загрузка при старті------------------------------


@bot.message_handler(commands=['start'])
def main(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/start', '/bottons', '/help')
    url = f'https://ua.sinoptik.ua/погода-{send_city}'
    bot.send_message(message.chat.id, text='Привіт.', reply_markup=keyboard)
    weatherOneDay(message.chat.id, 'bd1c', 'cur', url)
# --------------------Робота кнопок----------------------------------------


@bot.message_handler(commands=['bottons'])
def bottons(message):

    tabsWeather = []
    tabsImage = []

    tabBotton = []
    url = f'https://ua.sinoptik.ua/погода-{send_city}'
    tabs = loadWather(url).find('div', 'tabs')
    tab = tabs.find_all('div')
# -----------------------------------------------
    for i in range(0, len(tab)):
        if tab[i].get('id') == None:
            continue
        tabsWeather.append(tab[i].get('id'))
        if tab[i].find('img') == None:
            continue
        tabsImage.append(tab[i].find('img').get('src')[2:])
        tabsDay = []
        if tab[i].select_one('.date'):
            tabsDay.append(tab[i].select_one('.day-link').text)
            tabsDay.append(tab[i].select_one('.date').text)
            tabsDay.append(tab[i].select_one('.month').text)
        if tabsDay:
            tabBotton.append(tabsDay)
# -----------------------------------------------
    # bot.send_photo(message.from_user.id,tabsImage[0])

    markup = telebot.types.InlineKeyboardMarkup()
    for i in range(0, len(tabBotton)):
        markup.add(telebot.types.InlineKeyboardButton(
            text=f"{' '.join(tabBotton[i])}", callback_data=f'{tabsWeather[i]}'))

    bot.send_message(
        message.chat.id, text='Виберіть погоду на конкретний день', reply_markup=markup)
# ----------------Виконуємо дію кнопок----------------------


@ bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(
        callback_query_id=call.id, text="You check some button!")
    url = f'https://ua.sinoptik.ua/погода-{send_city}'

    tabs = loadWather(url).find('div', 'tabs')
    tab = tabs.find_all('div')

    arr_link = []
    for i in range(0, len(tab)):
        if tab[i].find('a', class_='day-link'):
            arr_link.append(tab[i].find(
                'a', class_='day-link').get('data-link'))

    if call.data == 'bd1':
        url = f'https://ua.sinoptik.ua/погода-{send_city}'

        weatherOneDay(call.message.chat.id, 'bd1c', 'cur', url)
    elif call.data == 'bd2':
        weatherOneDay(call.message.chat.id, 'bd2c',
                      'p5', 'https:'+arr_link[0])
    elif call.data == 'bd3':
        weatherOneDay(call.message.chat.id, 'bd3c',
                      'p3', 'https:'+arr_link[1])
    elif call.data == 'bd4':
        weatherOneDay(call.message.chat.id, 'bd4c',
                      'p3', 'https:'+arr_link[2])
    elif call.data == 'bd5':
        weatherOneDay(call.message.chat.id, 'bd5c',
                      'p3', 'https:'+arr_link[3])
    elif call.data == 'bd6':
        weatherOneDay(call.message.chat.id, 'bd6c',
                      'p3', 'https:'+arr_link[4])
    elif call.data == 'bd7':
        weatherOneDay(call.message.chat.id, 'bd7c',
                      'p3', 'https:'+arr_link[5])

    # bot.send_message(call.message.chat.id, answer)
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id)
# -------------Допомога---------------------------


@ bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(
        message.chat.id, 'Бот виводить інформацію про погоду на 7 днів, також можете ввести по назві населеного пункту')

# ----------------Виводимо по назві населеного пункта-------------------------------


@bot.message_handler(content_types=['text'])
def send_text(message):

    url = f'https://ua.sinoptik.ua/погода-{message.text.lower()}'
    bot.send_message(message.chat.id, message.text.lower())
    weatherOneDay(message.chat.id, 'bd1c', 'cur', url)


bot.polling()
# driver.close()
