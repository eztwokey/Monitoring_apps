import pandas as pd
import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Системный монитор")
        self.root.geometry("1920x1080")  # Установка размера окна
        self.root.configure(bg="#2E2E2E")  # Цвет фона

        self.cpu_data = []
        self.memory_data = []
        self.disk_data = []
        self.network_data = []
        self.temperature_data = []  # Для хранения данных температуры

        self.create_widgets()
        self.update_graphs()

    def create_widgets(self):
        # Приветственное слово
        self.welcome_label = ttk.Label(self.root, text="Мониторинг ПРО", font=("Helvetica", 16, "bold"), background="#2E2E2E", foreground="white")
        self.welcome_label.pack(pady=(10, 0))

        self.description_label = ttk.Label(self.root, text="Система создана для мониторинга использования ресурсов вашего компьютера.", font=("Helvetica", 12), background="#2E2E2E", foreground="white")
        self.description_label.pack(pady=(0, 20))

        # Создание рамки для графиков
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Настройка графиков
        self.fig, self.axs = plt.subplots(5, 1, figsize=(10, 10), constrained_layout=True)  # Растягиваем графики
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Настройка заголовков графиков
        self.axs[0].set_title("Использование CPU", fontsize=14, fontweight='bold', color='white')
        self.axs[1].set_title("Использование памяти", fontsize=14, fontweight='bold', color='white')
        self.axs[2].set_title("Использование диска", fontsize=14, fontweight='bold', color='white')
        self.axs[3].set_title("Использование сети", fontsize=14, fontweight='bold', color='white')
        self.axs[4].set_title("Температура (°C)", fontsize=14, fontweight='bold', color='white')

        # Настройка сетки для графиков
        for ax in self.axs:
            ax.grid(True)
            ax.set_facecolor("#3E3E3E")  # Цвет фона графиков
            ax.set_xlabel("Время (с)", fontsize=12, color='white')
            ax.set_ylabel("Процент (%)" if ax != self.axs[4] else "Температура (°C)", fontsize=12, color='white')
            ax.tick_params(axis='both', colors='white')  # Цвет меток осей

        # Кнопка выхода
        self.quit_button = ttk.Button(self.root, text="Выход", command=self.root.quit)
        self.quit_button.pack(pady=10)

        # Подвал программы
        self.footer_label = ttk.Label(self.root, text="Сделано Кириллом", font=("Helvetica", 10), background="#2E2E2E", foreground="white")
        self.footer_label.pack(side=tk.BOTTOM, pady=(10, 20))

    def update_graphs(self):
        # Сбор данных
        self.cpu_data.append(psutil.cpu_percent())
        self.memory_data.append(psutil.virtual_memory().percent)
        self.disk_data.append(psutil.disk_usage('/').percent)

        # Получение данных о сети
        net_io = psutil.net_io_counters()
        network_usage = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # МБ
        self.network_data.append(network_usage)

        # Получение данных о температуре (если поддерживается)
        try:
            sensors = psutil.sensors_temperatures()
            if 'coretemp' in sensors:
                temperature = sensors['coretemp'][0].current  # Получаем первую температуру
                self.temperature_data.append(temperature)
            else:
                self.temperature_data.append(0)  # Если температура недоступна
        except Exception as e:
            self.temperature_data.append(0)  # В случае ошибки

        # Ограничение длины данных
        if len(self.cpu_data) > 20:
            self.cpu_data.pop(0)
            self.memory_data.pop(0)
            self.disk_data.pop(0) 
            self.network_data.pop(0)
            self.temperature_data.pop(0)

        # Обновление графиков
        self.axs[0].clear()
        self.axs[1].clear()
        self.axs[2].clear()
        self.axs[3].clear()
        self.axs[4].clear()

        self.axs[0].plot(self.cpu_data, color='cyan')
        self.axs[1].plot(self.memory_data, color='magenta')
        self.axs[2].plot(self.disk_data, color='yellow')
        self.axs[3].plot(self.network_data, color='green')
        self.axs[4].plot(self.temperature_data, color='red')

        # Настройка заголовков графиков
        self.axs[0].set_title("Использование CPU", fontsize=14, fontweight='bold', color='white')
        self.axs[1].set_title("Использование памяти", fontsize=14, fontweight='bold', color='white')
        self.axs[2].set_title("Использование диска", fontsize=14, fontweight='bold', color='white')
        self.axs[3].set_title("Использование сети", fontsize=14, fontweight='bold', color='white')
        self.axs[4].set_title("Температура (°C)", fontsize=14, fontweight='bold', color='white')

        # Настройка сетки для графиков
        for ax in self.axs:
            ax.grid(True)
            ax.set_facecolor("#3E3E3E")  # Цвет фона графиков
            ax.set_xlabel("Время (с)", fontsize=12, color='white')
            ax.set_ylabel("Процент (%)" if ax != self.axs[4] else "Температура (°C)", fontsize=12, color='white')
            ax.tick_params(axis='both', colors='white')  # Цвет меток осей

        self.canvas.draw()
        self.root.after(1000, self.update_graphs)  # Обновление каждые 1 секунду

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()