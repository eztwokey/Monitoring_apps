import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import datetime

class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Профессиональный системный монитор")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1E1E1E")  # Современный тёмный фон

        # Данные для графиков
        self.cpu_data = []
        self.memory_data = []
        self.disk_data = []
        self.network_sent_data = []
        self.network_recv_data = []
        self.temperature_data = []
        self.process_count_data = []

        self.is_running = True

        # Пороговые значения для уведомлений
        self.cpu_threshold = 90
        self.memory_threshold = 90

        self.create_widgets()
        self.start_monitoring()

    def create_widgets(self):
        # Создание меню
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Добавление меню "Файл"
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.on_close)

        # Приветственное сообщение
        self.welcome_label = ttk.Label(
            self.root, text="Профессиональный мониторинг системы",
            font=("Helvetica", 18, "bold"),
            background="#1E1E1E", foreground="white"
        )
        self.welcome_label.pack(pady=(10, 0))

        self.description_label = ttk.Label(
            self.root,
            text="Отслеживайте использование ресурсов вашего компьютера в реальном времени.",
            font=("Helvetica", 12), background="#1E1E1E", foreground="white"
        )
        self.description_label.pack(pady=(0, 20))

        # Кнопка для принудительного обновления графиков
        self.update_button = ttk.Button(self.root, text="Обновить графики", command=self.update_plots)
        self.update_button.pack(pady=(0, 20))

        # Рамка для графиков
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Настройка графиков
        self.fig, self.axs = plt.subplots(3, 2, figsize=(12, 8))
        self.fig.patch.set_facecolor('#1E1E1E')  # Фон для всей фигуры

        # Настройка каждого графика
        self.setup_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Подвал программы
        self.footer_label = ttk.Label(
            self.root, text="Сделано Кириллом - версия 2.0",
            font=("Helvetica", 10),
            background="#1E1E1E", foreground="white"
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=(10, 10))

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_axes(self):
        # Настройка осей графиков
        axes_info = [
            (self.axs[0, 0], "Использование CPU (%)", 'lime'),
            (self.axs[0, 1], "Использование памяти (%)", 'cyan'),
            (self.axs[1, 0], "Использование диска (%)", 'magenta'),
            (self.axs[1, 1], "Сетевая активность (KB/s)", 'yellow'),
            (self.axs[2, 0], "Температура CPU (°C)", 'red'),
            (self.axs[2, 1], "Количество процессов", 'orange')
        ]

        for ax, title, color in axes_info:
            ax.set_title(title, fontsize=12, color='white')
            ax.set_facecolor("#2E2E2E")
            ax.grid(True, color='gray')
            ax.tick_params(axis='both', colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')

    def start_monitoring(self):
        # Запуск мониторинга в отдельном потоке
        self.monitor_thread = threading.Thread(target=self.update_data)
        self.monitor_thread.start()

    def update_data(self):
        # Для расчёта сетевой активности
        net_io = psutil.net_io_counters()
        prev_sent = net_io.bytes_sent
        prev_recv = net_io.bytes_recv

        while self.is_running:
            # Сбор данных
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            self.cpu_data.append(cpu)
            self.memory_data.append(memory)
            self.disk_data.append(disk)

            # Данные сети
            net_io = psutil.net_io_counters()
            sent = (net_io.bytes_sent - prev_sent) / 1024  # KB/s
            recv = (net_io.bytes_recv - prev_recv) / 1024  # KB/s
            self.network_sent_data.append(sent)
            self.network_recv_data.append(recv)
            prev_sent = net_io.bytes_sent
            prev_recv = net_io.bytes_recv

            # Данные температуры (если поддерживается)
            try:
                sensors = psutil.sensors_temperatures()
                if sensors:
                    for sensor in sensors.values():
                        for entry in sensor:
                            if entry.current:
                                temperature = entry.current
                                break
                    self.temperature_data.append(temperature)
                else:
                    self.temperature_data.append(None)
            except Exception:
                self.temperature_data.append(None)

            # Количество процессов
            self.process_count_data.append(len(psutil.pids()))

            # Ограничение длины данных
            max_points = 60
            data_sets = [
                self.cpu_data, self.memory_data, self.disk_data,
                self.network_sent_data, self.network_recv_data,
                self.temperature_data, self.process_count_data
            ]
            for data in data_sets:
                if len(data) > max_points:
                    data.pop(0)

            # Уведомление при превышении пороговых значений
            if cpu > self.cpu_threshold:
                self.show_notification("Высокая загрузка CPU!", f"Использование CPU превысило {self.cpu_threshold}%: {cpu}%")
            if memory > self.memory_threshold:
                self.show_notification("Высокая загрузка памяти!", f"Использование памяти превысило {self.memory_threshold}%: {memory}%")

            # Обновление графиков
            self.update_plots()

            time.sleep(1)  # Обновление каждую секунду

    def update_plots(self):
        # Очистка графиков
        for ax in self.axs.flat:
            ax.cla()
        self.setup_axes()

        # Обновление графиков
        x = range(len(self.cpu_data))

        # CPU
        self.axs[0, 0].plot(x, self.cpu_data, color='lime')
        self.axs[0, 0].set_ylim(0, 100)
        self.axs[0, 0].set_ylabel("Процент (%)", color='white')

        # Память
        self.axs[0, 1].plot(x, self.memory_data, color='cyan')
        self.axs[0, 1].set_ylim(0, 100)
        self.axs[0, 1].set_ylabel("Процент (%)", color='white')

        # Диск
        self.axs[1, 0].plot(x, self.disk_data, color='magenta')
        self.axs[1, 0].set_ylim(0, 100)
        self.axs[1, 0].set_ylabel("Процент (%)", color='white')

        # Сеть
        self.axs[1, 1].plot(x, self.network_sent_data, label='Отправлено', color='yellow')
        self.axs[1, 1].plot(x, self.network_recv_data, label='Получено', color='orange')
        self.axs[1, 1].legend(loc='upper right')
        self.axs[1, 1].set_ylabel("KB/s", color='white')

        # Температура
        if any(self.temperature_data):
            temp_data = [temp if temp is not None else 0 for temp in self.temperature_data]
            self.axs[2, 0].plot(x, temp_data, color='red')
            self.axs[2, 0].set_ylim(min(temp_data) - 5, max(temp_data) + 5)
            self.axs[2, 0].set_ylabel("°C", color='white')
        else:
            self.axs[2, 0].text(0.5, 0.5, 'Данные недоступны', horizontalalignment='center',
                                verticalalignment='center', transform=self.axs[2, 0].transAxes,
                                color='white', fontsize=12)

        # Количество процессов
        self.axs[2, 1].plot(x, self.process_count_data, color='orange')
        self.axs[2, 1].set_ylim(0, max(self.process_count_data) + 10)
        self.axs[2, 1].set_ylabel("Количество", color='white')

        # Обновление холста
        self.canvas.draw()

    def show_notification(self, title, message):
        # Функция для отображения уведомления
        messagebox.showwarning(title, message)

    def on_close(self):
        self.is_running = False
        self.monitor_thread.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()
