import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from threading import Thread
import re
import pyperclip  

class DictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Электронный словарь")
        self.root.geometry("750x750")
        self.root.configure(bg="#f0f0f0")
        
        # API ключи (замените на свои)
        self.yandex_api_key = "YOUR_API_KEY_HERE"
        self.free_dictionary_api = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        
        # Переменные для хранения данных
        self.current_data = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Стили
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 20, "bold"), background="#f0f0f0")
        
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="Электронный словарь",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=(0, 15))
        
        # Информационная панель
        info_frame = tk.Frame(main_frame, bg="#e8f5e9", bd=1, relief=tk.SOLID)
        info_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        info_label = tk.Label(
            info_frame,
            text="Поддерживает перевод: русский ↔ английский",
            font=("Arial", 10, "italic"),
            bg="#e8f5e9",
            fg="#2e7d32",
            pady=5
        )
        info_label.pack()
        
        # Раздел ввода
        input_frame = tk.LabelFrame(
            main_frame,
            text=" Введите слово: ",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#333333",
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Поле ввода с рамкой
        entry_frame = tk.Frame(input_frame, bg="white", bd=2, relief=tk.SUNKEN)
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.word_var = tk.StringVar()
        self.word_entry = tk.Entry(
            entry_frame,
            textvariable=self.word_var,
            font=("Arial", 14),
            width=30,
            justify='center',
            bd=0,
            relief=tk.FLAT
        )
        self.word_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.word_entry.bind('<Return>', lambda e: self.search_word())
        
        # Фокус на поле ввода при запуске
        self.word_entry.focus_set()
        
        # Индикатор языка
        self.lang_indicator = tk.Label(
            entry_frame,
            text="",
            font=("Arial", 9),
            bg="white",
            fg="gray"
        )
        self.lang_indicator.pack(side=tk.RIGHT, padx=5)
        
        # Кнопки
        button_frame = tk.Frame(input_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.RIGHT)
        
        # Стили для кнопок
        button_style = {
            'font': ("Arial", 11, "bold"),
            'width': 10,
            'height': 1,
            'relief': tk.RAISED,
            'bd': 2
        }
        
        self.search_btn = tk.Button(
            button_frame,
            text="Поиск",
            command=self.search_word,
            bg="#4CAF50",
            fg="white",
            **button_style
        )
        self.search_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="Очистить",
            command=self.clear_all,
            bg="#f44336",
            fg="white",
            **button_style
        )
        self.clear_btn.pack(side=tk.LEFT, padx=2)
        
        self.copy_btn = tk.Button(
            button_frame,
            text="Копировать",
            command=self.copy_to_clipboard,
            bg="#2196F3",
            fg="white",
            **button_style
        )
        self.copy_btn.pack(side=tk.LEFT, padx=2)
        
        # Информация о текущем слове
        self.word_info_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.word_info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.language_label = tk.Label(
            self.word_info_frame,
            text="",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#1565C0"
        )
        self.language_label.pack(side=tk.LEFT)
        
        self.translation_label = tk.Label(
            self.word_info_frame,
            text="",
            font=("Arial", 11),
            bg="#f0f0f0",
            fg="#2E7D32"
        )
        self.translation_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Раздел результатов
        result_frame = tk.LabelFrame(
            main_frame,
            text=" Результат: ",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#333333",
            padx=10,
            pady=10
        )
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Текстовое поле для результатов с прокруткой
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=("Consolas", 11),
            wrap=tk.WORD,
            bg="white",
            bd=2,
            relief=tk.SUNKEN,
            padx=15,
            pady=15,
            height=18
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Настройка тегов для форматирования
        self.result_text.tag_configure("header", font=("Consolas", 12, "bold"), foreground="#000000")
        self.result_text.tag_configure("divider", font=("Consolas", 11), foreground="#666666")
        self.result_text.tag_configure("pos", font=("Consolas", 11), foreground="#D32F2F")
        self.result_text.tag_configure("translation_num", font=("Consolas", 11, "bold"), foreground="#1976D2")
        self.result_text.tag_configure("translation", font=("Consolas", 11), foreground="#000000")
        self.result_text.tag_configure("synonyms", font=("Consolas", 10), foreground="#388E3C")
        self.result_text.tag_configure("example", font=("Consolas", 10, "italic"), foreground="#7B1FA2")
        
        # Статус бар
        self.status_bar = tk.Label(
            main_frame,
            text="Готов к работе. Введите слово на русском или английском языке",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e0e0e0",
            fg="#333333",
            font=("Arial", 9)
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def detect_language(self, word):
        """Определение языка слова"""
        if re.search(r'[а-яА-ЯёЁ]', word):
            return 'ru'
        elif re.search(r'[a-zA-Z]', word):
            return 'en'
        return None
    
    def search_word(self):
        """Поиск слова"""
        word = self.word_var.get().strip()
        
        if not word:
            messagebox.showwarning("Внимание", "Пожалуйста, введите слово для поиска")
            return
        
        # Определяем язык
        language = self.detect_language(word)
        if not language:
            messagebox.showerror("Ошибка", "Не удалось определить язык слова")
            return
        
        # Обновляем индикатор языка
        lang_text = "🇷🇺 Русский" if language == 'ru' else "🇬🇧 Английский"
        self.lang_indicator.config(text=lang_text)
        
        # Обновляем интерфейс
        self.search_btn.config(state=tk.DISABLED, text="Поиск...")
        self.status_bar.config(text=f"Идет поиск слова '{word}'...")
        
        # Запускаем поиск в отдельном потоке
        Thread(target=self.perform_search, args=(word, language), daemon=True).start()
    
    def perform_search(self, word, language):
        """Выполнение поиска в API"""
        try:
            if language == 'en':
                result = self.search_english_word(word)
            else:
                result = self.search_russian_word(word)
            
            # Сохраняем данные для копирования
            self.current_data = result
            
            # Обновляем UI в основном потоке
            self.root.after(0, self.display_results, result)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def search_english_word(self, word):
        """Поиск английского слова с переводом на русский"""
        result = {
            'original_word': word,
            'language': 'en',
            'translation': [],
            'phonetics': '',
            'part_of_speech': '',
            'synonyms': [],
            'examples': [],
            'russian_translation': []
        }
        
        # 1. Получаем информацию об английском слове
        try:
            url = f"{self.free_dictionary_api}{word.lower()}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = self.parse_english_response(data, word, result)
        except:
            pass  # Пропускаем если английский API не доступен
        
        # 2. Получаем перевод на русский через Яндекс
        try:
            russian_trans = self.get_russian_translation(word)
            result['russian_translation'] = russian_trans
        except:
            pass  # Пропускаем если Яндекс API не доступен
        
        return result
    
    def search_russian_word(self, word):
        """Поиск русского слова с переводом на английский"""
        result = {
            'original_word': word.upper(),
            'language': 'ru',
            'translation': [],
            'phonetics': '',
            'part_of_speech': '',
            'synonyms': [],
            'examples': []
        }
        
        # Получаем информацию через Яндекс API
        try:
            url = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"
            params = {
                "key": self.yandex_api_key,
                "lang": "ru-en",  # Русско-английский перевод
                "text": word,
                "flags": 4
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = self.parse_russian_response(data, word, result)
        except Exception as e:
            raise Exception(f"Ошибка при поиске русского слова: {str(e)}")
        
        return result
    
    def get_russian_translation(self, english_word):
        """Получение перевода английского слова на русский"""
        translations = []
        
        try:
            url = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"
            params = {
                "key": self.yandex_api_key,
                "lang": "en-ru",  # Англо-русский перевод
                "text": english_word,
                "flags": 4
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'def' in data and len(data['def']) > 0:
                for definition in data['def']:
                    for tr in definition.get('tr', []):
                        translations.append(tr.get('text', ''))
        
        except:
            pass
        
        return translations
    
    def parse_english_response(self, data, word, result):
        """Парсинг ответа от английского API"""
        if isinstance(data, list) and len(data) > 0:
            entry = data[0]
            
            # Фонетика
            if 'phonetics' in entry and len(entry['phonetics']) > 0:
                for ph in entry['phonetics']:
                    if 'text' in ph and ph['text']:
                        result['phonetics'] = ph['text']
                        break
            
            # Значения и переводы
            if 'meanings' in entry:
                for meaning in entry['meanings']:
                    result['part_of_speech'] = meaning.get('partOfSpeech', '')
                    
                    for definition in meaning.get('definitions', []):
                        translation = {
                            'meaning': definition.get('definition', ''),
                            'synonyms': definition.get('synonyms', []),
                            'example': definition.get('example', '')
                        }
                        result['translation'].append(translation)
                        
                        # Синонимы
                        result['synonyms'].extend(definition.get('synonyms', []))
                        
                        # Примеры
                        if definition.get('example'):
                            result['examples'].append(definition['example'])
                    
                    # Общие синонимы
                    result['synonyms'].extend(meaning.get('synonyms', []))
            
            # Убираем дубликаты
            result['synonyms'] = list(set(result['synonyms']))
        
        return result
    
    def parse_russian_response(self, data, word, result):
        """Парсинг ответа от Яндекс.Словаря"""
        if 'def' in data and len(data['def']) > 0:
            for definition in data['def']:
                result['part_of_speech'] = definition.get('pos', 'noun')
                
                # Транскрипция
                if 'ts' in definition:
                    result['phonetics'] = definition['ts']
                
                # Переводы
                for tr in definition.get('tr', []):
                    translation_item = {
                        'meaning': tr.get('text', ''),
                        'synonyms': [],
                        'example': ''
                    }
                    
                    # Синонимы для этого перевода
                    if 'syn' in tr:
                        for syn in tr['syn']:
                            translation_item['synonyms'].append(syn.get('text', ''))
                            result['synonyms'].append(syn.get('text', ''))
                    
                    # Примеры
                    if 'ex' in tr and len(tr['ex']) > 0:
                        for ex in tr['ex']:
                            if 'text' in ex:
                                example_text = f"{ex['text']} - {ex.get('tr', [{}])[0].get('text', '')}"
                                translation_item['example'] = example_text
                                result['examples'].append(example_text)
                                break
                    
                    result['translation'].append(translation_item)
        
        # Убираем дубликаты
        result['synonyms'] = list(set(result['synonyms']))
        
        return result
    
    def display_results(self, result):
        """Отображение результатов в текстовом поле"""
        self.result_text.delete(1.0, tk.END)
        
        # Обновляем информацию о языке
        lang_text = "АНГЛИЙСКОЕ СЛОВО" if result['language'] == 'en' else "РУССКОЕ СЛОВО"
        self.language_label.config(text=f"{lang_text}: {result['original_word']}")
        
        # Отображение перевода
        if result['language'] == 'en' and result['russian_translation']:
            trans_text = f"Перевод на русский: {', '.join(result['russian_translation'][:3])}"
            self.translation_label.config(text=trans_text)
        elif result['language'] == 'ru' and result['translation']:
            trans_text = f"Перевод на английский: {result['translation'][0]['meaning'] if result['translation'] else 'нет перевода'}"
            self.translation_label.config(text=trans_text)
        else:
            self.translation_label.config(text="")
        
        # Заголовок с названием слова
        if result['language'] == 'ru':
            self.result_text.insert(tk.END, f"РУССКОЕ СЛОВО: {result['original_word']}\n", "header")
        else:
            self.result_text.insert(tk.END, f"АНГЛИЙСКОЕ СЛОВО: {result['original_word'].capitalize()}\n", "header")
        
        self.result_text.insert(tk.END, "---\n\n", "divider")
        
        # Часть речи
        if result['part_of_speech']:
            pos_display = {
                'noun': 'существительное',
                'verb': 'глагол',
                'adjective': 'прилагательное',
                'adverb': 'наречие',
                'pronoun': 'местоимение',
                'preposition': 'предлог',
                'conjunction': 'союз',
                'interjection': 'междометие'
            }
            pos = result['part_of_speech']
            pos_text = pos_display.get(pos, pos)
            self.result_text.insert(tk.END, f"Часть речи: ", "pos")
            self.result_text.insert(tk.END, f"{pos_text}\n\n", "translation")
        
        # Транскрипция (для английских слов)
        if result['language'] == 'en' and result['phonetics']:
            self.result_text.insert(tk.END, f"Транскрипция: ", "pos")
            self.result_text.insert(tk.END, f"[{result['phonetics']}]\n\n", "translation")
        
        # Перевод на английский (для русских слов) - уже в заголовке
        if result['language'] == 'ru' and result['translation']:
            english_word = result['translation'][0]['meaning'] if result['translation'] else "n/a"
            self.result_text.insert(tk.END, f"Слово на английском: ", "pos")
            self.result_text.insert(tk.END, f"{english_word}\n\n", "translation")
        
        # Перевод на русский (для английских слов)
        if result['language'] == 'en' and result['russian_translation']:
            self.result_text.insert(tk.END, "Перевод на русский:\n", "pos")
            for i, trans in enumerate(result['russian_translation'][:5], 1):
                self.result_text.insert(tk.END, f"{i}. ", "translation_num")
                self.result_text.insert(tk.END, f"{trans}\n", "translation")
            self.result_text.insert(tk.END, "\n")
        
        # Определения/переводы
        if result['translation']:
            if result['language'] == 'en':
                self.result_text.insert(tk.END, "Значения:\n", "pos")
            else:
                self.result_text.insert(tk.END, "Переводы:\n", "pos")
            
            for i, trans in enumerate(result['translation'][:5], 1):
                self.result_text.insert(tk.END, f"{i}. ", "translation_num")
                self.result_text.insert(tk.END, f"{trans['meaning']}\n", "translation")
                
                # Синонимы для данного перевода
                if trans.get('synonyms'):
                    synonyms_text = ", ".join(trans['synonyms'][:3])
                    self.result_text.insert(tk.END, "   ", "synonyms")
                    self.result_text.insert(tk.END, f"Синонимы: {synonyms_text}\n", "synonyms")
                
                # Пример использования
                if trans.get('example'):
                    self.result_text.insert(tk.END, "   ", "example")
                    self.result_text.insert(tk.END, f"Пример: {trans['example']}\n", "example")
                
                self.result_text.insert(tk.END, "\n")
        
        # Общие синонимы, если есть
        if result['synonyms'] and len(result['synonyms']) > 0:
            self.result_text.insert(tk.END, "Синонимы:\n", "pos")
            synonyms_list = ", ".join(result['synonyms'][:10])
            self.result_text.insert(tk.END, f"{synonyms_list}\n\n", "synonyms")
        
        # Примеры использования
        if result['examples'] and len(result['examples']) > 0:
            self.result_text.insert(tk.END, "Примеры использования:\n", "pos")
            for i, example in enumerate(result['examples'][:3], 1):
                self.result_text.insert(tk.END, f"{i}. ", "example")
                self.result_text.insert(tk.END, f"{example}\n", "example")
        
        # Обновление статуса
        self.search_btn.config(state=tk.NORMAL, text="Поиск")
        trans_count = len(result['translation']) + len(result.get('russian_translation', []))
        self.status_bar.config(text=f"Найдено {trans_count} переводов/значений")
    
    def clear_all(self):
        """Очистить все поля"""
        self.word_var.set("")
        self.result_text.delete(1.0, tk.END)
        self.language_label.config(text="")
        self.translation_label.config(text="")
        self.lang_indicator.config(text="")
        self.current_data = None
        self.status_bar.config(text="Поля очищены. Введите новое слово")
        self.word_entry.focus_set()
    
    def copy_to_clipboard(self):
        """Копировать результаты в буфер обмена"""
        if self.current_data:
            # Формируем текст для копирования
            text_to_copy = self.result_text.get(1.0, tk.END)
            try:
                pyperclip.copy(text_to_copy)
                self.status_bar.config(text="Результаты скопированы в буфер обмена")
            except:
                messagebox.showinfo("Копирование", 
                    "Для функции копирования установите pyperclip:\n"
                    "pip install pyperclip\n\n"
                    "Альтернатива: выделите текст и используйте Ctrl+C")
        else:
            messagebox.showwarning("Внимание", "Нет данных для копирования")
    
    def show_error(self, error_message):
        """Отображение ошибки"""
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{error_message}")
        self.search_btn.config(state=tk.NORMAL, text="Поиск")
        self.status_bar.config(text="Ошибка при поиске. Проверьте API ключ и соединение")

def main():
    root = tk.Tk()
    app = DictionaryApp(root)
    
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