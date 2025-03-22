import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import requests
from datetime import datetime

class DB_Map:
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id INTEGER,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return True
            else:
                return False

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def get_cities_by_country(self, country):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT city 
                            FROM cities  
                            WHERE country = ?''', (country,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_cities_by_population_density(self, min_density):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT city 
                            FROM cities  
                            WHERE population_density >= ?''', (min_density,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_cities_by_country_and_population_density(self, country, min_density):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT city 
                            FROM cities  
                            WHERE country = ? AND population_density >= ?''', (country, min_density))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def create_graph(self, path, cities, marker_color='red'):
        plt.figure(figsize=(15, 10))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Заливка континентов и океанов
        ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')  # Заливка континентов
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')  # Заливка океанов
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
        ax.gridlines(draw_labels=True)  # Добавляем сетку с подписями

        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lng = coords
                ax.plot(lng, lat, 'o', markersize=10, color=marker_color, transform=ccrs.PlateCarree())  # Используем выбранный цвет
                ax.text(lng + 1, lat, city, fontsize=12, transform=ccrs.PlateCarree(), color='blue')

        plt.savefig(path, dpi=300)
        plt.close()

    def get_weather(self, city_name):
        coords = self.get_coordinates(city_name)
        if not coords:
            return None
        lat, lng = coords
        api_key = ""  # Замените на ваш API-ключ
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            return f"Погода в {city_name}: {weather}, температура: {temp}°C"
        else:
            return None

    def get_local_time(self, city_name):
        coords = self.get_coordinates(city_name)
        if not coords:
            return None
        lat, lng = coords
        api_key = ""  # Замените на ваш API-ключ
        url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={api_key}&format=json&by=position&lat={lat}&lng={lng}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            local_time = datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            return f"Местное время в {city_name}: {local_time}"
        else:
            return None

if __name__ == "__main__":
    m = DB_Map('database.db')
    m.create_user_table()