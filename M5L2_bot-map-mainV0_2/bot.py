import telebot
from logic import DB_Map

TOKEN = '7879294822:AAFKARnaFJs2WTO9p5utSikSKHpmG_JymwI'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: \n"
                     "/show_city <город> [цвет] - показать город на карте (цвет маркера опционально)\n"
                     "/remember_city <город> - запомнить город\n"
                     "/show_my_cities [цвет] - показать все запомненные города (цвет маркера опционально)")

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

if __name__ == "__main__":
    bot.polling()