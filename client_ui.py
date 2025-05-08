"""Client for the secure messenger using PyQt6 and asyncio."""
import sys
import asyncio
import threading
import websockets
import urllib.request
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QTextEdit, QLineEdit, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from DSA.sign_utils import generate_keys, sign_message
from DSA.verification import verify_sign
import base64, ast, json

from ECC.client import ECC


with open("DSA_params.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
p = int(lines[0].split(": ")[1])
q = int(lines[1].split(": ")[1])
g = int(lines[2].split(": ")[1])

SERVER_URL = "wss://helo-bw8r.onrender.com/ws/"

class SignalHandler(QObject):
    """Signal handler for PyQt signals."""
    new_message = pyqtSignal(str)
    update_users = pyqtSignal(list)

class ChatClient(QWidget):
    """Main window for the secure messenger client."""
    def __init__(self):
        super().__init__()
        self.private_key, self.public_key = ECC.create_keys()

        self._connected = False

        self.setWindowTitle("Secure Messenger 💬 (PyQt6)")
        self.resize(600, 600)

        self.username = None
        self.websocket = None
        self.loop = None
        self.selected_recipient = None
        self.selected_recipient_key = None

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

        for el in self.username:
            if not(65 <= ord(el) <= 90 or 97 <= ord(el) <= 122 or 48 <= ord(el) <= 57):
                QMessageBox.warning(self, "Помилка", "Ім'я може містити лише літери та цифри.")
                return

        self.username_input.setEnabled(False)
        self.connect_button.setEnabled(False)

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

    async def __fetch_public_key(self, username):
        try:
            with websockets.connect(SERVER_URL + f'ws/get_key_{username}') as websocket:
                public_key = await websocket.recieve_text() ## gettin key from server
                self.selected_recipient_key = ast.literal_eval(public_key)
        except Exception as e:
            print(f"❌ Помилка отримання ключа користувача {username}: {e}")

    def user_selected(self, item):
        """Handle user selection from the list."""
        self.selected_recipient = item.text()
        self.message_input.setPlaceholderText(f"Пишете до: {self.selected_recipient}")
        threading.Thread(target=self.__fetch_public_key, args=(self.selected_recipient,), daemon=True).start()

    def run_client(self):
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())

    async def listen_messages(self):
        """Listen for incoming messages from the server."""
        async for content in self.websocket:

            if content.startswith("__ERROR__:Username already taken"):
                self.signals.new_message.emit("❌ Ім’я вже зайняте. Виберіть інше.")
                await self.websocket.close()
                return
            else:
                if not self._connected:
                    self.signals.new_message.emit("✅ Підключено до сервера!")
                    self._connected = True

            if isinstance(content, str) and content.startswith("__USERS__:"):
                users_str = content.replace("__USERS__:", "")
                users = users_str.split(",") if users_str else []
                self.signals.update_users.emit(users)

            try:
                username, _, message, iv, signature, y = json.loads(content) ## unpackin required variables
                message, iv = ast.literal_eval(message), base64.b64decode(ast.literal_eval(iv)) ## unpacking bytes from str
                r, s = signature
                decrypted_msg = ECC.decrypt(self.private_key, message, iv).strip() # decryption
                signature = (int(r), int(s))
                y = int(y)
                v = verify_sign(decrypted_msg, signature, p, q, g, y)
                if not v:
                    self.signals.new_message.emit("❌ Некоректний підпис!")
                    continue
                self.signals.new_message.emit(f"📩 {username}: {decrypted_msg}")

            except json.JSONDecodeError:
                continue

    async def connect_to_server(self):
        """Connect to the WebSocket server."""
        uri = SERVER_URL + self.username
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                await websocket.send(str(self.public_key))
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
        encrypted_msg, iv = ECC.encrypt(self.selected_recipient_key, message_text.encode('utf-8')) # encryption
        iv = base64.b64encode(iv)
        x, y = generate_keys(p, q, g)
        signature = sign_message(message_text, p, q, g, x)
        if not message_text:
            QMessageBox.warning(self, "Помилка", "Повідомлення порожнє.")
            return

        to_send = json.dumps((self.username, self.selected_recipient, str(encrypted_msg), str(iv), signature, y))
        asyncio.run_coroutine_threadsafe(self.websocket.send(to_send), self.loop)
        self.add_chat_message(f"➡️ Ви до {self.selected_recipient}: {message_text}")
        self.message_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatClient()
    window.show()
    sys.exit(app.exec())
