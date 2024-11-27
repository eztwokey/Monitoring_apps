import tkinter as tk
from tkinter import ttk
import subprocess
import os

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лаунчер программ")
        self.root.geometry("1920x1280")  # Установка размера окна

        # Создание кнопок для запуска программ
        self.create_buttons()

    def create_buttons(self):
        # Кнопка для запуска системного монитора
        self.monitor_button = ttk.Button(self.root, text="Система мониторинга АльтЛинукс", command=self.run_monitor)
        self.monitor_button.pack(pady=10)

        # Здесь можно добавить другие кнопки для других программ
        # Например:
        # self.other_program_button = ttk.Button(self.root, text="Другая программа", command=self.run_other_program)
        # self.other_program_button.pack(pady=10)

        # Кнопка выхода
        self.quit_button = ttk.Button(self.root, text="Выход", command=self.root.quit)
        self.quit_button.pack(pady=10)

    def run_monitor(self):
        # Запуск программы мониторинга
        monitor_script = os.path.join(os.path.dirname(__file__), "main.py")  # Укажите правильный путь к вашему скрипту
        subprocess.Popen(["python3", monitor_script])

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()