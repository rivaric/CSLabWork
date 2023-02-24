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
week = 'ch' if round(delta.days / 7) % 2 == 0 else 'nch'
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
    bot.send_message(message.chat.id, 'Привет! Я ')


@bot.message_handler(commands=['week'])
def return_num_week(message):
    bot.send_message(message.chat.id, f'Неделя: №{num_week}, {"чётная" if week == "ch" else "нечётная"}')


@bot.message_handler(commands=['mtuci'])
def return_mtuci_link(message):
    bot.send_message(message.chat.id, 'Официальный сайт МТУСИ - https://mtuci.ru/')


@bot.message_handler(content_types=['text'])
def answer(message, week=week):
    if message.text.lower() == "help":
        start_message(message)
    elif message.text.lower() == "понедельник":
        message_day_schedule('Понедельник', message)
    elif message.text.lower() == "вторник":
        message_day_schedule('Вторник', message)
    elif message.text.lower() == "среда":
        message_day_schedule('Среда', message)
    elif message.text.lower() == "четверг":
        message_day_schedule('Четверг', message)
    elif message.text.lower() == "пятница":
        message_day_schedule('Пятница', message)
    elif message.text.lower() == "суббота":
        message_day_schedule('Суббота', message)
    elif message.text.lower() == "расписание на текущую неделю":
        res_str = f'Неделя: №{num_week}, {"чётная" if week == "ch" else "нечётная"}\n'
        for i in range(7):
            res_str += form_day(weekday_dict[i], day_sql_query(weekday_dict[i]))
        bot.send_message(message.chat.id, res_str)
    elif message.text.lower() == "расписание на следущую неделю":
        res_str = f'Неделя: №{num_week + 1}, {"нечётная" if week == "ch" else "чётная"}\n'
        for i in range(7):
            res_str += form_day(weekday_dict[i], day_sql_query(weekday_dict[i], 'nch' if week == 'ch' else 'ch'))
        bot.send_message(message.chat.id, res_str)
    elif message.text.lower() == "сегодня":
        message_day_schedule(weekday_dict[weekday], message)
    elif message.text.lower() == "завтра":
        message_day_schedule(weekday_dict[weekday + 1], message)
    else:
        bot.send_message(message.chat.id, 'Извините, я вас не понимать')


bot.polling(none_stop=True)