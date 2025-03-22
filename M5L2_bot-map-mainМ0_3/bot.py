import telebot
from logic import DB_Map

TOKEN = '7879294822:AAGfPSh7Dn40b7qyTNFxytfK-GkMTqv3a1w'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: \n"
                     "/show_city <город> [цвет] - показать город на карте (цвет маркера опционально)\n"
                     "/remember_city <город> - запомнить город\n"
                     "/show_my_cities [цвет] - показать все запомненные города (цвет маркера опционально)\n"
                     "/show_country <страна> - показать города в указанной стране\n"
                     "/show_density <плотность> - показать города с плотностью населения выше указанной\n"
                     "/show_country_density <страна> <плотность> - показать города в стране с плотностью выше указанной\n"
                     "/weather <город> - показать погоду в городе\n"
                     "/time <город> - показать местное время в городе")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите город после команды /show_city.")
            return

        city_name = ' '.join(parts[1:-1]) if len(parts) > 2 else parts[1]
        marker_color = parts[-1] if len(parts) > 2 else 'red'  # Цвет по умолчанию — красный

        manager = DB_Map('database.db')
        coords = manager.get_coordinates(city_name)
        if coords:
            manager.create_graph('city_map.png', [city_name], marker_color=marker_color)
            with open('city_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, 'Город не найден. Убедись, что он написан на английском!')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    try:
        user_id = message.chat.id
        city_name = ' '.join(message.text.split()[1:])
        if not city_name:
            bot.send_message(message.chat.id, "Пожалуйста, укажите город после команды /remember_city.")
            return

        manager = DB_Map('database.db')
        if manager.add_city(user_id, city_name):
            bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
        else:
            bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    try:
        parts = message.text.split()
        marker_color = parts[-1] if len(parts) > 1 else 'red'  # Цвет по умолчанию — красный

        manager = DB_Map('database.db')
        cities = manager.select_cities(message.chat.id)
        if cities:
            manager.create_graph('cities_map.png', cities, marker_color=marker_color)
            with open('cities_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, 'Вы еще не сохранили ни одного города.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['show_country'])
def handle_show_country(message):
    try:
        country = ' '.join(message.text.split()[1:])
        if not country:
            bot.send_message(message.chat.id, "Пожалуйста, укажите страну после команды /show_country.")
            return

        manager = DB_Map('database.db')
        cities = manager.get_cities_by_country(country)
        if cities:
            manager.create_graph('country_map.png', cities)
            with open('country_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, 'Города в указанной стране не найдены.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['show_density'])
def handle_show_density(message):
    try:
        min_density = float(message.text.split()[1])
        manager = DB_Map('database.db')
        cities = manager.get_cities_by_population_density(min_density)
        if cities:
            manager.create_graph('density_map.png', cities)
            with open('density_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, 'Города с указанной плотностью населения не найдены.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['show_country_density'])
def handle_show_country_density(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, "Пожалуйста, укажите страну и плотность населения после команды /show_country_density.")
            return

        country = ' '.join(parts[1:-1])
        min_density = float(parts[-1])
        manager = DB_Map('database.db')
        cities = manager.get_cities_by_country_and_population_density(country, min_density)
        if cities:
            manager.create_graph('country_density_map.png', cities)
            with open('country_density_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, 'Города в указанной стране с указанной плотностью населения не найдены.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['weather'])
def handle_weather(message):
    try:
        city_name = ' '.join(message.text.split()[1:])
        if not city_name:
            bot.send_message(message.chat.id, "Пожалуйста, укажите город после команды /weather.")
            return

        manager = DB_Map('database.db')
        weather_info = manager.get_weather(city_name)
        if weather_info:
            bot.send_message(message.chat.id, weather_info)
        else:
            bot.send_message(message.chat.id, 'Не удалось получить данные о погоде. Проверьте название города.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['time'])
def handle_time(message):
    try:
        city_name = ' '.join(message.text.split()[1:])
        if not city_name:
            bot.send_message(message.chat.id, "Пожалуйста, укажите город после команды /time.")
            return

        manager = DB_Map('database.db')
        time_info = manager.get_local_time(city_name)
        if time_info:
            bot.send_message(message.chat.id, time_info)
        else:
            bot.send_message(message.chat.id, 'Не удалось получить данные о времени.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

if __name__ == "__main__":
    bot.polling()