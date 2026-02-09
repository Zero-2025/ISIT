import tkinter as tk
from tkinter import ttk, font
import datetime
from tkinter import messagebox

class ModernWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤 Экспертная система погоды")
        self.root.geometry("500x830")
        self.root.configure(bg='#f0f8ff')
        
        # Устанавливаем иконку (если есть)
        try:
            self.root.iconbitmap('weather_icon.ico')
        except:
            pass
        
        # Цветовая схема
        self.colors = {
            'bg': '#f0f8ff',
            'card': '#ffffff',
            'primary': '#4a6fa5',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'blue': '#007bff',
            'gray': '#6c757d',
            'border': '#dee2e6'
        }
        
        # Данные для городов
        self.cities_data = {
            "Макеевка": {
                "temperature": -7,
                "feels_like": -7,
                "humidity": 60,
                "wind": 5,
                "pressure": 1013,
                "precipitation": 0.0,
                "condition": "ЯСНО",
                "icon": "☀️"
            },
            "Донецк": {
                "temperature": -5,
                "feels_like": -6,
                "humidity": 65,
                "wind": 7,
                "pressure": 1012,
                "precipitation": 0.0,
                "condition": "ЯСНО",
                "icon": "⛅"
            },
            "Ростов": {
                "temperature": 0,
                "feels_like": -2,
                "humidity": 70,
                "wind": 10,
                "pressure": 1015,
                "precipitation": 0.5,
                "condition": "ОБЛАЧНО",
                "icon": "☁️"
            },
            "Москва": {
                "temperature": -10,
                "feels_like": -12,
                "humidity": 80,
                "wind": 3,
                "pressure": 1008,
                "precipitation": 0.0,
                "condition": "СНЕГ",
                "icon": "❄️"
            },
            "Санкт-Петербург": {
                "temperature": -8,
                "feels_like": -10,
                "humidity": 75,
                "wind": 8,
                "pressure": 1010,
                "precipitation": 1.2,
                "condition": "ДОЖДЬ",
                "icon": "🌧️"
            }
        }
        
        self.current_city = "Макеевка"
        self.last_update = datetime.datetime.now()
        
        self.setup_fonts()
        self.create_widgets()
        self.update_display()
        
        # Автообновление каждые 60 секунд
        self.auto_refresh()
    
    def setup_fonts(self):
        """Настройка шрифтов"""
        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=11)
        self.city_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.condition_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.param_label_font = font.Font(family="Segoe UI", size=10, weight="bold")
        self.param_value_font = font.Font(family="Segoe UI", size=12)
        self.param_comment_font = font.Font(family="Segoe UI", size=9)
        self.time_font = font.Font(family="Segoe UI", size=9)
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной контейнер с прокруткой
        self.main_canvas = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg=self.colors['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.main_scrollbar.pack(side="right", fill="y")
        
        # Заголовок с иконкой
        header_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(header_frame,
                              text="🌤 Экспертная система погоды",
                              font=self.title_font,
                              bg=self.colors['bg'],
                              fg=self.colors['primary'])
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(header_frame,
                                 text="Машина вывода реляционного типа • v1.0",
                                 font=self.subtitle_font,
                                 bg=self.colors['bg'],
                                 fg=self.colors['gray'])
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Карточка выбора города
        city_card = tk.Frame(self.scrollable_frame,
                            bg=self.colors['card'],
                            relief=tk.RAISED,
                            bd=1,
                            padx=20,
                            pady=15)
        city_card.pack(fill=tk.X, pady=(0, 20))
        
        # Заголовок карточки
        card_title = tk.Label(city_card,
                             text="Выбор города",
                             font=self.param_label_font,
                             bg=self.colors['card'],
                             fg=self.colors['primary'])
        card_title.pack(anchor="w", pady=(0, 10))
        
        # Поле выбора города и кнопка
        control_frame = tk.Frame(city_card, bg=self.colors['card'])
        control_frame.pack(fill=tk.X)
        
        self.city_var = tk.StringVar(value=self.current_city)
        
        # Стилизованный Combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox",
                       fieldbackground=self.colors['light'],
                       background=self.colors['light'],
                       arrowcolor=self.colors['primary'])
        
        self.city_combo = ttk.Combobox(control_frame,
                                      textvariable=self.city_var,
                                      values=list(self.cities_data.keys()),
                                      state="readonly",
                                      width=20,
                                      font=self.subtitle_font)
        self.city_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.city_combo.bind("<<ComboboxSelected>>", self.on_city_changed)
        
        # Стилизованная кнопка Обновить
        self.refresh_btn = tk.Button(control_frame,
                                    text="🔄 Обновить",
                                    command=self.on_refresh,
                                    font=self.param_label_font,
                                    bg=self.colors['primary'],
                                    fg='white',
                                    activebackground=self.colors['dark'],
                                    activeforeground='white',
                                    relief=tk.RAISED,
                                    bd=1,
                                    padx=15,
                                    pady=5,
                                    cursor="hand2")
        self.refresh_btn.pack(side=tk.LEFT)
        
        # Разделитель
        separator = tk.Frame(self.scrollable_frame, height=1, bg=self.colors['border'])
        separator.pack(fill=tk.X, pady=(0, 20))
        
        # Карточка погоды
        weather_card = tk.Frame(self.scrollable_frame,
                               bg=self.colors['card'],
                               relief=tk.RAISED,
                               bd=1,
                               padx=20,
                               pady=20)
        weather_card.pack(fill=tk.X, pady=(0, 20))
        
        # Заголовок карточки погоды
        weather_title = tk.Label(weather_card,
                                text="Текущая погода",
                                font=self.param_label_font,
                                bg=self.colors['card'],
                                fg=self.colors['primary'])
        weather_title.pack(anchor="w", pady=(0, 15))
        
        # Название города и состояние
        city_condition_frame = tk.Frame(weather_card, bg=self.colors['card'])
        city_condition_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.city_name_label = tk.Label(city_condition_frame,
                                       text="",
                                       font=self.city_font,
                                       bg=self.colors['card'],
                                       fg=self.colors['dark'])
        self.city_name_label.pack(side=tk.LEFT)
        
        self.condition_icon = tk.Label(city_condition_frame,
                                      text="",
                                      font=font.Font(size=20),
                                      bg=self.colors['card'])
        self.condition_icon.pack(side=tk.LEFT, padx=(10, 0))
        
        self.condition_label = tk.Label(city_condition_frame,
                                       text="",
                                       font=self.condition_font,
                                       bg=self.colors['card'],
                                       fg=self.colors['blue'])
        self.condition_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Параметры погоды в сетке
        params_grid = tk.Frame(weather_card, bg=self.colors['card'])
        params_grid.pack(fill=tk.BOTH, expand=True)
        
        # Создаем 3 строки и 2 колонки для параметров
        self.param_widgets = {}
        params = [
            ("Температура", "temp", "°C"),
            ("Влажность", "humidity", "%"),
            ("Ветер", "wind", "км/ч"),
            ("Ощущается как", "feels_like", "°C"),
            ("Давление", "pressure", "гПа"),
            ("Осадки", "precipitation", "мм")
        ]
        
        for i, (label, key, unit) in enumerate(params):
            row = i // 2
            col = i % 2
            
            param_frame = tk.Frame(params_grid,
                                  bg=self.colors['card'],
                                  relief=tk.GROOVE,
                                  bd=1,
                                  padx=10,
                                  pady=10)
            param_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Название параметра
            label_widget = tk.Label(param_frame,
                                   text=label,
                                   font=self.param_label_font,
                                   bg=self.colors['card'],
                                   fg=self.colors['dark'])
            label_widget.pack(anchor="w")
            
            # Значение с иконкой
            value_frame = tk.Frame(param_frame, bg=self.colors['card'])
            value_frame.pack(fill=tk.X, pady=(5, 2))
            
            # Иконка параметра
            icons = {
                "temp": "🌡️",
                "humidity": "💧",
                "wind": "💨",
                "feels_like": "👤",
                "pressure": "📊",
                "precipitation": "🌧️"
            }
            icon_label = tk.Label(value_frame,
                                 text=icons.get(key, ""),
                                 font=font.Font(size=14),
                                 bg=self.colors['card'])
            icon_label.pack(side=tk.LEFT, padx=(0, 5))
            
            # Значение
            value_widget = tk.Label(value_frame,
                                   text="",
                                   font=self.param_value_font,
                                   bg=self.colors['card'],
                                   fg=self.colors['primary'])
            value_widget.pack(side=tk.LEFT)
            
            # Единица измерения
            unit_label = tk.Label(value_frame,
                                 text=unit,
                                 font=self.param_comment_font,
                                 bg=self.colors['card'],
                                 fg=self.colors['gray'])
            unit_label.pack(side=tk.LEFT, padx=(2, 0))
            
            # Комментарий
            comment_widget = tk.Label(param_frame,
                                     text="",
                                     font=self.param_comment_font,
                                     bg=self.colors['card'],
                                     fg=self.colors['gray'])
            comment_widget.pack(anchor="w")
            
            # Сохраняем ссылки
            self.param_widgets[key] = {
                'value': value_widget,
                'comment': comment_widget,
                'unit': unit
            }
        
        # Настройка веса строк и колонок
        for i in range(3):
            params_grid.rowconfigure(i, weight=1)
        for i in range(2):
            params_grid.columnconfigure(i, weight=1)
        
        # Панель статуса
        status_frame = tk.Frame(self.scrollable_frame,
                               bg=self.colors['light'],
                               relief=tk.SUNKEN,
                               bd=1,
                               padx=15,
                               pady=10)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Иконка статуса
        status_icon = tk.Label(status_frame,
                              text="⏱️",
                              font=font.Font(size=12),
                              bg=self.colors['light'])
        status_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.update_time_label = tk.Label(status_frame,
                                         text="",
                                         font=self.time_font,
                                         bg=self.colors['light'],
                                         fg=self.colors['gray'])
        self.update_time_label.pack(side=tk.LEFT)
        
        # Кнопка информации
        info_btn = tk.Button(status_frame,
                            text="ℹ️ О программе",
                            command=self.show_info,
                            font=self.time_font,
                            bg=self.colors['light'],
                            fg=self.colors['primary'],
                            relief=tk.FLAT,
                            bd=0,
                            cursor="hand2")
        info_btn.pack(side=tk.RIGHT)
    
    def update_display(self):
        """Обновляет отображение данных"""
        data = self.cities_data[self.current_city]
        
        # Обновляем название города
        self.city_name_label.config(text=self.current_city)
        
        # Обновляем состояние погоды и иконку
        self.condition_icon.config(text=data["icon"])
        self.condition_label.config(text=data["condition"])
        
        # Обновляем параметры
        temp_data = [
            ("temp", data["temperature"], self.get_temperature_comment(data["temperature"])),
            ("feels_like", data["feels_like"], self.get_temperature_comment(data["feels_like"])),
            ("humidity", data["humidity"], self.get_humidity_comment(data["humidity"])),
            ("wind", data["wind"], self.get_wind_comment(data["wind"])),
            ("pressure", data["pressure"], self.get_pressure_comment(data["pressure"])),
            ("precipitation", data["precipitation"], self.get_precipitation_comment(data["precipitation"]))
        ]
        
        for key, value, comment in temp_data:
            if key == 'precipitation':
                display_value = f"{value:.1f}".replace('.', ',')
            else:
                display_value = str(int(value))
            
            self.param_widgets[key]['value'].config(text=display_value)
            self.param_widgets[key]['comment'].config(text=comment)
        
        # Обновляем время
        time_str = self.last_update.strftime("%H:%M:%S")
        date_str = self.last_update.strftime("%d.%m.%Y")
        self.update_time_label.config(
            text=f"Данные для {self.current_city} обновлены: {time_str} • {date_str}"
        )
    
    def get_temperature_comment(self, temperature):
        """Получить комментарий к температуре"""
        if temperature < -10:
            return "❄️ Очень холодно"
        elif temperature < 0:
            return "🥶 Холодно"
        elif temperature < 15:
            return "😊 Прохладно"
        else:
            return "😎 Тепло"
    
    def get_humidity_comment(self, humidity):
        """Получить комментарий к влажности"""
        if humidity < 30:
            return "🏜️ Низкая"
        elif humidity < 70:
            return "👍 Нормальная"
        else:
            return "💦 Высокая"
    
    def get_wind_comment(self, wind):
        """Получить комментарий к ветру"""
        if wind < 5:
            return "🍃 Слабый"
        elif wind < 15:
            return "💨 Умеренный"
        else:
            return "💨💨 Сильный"
    
    def get_pressure_comment(self, pressure):
        """Получить комментарий к давлению"""
        if pressure < 1000:
            return "⬇️ Низкое"
        elif pressure < 1020:
            return "✅ Нормальное"
        else:
            return "⬆️ Высокое"
    
    def get_precipitation_comment(self, precipitation):
        """Получить комментарий к осадкам"""
        if precipitation == 0:
            return "☀️ Нет или слабые"
        elif precipitation <= 5:
            return "🌦️ Умеренные"
        else:
            return "⛈️ Сильные"
    
    def on_city_changed(self, event):
        """Обработчик изменения города"""
        self.current_city = self.city_var.get()
        self.last_update = datetime.datetime.now()
        self.update_display()
    
    def on_refresh(self):
        """Обработчик кнопки Обновить"""
        self.last_update = datetime.datetime.now()
        self.update_display()
        
        # Анимация кнопки
        self.refresh_btn.config(text="⏳ Обновление...")
        self.root.after(500, lambda: self.refresh_btn.config(text="🔄 Обновить"))
    
    def auto_refresh(self):
        """Автоматическое обновление каждые 60 секунд"""
        self.on_refresh()
        self.root.after(60000, self.auto_refresh)  # 60000 мс = 60 секунд
    
    def show_info(self):
        """Показать информацию о программе"""
        info_text = """🌤 Экспертная система погоды v1.0

Машина вывода реляционного типа
для определения погодных условий

Функции:
• Погода для 5 городов
• Интеллектуальная оценка параметров
• Автоматическое обновление
• Современный интерфейс

© 2024 Экспертная система погоды"""
        
        messagebox.showinfo("О программе", info_text)

def main():
    root = tk.Tk()
    app = ModernWeatherApp(root)
    
    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
