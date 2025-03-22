import telebot
from logic import DB_Map

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: \n/show_city <город> - показать город на карте\n/remember_city <город> - запомнить город\n/show_my_cities - показать все запомненные города")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    try:
        city_name = ' '.join(message.text.split()[1:])
        if not city_name:
            bot.send_message(message.chat.id, "Пожалуйста, укажите город после команды /show_city.")
            return

        manager = DB_Map('database.db')
        coords = manager.get_coordinates(city_name)
        if coords:
            manager.create_graph('city_map.png', [city_name])
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
        manager = DB_Map('database.db')
        cities = manager.select_cities(message.chat.id)
        if cities:
            manager.create_graph('cities_map.png', cities)
            with open('cities_map.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, 'Вы еще не сохранили ни одного города.')
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

if __name__ == "__main__":
    bot.polling()