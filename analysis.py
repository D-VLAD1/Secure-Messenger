from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QDialog
import sys
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import ECC.utils, Elgamal.utils, Rabin.rabin, RSA.utils

class KeygenWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вибір розміру ключа")
        self.setGeometry(400, 400, 300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Оберіть розмір ключа:")
        layout.addWidget(title)

        # Додаємо комбобокс для вибору розміру ключа
        self.key_size_combo = QComboBox()
        self.key_size_combo.addItems(['10**10', '10**50', '10**100'])
        layout.addWidget(self.key_size_combo)

        # Кнопка для розрахунку часу генерації ключа
        self.calculate_btn = QPushButton("Порівняти час")
        self.calculate_btn.clicked.connect(self.calculate_keygen_time)
        layout.addWidget(self.calculate_btn)

        self.setLayout(layout)

    def calculate_keygen_time(self):
        key_size = 10**10 if self.key_size_combo.currentText()=='10**10' else 10**50 if self.key_size_combo.currentText()=='10**50' else 10**100

        # Вимірюємо час генерації ключів для кожного алгоритму
        rsa_time = self.measure_keygen_time_RSA(RSA.utils, key_size)
        # rabin_time = self.measure_keygen_time_Rabin(Rabin.rabin.generate_key, key_size)
        # ecc_time = self.measure_keygen_time_ECC(ECC.utils.generate_key, key_size)
        elgamal_time = self.measure_keygen_time_Elgamal(Elgamal.utils, key_size)
        print(f"RSA: {rsa_time}, Elgamal: {elgamal_time}")
        # Показуємо графік
        # self.show_keygen_time_chart(rsa_time, rabin_time, ecc_time, elgamal_time)
        self.show_keygen_time_chart(rsa_time, elgamal_time)

    def measure_keygen_time_RSA(self, rsa_module, key_size):
        start_time = time.time()
        p = rsa_module.get_key(key_size, key_size*10)  # p generation
        q = rsa_module.get_key(key_size, key_size*10)  # q generation
        mod = p * q
        phi = (p - 1) * (q - 1)
        e = rsa_module.generate_key(phi) # public e
        d = pow(e, -1, phi) # private d
        print("RSA keys are done!")
        return time.time() - start_time

    def measure_keygen_time_Rabin(self, rabin_module, key_size):
        start_time = time.time()
        p, q = rabin_module(key_size, key_size*10)  # p, q generation
        mod = p * q
        phi = (p - 1) * (q - 1)
        e = rabin_module(phi) # public e
        d = pow(self.encrypt_key, -1, phi) # private d
        return time.time() - start_time

    def measure_keygen_time_ECC(self, p_q_gen, e_gen, key_size):
        start_time = time.time()
        p, q = p_q_gen(key_size, key_size*10)  # p, q generation
        mod = p * q
        phi = (p - 1) * (q - 1)
        e = e_gen(phi) # public e
        d = pow(self.encrypt_key, -1, phi) # private d
        return time.time() - start_time

    def measure_keygen_time_Elgamal(self, elg_module, key_size):
        start_time = time.time()
        p = elg_module.generate_prime(key_size, key_size*10) # p
        g = elg_module.primitive_root(p) # primitive root g
        secret_a = elg_module.random.randint(2, p-2) # a
        e = pow(g, secret_a, p) # e
        print("Elgamal keys are done!")
        return time.time() - start_time

    def show_keygen_time_chart(self, rsa_time, elgamal_time):
        algorithms = ['RSA', 'ElGamal']
        times = [rsa_time, elgamal_time]

        fig, ax = plt.subplots()
        ax.bar(algorithms, times)
        ax.set_ylabel('Час генерації ключа (сек.)')
        ax.set_title('Порівняння часу генерації ключів')

        canvas = FigureCanvas(fig)
        canvas.draw()
        canvas.setParent(self)
        self.layout().addWidget(canvas)


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Порівняння криптографічних алгоритмів")
        self.setGeometry(400, 400, 300, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Оберіть операцію для порівняння:")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.gen_time_btn = QPushButton("Порівняти час генерації ключів")
        self.gen_time_btn.clicked.connect(self.compare_keygen_time)
        layout.addWidget(self.gen_time_btn)

        self.crypt_time_btn = QPushButton("Порівняти час шифрування / розшифрування")
        self.crypt_time_btn.clicked.connect(self.compare_crypt_time)
        layout.addWidget(self.crypt_time_btn)

        self.memory_btn = QPushButton("Зіставити обсяги пам’яті")
        self.memory_btn.clicked.connect(self.compare_memory)
        layout.addWidget(self.memory_btn)

        self.setLayout(layout)

    def compare_keygen_time(self):
        self.keygen_window = KeygenWindow()
        self.keygen_window.exec()

    def compare_crypt_time(self):
        print("Тут буде логіка для вимірювання часу шифрування та розшифрування")

    def compare_memory(self):
        print("Тут буде логіка для оцінки використання пам’яті")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())
