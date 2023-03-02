import math

import telebot
from telebot import types
from datetime import date
import psycopg2

# Подключение самого бота с помощью токена
token = '5922817225:AAFYz53w78FdWBZguCtMAOA1UhVR5DSK7QM'
bot = telebot.TeleBot(token)

# Поделючение к базе данных
conn = psycopg2.connect(
    database="schedule_db",
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

# Получение текущей даты для вычисления текущей недели и получение текущего дня недели
start_training = date(2023, 1, 30)
current_date = date.today()
weekday = current_date.weekday()
delta = current_date - start_training
week = 'ch' if math.ceil(delta.days / 7) % 2 == 0 else 'nch'
num_week = round(delta.days / 7)

# Словарь для перевода числа в день недели
weekday_dict = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота',
                6: 'Воскресенье'}


# Вывод расипсания по предмету
def get_subject(i, subject, room, stime, etime, teacher):
    return f'{i}. <{subject}> <{room} Каб.> <{str(stime)[:-3]} - {str(etime)[:-3]}> <{teacher}> \n'


def day_sql_query(day, week_f=week):
    cursor.execute(
        "SELECT day, timetable.subject, room_numb, start_time, end_time, evenness, teacher.full_name " \
        "FROM timetable INNER JOIN teacher ON teacher.subject = timetable.subject " \
        "WHERE day = %s AND evenness = %s " \
        "ORDER BY start_time ASC", (day, week_f))

    records = list(cursor.fetchall())

    return records


def form_day(day, res_list):
    res_str = f'{day}: \n' \
              '---------------------- \n'
    if res_list:
        for i in range(len(res_list)):
            res_str += get_subject(i + 1, res_list[i][1], res_list[i][2], res_list[i][3], res_list[i][4],
                                   res_list[i][6])
    else:
        res_str += 'Занятий нет!\n'
    res_str += '---------------------- \n'

    return res_str


def form_week(week_list):
    week_str = ''
    for day in week_list:
        week_str += form_day(day, day[0])

    return week_str


def message_day_schedule(day, message):
    bot.send_message(message.chat.id, form_day(day, day_sql_query(day)))


def message_week_schedule(toggle, message):
    global week
    if toggle == 'cur':
        res_str = f'Неделя: №{num_week}, {"чётная" if week == "ch" else "нечётная"}\n'
    elif toggle == 'next':
        week = 'nch' if week == 'ch' else 'ch'
        res_str = f'Неделя: №{num_week + 1}, {"нечётная" if week == "ch" else "чётная"}\n'

    for i in range(6):
        res_str += form_day(weekday_dict[i], day_sql_query(weekday_dict[i], week))

    bot.send_message(message.chat.id, res_str)


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Help", "Сегодня", "Завтра")
    keyboard.row("Понедельник", "Вторник", "Среда")
    keyboard.row("Четверг", "Пятница", "Суббота")
    keyboard.row("Расписание на текущую неделю", "Расписание на следущую неделю")
    bot.send_message(message.chat.id, 'Привет хочешь узнать своё расписание? \n'
                                      'Чтобы узнать полный перечень команд введите /help',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Я создан для того, чтобы показывать расписание твоих занятий.'
                                      'Под стракой ввода находятся кнопки с текстом, пользуйся ими для эффективного'
                                      'и быстрого использования бота, однако есть другой вариант - команды:\n'
                                      '\n'
                                      '/start - запуск приложения\n'
                                      '/help - список команд\n'
                                      '/mondey - расписание на понедельник\n'
                                      '/tuesday - расписание на вторник\n'
                                      '/wednesday - расписание на среду\n'
                                      '/thursday - расписание на четверг\n'
                                      '/friday - расписание на пятницу\n'
                                      '/satuday - расписание на субботу\n'  
                                      '/nextweek - расписание на следующую неделю\n'  
                                      '/thisweek - расписание на текущую неделю\n'
                                      '/today - расписание на сегодня\n'
                                      '/tomorrow - расписание на завтра\n'
                                      '/week - какая сейчас неделя\n'
                                      '/mtuci - ссылка на сайт МТУСИ\n')


@bot.message_handler(commands=['week'])
def message_num_week(message):
    bot.send_message(message.chat.id, f'Неделя: №{num_week}, {"чётная" if week == "ch" else "нечётная"}')


@bot.message_handler(commands=['mtuci'])
def message_mtuci_link(message):
    bot.send_message(message.chat.id, 'Официальный сайт МТУСИ - https://mtuci.ru/')


@bot.message_handler(commands=['today'])
def today_schedule(message):
    message_day_schedule(weekday_dict[weekday], message)


@bot.message_handler(commands=['tomorrow'])
def tomorrow_schedule(message):
    message_day_schedule(weekday_dict[weekday + 1], message)


@bot.message_handler(commands=['currentweek'])
def current_week(message):
    message_week_schedule('cur', message)


@bot.message_handler(commands=['nextweek'])
def next_week(message):
    message_week_schedule('next', message)


@bot.message_handler(commands=['monday'])
def monday_schedule(message):
    message_day_schedule('Понедельник', message)


@bot.message_handler(commands=['tuesday'])
def tuesday_schedule(message):
    message_day_schedule('Вторник', message)


@bot.message_handler(commands=['wednesday'])
def wednesday_schedule(message):
    message_day_schedule('Среда', message)


@bot.message_handler(commands=['thursday'])
def thursday_schedule(message):
    message_day_schedule('Четверг', message)


@bot.message_handler(commands=['friday'])
def friday_schedule(message):
    message_day_schedule('Пятница', message)


@bot.message_handler(commands=['satuday'])
def satuday_schedule(message):
    message_day_schedule('Суббота', message)


@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text.lower() == "help":
        start_message(message)
    elif message.text.lower() == "понедельник":
        monday_schedule(message)
    elif message.text.lower() == "вторник":
        tuesday_schedule(message)
    elif message.text.lower() == "среда":
        wednesday_schedule(message)
    elif message.text.lower() == "четверг":
        thursday_schedule(message)
    elif message.text.lower() == "пятница":
        friday_schedule(message)
    elif message.text.lower() == "суббота":
        satuday_schedule(message)
    elif message.text.lower() == "расписание на текущую неделю":
        current_week(message)
    elif message.text.lower() == "расписание на следущую неделю":
        next_week(message)
    elif message.text.lower() == "сегодня":
        today_schedule(message)
    elif message.text.lower() == "завтра":
        tomorrow_schedule(message)
    else:
        bot.send_message(message.chat.id, 'Извините, я вас не понимаю')


bot.polling(none_stop=True)