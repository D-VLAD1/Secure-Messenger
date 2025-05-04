"""Client for the secure messenger using PyQt6 and asyncio."""
import sys
import asyncio
import threading
import websockets
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QTextEdit, QLineEdit, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from DSA.sign_utils import generate_keys, sign_message
from DSA.verification import verify_sign

with open("DSA_params.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
p = int(lines[0].split(": ")[1])
q = int(lines[1].split(": ")[1])
g = int(lines[2].split(": ")[1])

SERVER_URL = "ws://localhost:8000/ws/"

class SignalHandler(QObject):
    """Signal handler for PyQt signals."""
    new_message = pyqtSignal(str)
    update_users = pyqtSignal(list)

class ChatClient(QWidget):
    """Main window for the secure messenger client."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Messenger 💬 (PyQt6)")
        self.resize(600, 600)

        self.username = None
        self.websocket = None
        self.loop = None
        self.selected_recipient = None

        self.signals = SignalHandler()
        self.signals.new_message.connect(self.add_chat_message)
        self.signals.update_users.connect(self.update_users_list)

        self.build_ui()

    def build_ui(self):
        """Build the UI components."""
        layout = QVBoxLayout()

        # Top: Username + Connect
        top_layout = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введіть ім'я")
        self.connect_button = QPushButton("🔗 Підключитись")
        self.connect_button.clicked.connect(self.start_connection)
        top_layout.addWidget(self.username_input)
        top_layout.addWidget(self.connect_button)
        layout.addLayout(top_layout)

        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(QLabel("💬 Чат:"))
        layout.addWidget(self.chat_area)

        # Users list
        layout.addWidget(QLabel("👥 Онлайн:"))
        self.users_list = QListWidget()
        self.users_list.itemClicked.connect(self.user_selected)
        layout.addWidget(self.users_list)

        # Bottom: Message input + Send
        bottom_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Напишіть повідомлення")
        self.send_button = QPushButton("✉️ Надіслати")
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.message_input)
        bottom_layout.addWidget(self.send_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def start_connection(self):
        """Start the connection to the server."""
        self.username = self.username_input.text().strip()
        if not self.username:
            QMessageBox.warning(self, "Помилка", "Введіть ім'я користувача.")
            return

        self.add_chat_message(f"🔗 Підключення як {self.username}...")

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.run_client, daemon=True).start()

    def add_chat_message(self, message):
        """Add a message to the chat area."""
        self.chat_area.append(message)

    def update_users_list(self, users):
        """Update the list of online users."""
        self.users_list.clear()
        for user in users:
            if user != self.username:
                self.users_list.addItem(user)

    def user_selected(self, item):
        """Handle user selection from the list."""
        self.selected_recipient = item.text()
        self.message_input.setPlaceholderText(f"Пишете до: {self.selected_recipient}")

    def run_client(self):
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())

    async def listen_messages(self):
        """Listen for incoming messages from the server."""
        async for content in self.websocket:
            if content.startswith("__USERS__:"):
                users_str = content.replace("__USERS__:", "")
                users = users_str.split(",") if users_str else []
                self.signals.update_users.emit(users)
            elif "||" in content:
                username, message, signature, y = content.split("||")
                r,s = signature[1:-1].split(",")
                signature = (int(r), int(s))
                y = int(y)
                v = verify_sign(message, signature, p, q, g, y)
                if not v:
                    self.signals.new_message.emit("❌ Некоректний підпис!")
                    return
                self.signals.new_message.emit(f"📩 {username}: {message}")


    async def connect_to_server(self):
        """Connect to the WebSocket server."""
        uri = SERVER_URL + self.username
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                self.signals.new_message.emit("✅ Підключено до сервера!")
                await self.listen_messages()
        except Exception as e:
            print(e)
            self.signals.new_message.emit(f"❌ Помилка підключення: {e}")

    def send_message(self):
        """Send a message to the selected recipient."""
        if not self.websocket:
            QMessageBox.warning(self, "Помилка", "Ви ще не підключені!")
            return
        if not self.selected_recipient:
            QMessageBox.warning(self, "Помилка", "Спершу оберіть одержувача!")
            return
        message_text = self.message_input.text().strip()
        x, y = generate_keys(p, q, g)
        signature = sign_message(message_text, p, q, g, x)
        if not message_text:
            QMessageBox.warning(self, "Помилка", "Повідомлення порожнє.")
            return

        to_send = f"{self.selected_recipient}||{message_text}||{signature}||{y}"
        asyncio.run_coroutine_threadsafe(self.websocket.send(to_send), self.loop)
        self.add_chat_message(f"➡️ Ви до {self.selected_recipient}: {message_text}")
        self.message_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatClient()
    window.show()
    sys.exit(app.exec())
