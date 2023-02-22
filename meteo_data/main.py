import requests

city = "Moscow, RU"
appid = "64e2e222a3b65cd50d3341bb13e366ba"

res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                   params={'q': city, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
data = res.json()

print("Город:", city)
print("Погодные условия:", data['weather'][0]['description'])
print("Температура:", data['main']['temp'])
print("Минимальная температура:", data['main']['temp_min'])
print("Максимальная температура", data['main']['temp_max'])
print("Видимость:", data['visibility'], 'm')
print("Скорость ветра:", data['wind']['speed'])
print("____________________________")

res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                   params={'q': city, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
data = res.json()
print("Прогноз погоды на неделю:")
for i in data['list']:
        print("Дата <", i['dt_txt'], "> "
              "\r\nТемпература <", '{0:+3.0f}'.format(i['main']['temp']), "> "
              "\r\nПогодные условия <", i['weather'][0]['description'], ">",
              "\r\nВидимость <", i['visibility'], '>',
              "\r\nСкорость ветра:", i['wind']['speed'])
print("____________________________")