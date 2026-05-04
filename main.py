import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "weather_diary.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("700x500")

        # Хранилище записей
        self.records = []

        # --- Поля ввода ---
        input_frame = ttk.LabelFrame(root, text="Добавить запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (дд.мм.гггг):").grid(row=0, column=0, sticky="w")
        self.entry_date = ttk.Entry(input_frame, width=12)
        self.entry_date.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.entry_temp = ttk.Entry(input_frame, width=8)
        self.entry_temp.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w")
        self.entry_desc = ttk.Entry(input_frame, width=40)
        self.entry_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="ew")

        self.precip_var = tk.BooleanVar()
        self.check_precip = ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var)
        self.check_precip.grid(row=2, column=1, sticky="w", pady=5)

        self.btn_add = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        self.btn_add.grid(row=2, column=2, columnspan=2, sticky="e", padx=5)

        # --- Таблица ---
        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=250)
        self.tree.column("precipitation", width=80)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="По дате:").grid(row=0, column=0, sticky="w")
        self.filter_date = ttk.Entry(filter_frame, width=12)
        self.filter_date.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Мин. температура (°C):").grid(row=0, column=2, sticky="w")
        self.filter_temp = ttk.Entry(filter_frame, width=8)
        self.filter_temp.grid(row=0, column=3, padx=5)

        self.btn_filter = ttk.Button(filter_frame, text="Применить", command=self.apply_filter)
        self.btn_filter.grid(row=0, column=4, padx=5)
        self.btn_reset = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        self.btn_reset.grid(row=0, column=5, padx=5)

        # --- Кнопки сохранения/загрузки ---
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        self.btn_save = ttk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_json)
        self.btn_save.pack(side="left", padx=5)
        self.btn_load = ttk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_json)
        self.btn_load.pack(side="left", padx=5)

        # Загрузка данных при старте
        self.load_from_json()

    # --- Валидация и добавление ---
    def add_record(self):
        date_str = self.entry_date.get().strip()
        temp_str = self.entry_temp.get().strip()
        desc = self.entry_desc.get().strip()
        precip = self.precip_var.get()

        # Проверка даты
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            date_formatted = date_obj.strftime("%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Введите дд.мм.гггг")
            return

        # Проверка температуры
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        # Проверка описания
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        record = {
            "date": date_formatted,
            "temperature": temperature,
            "description": desc,
            "precipitation": "Да" if precip else "Нет"
        }
        self.records.append(record)
        self.refresh_table(self.records)
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.entry_date.delete(0, tk.END)
        self.entry_temp.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.precip_var.set(False)

    # --- Работа с таблицей ---
    def refresh_table(self, records):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in records:
            self.tree.insert("", "end", values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                rec["precipitation"]
            ))

    # --- Фильтрация ---
    def apply_filter(self):
        date_filter = self.filter_date.get().strip()
        temp_filter = self.filter_temp.get().strip()
        filtered = self.records

        if date_filter:
            filtered = [r for r in filtered if r["date"] == date_filter]

        if temp_filter:
            try:
                min_temp = float(temp_filter)
                filtered = [r for r in filtered if r["temperature"] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Минимальная температура должна быть числом")
                return

        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.refresh_table(self.records)

    # --- Сохранение и загрузка JSON ---
    def save_to_json(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_from_json(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.refresh_table(self.records)
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()