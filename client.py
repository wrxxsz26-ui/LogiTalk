import threading
from socket import *
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.title("Black Chat")

        # 🔥 Увімкнення чорної теми
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")

        # 🎨 Кольори
        self.color_bg = "#0f0f0f"         # фон вікна (майже чорний)
        self.color_menu = "#1a1a1a"       # бокове меню
        self.color_button = "#2e2e2e"     # кнопки
        self.color_field = "#333333"      # поля
        self.text_color = "white"         # текст

        # ⚙️ Загальні налаштування
        self.configure(fg_color=self.color_bg)
        self.label = None
        self.is_show_menu = False
        self.speed_animate_menu = -5

        # 🧭 Меню
        self.menu_frame = CTkFrame(self, width=30, height=300, fg_color=self.color_menu)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.btn = CTkButton(
            self,
            text='▶️',
            command=self.toggle_show_menu,
            width=30,
            fg_color=self.color_button,
            hover_color="#444444",
            text_color=self.text_color
        )
        self.btn.place(x=0, y=0)

        # 💬 Поле чату
        self.chat_field = CTkTextbox(
            self,
            font=('Arial', 14, 'bold'),
            state='disable',
            fg_color=self.color_field,
            text_color=self.text_color
        )
        self.chat_field.place(x=0, y=0)

        # 🔤 Поле вводу
        self.message_entry = CTkEntry(
            self,
            placeholder_text='Введіть повідомлення:',
            height=40,
            fg_color=self.color_field,
            text_color=self.text_color,
            placeholder_text_color="#aaaaaa"
        )
        self.message_entry.place(x=0, y=0)

        # 🚀 Кнопка “Надіслати”
        self.send_button = CTkButton(
            self,
            text='>',
            width=50,
            height=40,
            command=self.send_message,
            fg_color=self.color_button,
            hover_color="#444444",
            text_color=self.text_color
        )
        self.send_button.place(x=0, y=0)

        # 👤 Користувач
        self.username = 'Artem'

        # 🔌 Підключення до сервера
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()

    # --- Меню ---
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()

            # елементи меню
            self.label = CTkLabel(self.menu_frame, text='Імʼя', text_color=self.text_color)
            self.label.pack(pady=30)
            self.entry = CTkEntry(
                self.menu_frame,
                fg_color=self.color_field,
                text_color=self.text_color,
                placeholder_text="Введіть ім'я"
            )
            self.entry.pack()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()

    # --- Адаптація інтерфейсу ---
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                  height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())
        self.after(50, self.adaptive_ui)

    # --- Відображення повідомлень ---
    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.see(END)
        self.chat_field.configure(state='disable')

    # --- Надсилання ---
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    # --- Отримання ---
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]
        if msg_type == "TEXT" and len(parts) >= 3:
            author = parts[1]
            message = parts[2]
            self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE" and len(parts) >= 4:
            author = parts[1]
            filename = parts[2]
            self.add_message(f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)


win = MainWindow()
win.mainloop()