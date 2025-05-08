from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys

# Генерація ключів
iters = 100
key_len = "10**50"
rsa_time = 0.015076885223388672
elg_time = 1.276200224309702876
rabin_time = 0.03366813182830811
ecc_time = 0.049496512413024905
algorithms = ['RSA', 'ElGamal', "Rabin", "ECC"]
gen_times = [rsa_time, elg_time, rabin_time, ecc_time]

# Шифрування
iters = 100
message = "Test message for checking encoding and decoding speed"
rsa_enc_time = 0.00001367330551147461
elg_enc_time = 0.0003565835952758789
rabin_enc_time = 0
ecc_enc_time = 0

# Дешифрування
rsa_dec_time = 0.0015830945968627929
elg_dec_time = 0.0003760385513305664
rabin_dec_time = 0
ecc_dec_time = 0


class PlotWindow(QWidget):
    def __init__(self, title, x_data, y_data, ylabel, footer_text=None):
        super().__init__()
        self.setWindowTitle(title)
        layout = QVBoxLayout()

        # Створення графіка
        self.resize(800, 600)
        fig = Figure(figsize=(7, 5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.bar(x_data, y_data)

      # Додаємо текст над кожним стовпцем
        for i, v in enumerate(y_data):
            ax.text(i, v + max(y_data) * 0.01, f"{v:.7f}", ha='center', va='bottom', fontsize=9)

        ax.set_ylabel(ylabel)
        ax.set_title(title)

        if footer_text:
            fig.text(0.5, 0.01, footer_text, ha='center', fontsize=10)

        layout.addWidget(canvas)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Аналіз алгоритмів шифрування")
        self.resize(600, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Оберіть, що хочете проаналізувати:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # Центрування тексту
        self.label.setFont(QFont("Arial", 18))
        layout.addWidget(self.label)

        self.gen_btn = QPushButton("Час генерації ключів")
        self.gen_btn.clicked.connect(self.show_gen_time)
        layout.addWidget(self.gen_btn)

        self.enc_btn = QPushButton("Час шифрування/дешифрування")
        self.enc_btn.clicked.connect(self.show_enc_time)
        layout.addWidget(self.enc_btn)

        self.sec_btn = QPushButton("Безпека")
        self.sec_btn.clicked.connect(self.show_security_info)
        layout.addWidget(self.sec_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_gen_time(self):
        footer = "Elgamal - найдовша генерація через проблему пошуку первісних коренів великого числа.\n" \
 "Rabin - найшвидше, бо треба всього лиш два великих простих числа p та q які дорівнюють 3mod4.\n" \
 "RSA - схоже до Rabin, невелика різниця\n" \
 "ECC - генерація елементів групи, точки та обчислення множення займає небагато часу"
        self.plot_window = PlotWindow(
            f"Час генерації ключів розміру ~{key_len} на 100 ітераціях",
            algorithms, gen_times, "Час (с)", footer
        )
        self.plot_window.show()

    def show_enc_time(self):
        enc_times = [rsa_enc_time, elg_enc_time, rabin_enc_time, ecc_enc_time]
        dec_times = [rsa_dec_time, elg_dec_time, rabin_dec_time, ecc_dec_time]

        # Графік шифрування
        enc_footer = "RSA шифрує найшвидше, ElGamal трохи повільніше. Rabin та ECC не реалізовані."
        self.plot_enc_window = PlotWindow(
            f"Час шифрування повідомлення\n '{message}'",
            algorithms,
            enc_times,
            "Час (с)",
            enc_footer
        )
        self.plot_enc_window.show()

        # Графік дешифрування
        dec_footer = "Розшифрування в RSA повільніше через велику приватну експоненту."
        self.plot_dec_window = PlotWindow(
            f"Час дешифрування зашифрованого повідомлення\n '{message}'",
            algorithms,
            dec_times,
            "Час (с)",
            dec_footer
        )
        self.plot_dec_window.show()

    def show_security_info(self):
        # Тут можна реалізувати відкриття нового вікна з текстовою або табличною інформацією
        self.sec_window = QWidget()
        self.sec_window.setWindowTitle("Безпека")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("RSA: 2048 біт, ECC: 256 біт ..."))
        self.sec_window.setLayout(layout)
        self.sec_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
