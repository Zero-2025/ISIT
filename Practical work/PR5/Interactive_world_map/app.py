import tkinter as tk
from tkinter import ttk
import tkintermapview
import requests
from geopy.geocoders import Nominatim
from PIL import Image, ImageTk
from io import BytesIO

class WorldMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("World Map Country Information")
        self.root.geometry("1000x700")

        # Настройка геокодера (для получения страны по координатам)
        self.geolocator = Nominatim(user_agent="world_map_app")

        # 1. Инициализация карты
        self.map_widget = tkintermapview.TkinterMapView(self.root, width=1000, height=700, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)

        # Установка начального вида (Европа/Россия)
        self.map_widget.set_position(55.75, 37.62)  # Москва
        self.map_widget.set_zoom(4)

        # Размещение начальных маркеров (Пример: Россия, Польша, Испания, Италия, Пакистан)
        self.add_initial_markers()

        # Вариант Б: Правый клик на карте
        self.map_widget.add_right_click_menu_command(label="Получить информацию о стране",
                                                    command=self.get_info_by_coords,
                                                    pass_coords=True)

    def add_initial_markers(self):
        """Размещение маркеров для ключевых стран"""
        countries = [
            {"name": "Russia", "pos": (55.75, 37.62)},
            {"name": "Poland", "pos": (52.23, 21.01)},
            {"name": "Spain", "pos": (40.41, -3.70)},
            {"name": "Italy", "pos": (41.89, 12.49)},
            {"name": "Pakistan", "pos": (33.68, 73.04)}
        ]
        
        for c in countries:
            self.map_widget.set_marker(c["pos"][0], c["pos"][1], text=c["name"], 
                                       command=self.on_marker_click)

    def on_marker_click(self, marker):
        """Вариант А: Клик по маркеру"""
        self.fetch_and_show_country_data(marker.text)

    def get_info_by_coords(self, coords):
        """Обработка правого клика: координаты -> страна -> данные"""
        try:
            location = self.geolocator.reverse(coords, language='en')
            if location and 'address' in location.raw:
                country_name = location.raw['address'].get('country')
                if country_name:
                    self.fetch_and_show_country_data(country_name)
        except Exception as e:
            print(f"Ошибка геокодирования: {e}")

    def fetch_and_show_country_data(self, country_name):
        """3. Обработка данных: API запросы и парсинг"""
        try:
            # Используем REST Countries API (v3.1)
            response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}?fullText=true")
            data = response.json()[0]

            # Извлечение данных
            # Локализация на русский (если доступно в API)
            name_ru = data['translations'].get('rus', {}).get('common', country_name)
            
            # Валюта
            currencies = data.get('currencies', {})
            curr_code = list(currencies.keys())[0]
            curr_name = currencies[curr_code].get('name', 'N/A')
            # Небольшой хак для перевода рубля, если API на англ.
            if curr_code == "RUB": curr_name = "Российский рубль"

            # Население (форматирование: 146 028 325)
            population = f"{data.get('population', 0):,}".replace(',', ' ')

            # Флаг (URL)
            flag_url = data['flags']['png']

            # 4. Отображение результатов
            self.show_info_window(name_ru, flag_url, curr_name, population)

        except Exception as e:
            print(f"Ошибка получения данных: {e}")

    def show_info_window(self, name, flag_url, currency, population):
        """Создание всплывающего окна информации (как на скриншоте)"""
        info_win = tk.Toplevel(self.root)
        info_win.title("Информация о стране")
        info_win.geometry("350x450")
        info_win.configure(bg="white")

        # Название страны
        tk.Label(info_win, text=name, font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        # Загрузка и отображение флага
        try:
            img_response = requests.get(flag_url)
            img_data = Image.open(BytesIO(img_response.content))
            img_data = img_data.resize((200, 120), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_data)
            flag_label = tk.Label(info_win, image=photo, bg="white", borderwidth=1, relief="solid")
            flag_label.image = photo  # сохраняем ссылку
            flag_label.pack(pady=10)
        except:
            tk.Label(info_win, text="[Флаг не загружен]", bg="white").pack()

        # Информационная панель
        details_frame = tk.Frame(info_win, bg="white")
        details_frame.pack(padx=20, fill="x")

        tk.Label(details_frame, text="Валюта:", font=("Arial", 11, "bold"), bg="white").grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(details_frame, text=currency, font=("Arial", 11), bg="white").grid(row=0, column=1, sticky="w", padx=10)

        tk.Label(details_frame, text="Население:", font=("Arial", 11, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(details_frame, text=population, font=("Arial", 11), bg="white").grid(row=1, column=1, sticky="w", padx=10)

        # Кнопка закрыть
        btn_close = tk.Button(info_win, text="Закрыть", command=info_win.destroy, width=15)
        btn_close.pack(pady=30)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorldMapApp(root)
    root.mainloop()