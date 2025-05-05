from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QLabel
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys

# Фіктивні дані для графіка
iters = 20
key_len = "10**50"
rsa_time = 0.016384208202362062
elg_time = 2.605035674571991
algorithms = ['RSA', 'ElGamal']
gen_times = [rsa_time, elg_time]

class PlotWindow(QWidget):
    def __init__(self, title, x_data, y_data, ylabel, footer_text=None):
        super().__init__()
        self.setWindowTitle(title)
        layout = QVBoxLayout()

        # Створення графіка
        fig = Figure(figsize=(5, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.bar(x_data, y_data)
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
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Оберіть, що проаналізувати:")
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
        footer = "Можем бачити, що Elgamal найдовше генерує ключі.\n Це загалом\
 через проблему пошуку первісних коренів за mod великого простого числа"
        self.plot_window = PlotWindow(
            f"Час генерації ключів розміру ~{key_len} на {iters} ітераціях",
            algorithms, gen_times, "Час (с)", footer
        )
        self.plot_window.show()

    def show_enc_time(self):
        # Приклад з фіктивними даними
        enc_times = [0.01, 0.009, 0.012, 0.003]
        self.plot_window = PlotWindow("Час шифрування", algorithms, enc_times, "Час (с)")
        self.plot_window.show()

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
