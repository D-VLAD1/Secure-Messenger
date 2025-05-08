from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys
import inspect
from radon.complexity import cc_visit

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
rabin_enc_time = 0.0000096106529
ecc_enc_time = 6.926059722900391e-06

# Дешифрування
rsa_dec_time = 0.0015830945968627929
elg_dec_time = 0.0003760385513305664
rabin_dec_time = 0.0013728952407836914
ecc_dec_time = 5.47647476196289e-06


class PlotWindow(QWidget):
    def __init__(self, title, x_data, y_data, ylabel, footer_text=None):
        super().__init__()
        self.setWindowTitle(title)
        layout = QVBoxLayout()

        # Створення графіка
        self.resize(800, 600)
        fig = Figure(figsize=(4, 3))
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

        self.ecc_btn = QPushButton("Про ECC")
        self.ecc_btn.clicked.connect(self.show_ecc_info)
        layout.addWidget(self.ecc_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_gen_time(self):
        footer = "RSA - Швидкий генератор 2 простих p, q\n" \
 "Elgamal - найдовша генерація через проблему пошуку первісного кореня g за mod p.\n" \
 "Rabin - подібно до RSA, але з умовою що p ≡ q ≡ 3mod4.\n" \
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
        enc_footer = "RSA - швидко, c = m^e mod n\n" \
        "Elgamal - повільніше, бо працює з двома експонентами c1 = g^k modp, c2 = y^k*m modp з великим k\n" \
        "Rabin - найшвидше, всьоголиш виконати c = m^2 modn\n" \
        "ECC - найшвидше шифрування"
        self.plot_enc_window = PlotWindow(
            f"Час шифрування повідомлення\n m:'{message}'",
            algorithms,
            enc_times,
            "Час (с)",
            enc_footer
        )
        self.plot_enc_window.show()

        # Графік дешифрування
        dec_footer = "RSA - повільно, використовується велика експонента d\n" \
        "Elgamal - всього менше обчислень ніж у RSA\n" \
        "Rabin - не найкращий через обчислення зразу чотирьох коренів із яких один правильний\n" \
        "ECC - найшвидше, бо небагато важких обчислень"
        self.plot_dec_window = PlotWindow(
            f"Час дешифрування зашифрованого повідомлення\n m:'{message}'",
            algorithms,
            dec_times,
            "Час (с)",
            dec_footer
        )
        self.plot_dec_window.show()



    def evaluate_simplicity(self, algo_func):
        """
        Обчислює умовний індекс простоти реалізації:
        - менше рядків коду — простіше
        - нижча цикломатична складність — простіше
        - менше залежностей (import) — простіше
        - менше параметрів — простіше
        """
        source = inspect.getsource(algo_func)
        lines = len(source.splitlines())
        complexity = cc_visit(source)[0].complexity if cc_visit(source) else 1
        imports = sum(1 for line in source.splitlines() if 'import' in line)
        args = algo_func.__code__.co_argcount

        # Normalization (based on assumed max reasonable values)
        norm_lines = lines / 100     # 100 lines = max
        norm_complexity = complexity / 10  # 10 = very complex
        norm_imports = imports / 5   # 5 imports = high
        norm_args = args / 6         # 6+ arguments = complex interface

        # Clamp values to [0, 1]
        norm_lines = min(norm_lines, 1)
        norm_complexity = min(norm_complexity, 1)
        norm_imports = min(norm_imports, 1)
        norm_args = min(norm_args, 1)

        # Weighted average
        simplicity_score = (
            0.4 * norm_lines +
            0.3 * norm_complexity +
            0.2 * norm_imports +
            0.1 * norm_args
        )

        return simplicity_score  # Чим менше — тим простіше

    def evaluate_flexibility(self, algo_func):
        """Повертає кількість вхідних параметрів, які можна змінювати"""
        return algo_func.__code__.co_argcount


    def evaluate_security(self, name):
        """Повертає словник з деталями про криптографічну безпеку алгоритму"""
        if name == 'ECC':
            return {
                'bit_strength': 128,
                'key_size': 256,
                'quantum_resistant': False,
                'hard_problem': 'Elliptic Curve Discrete Logarithm Problem (ECDLP)'
            }
        elif name == 'Rabin':
            return {
                'bit_strength': 112,
                'key_size': 2048,
                'quantum_resistant': False,
                'hard_problem': 'Integer Factorization Problem'
            }
        elif name == 'ElGamal':
            return {
                'bit_strength': 80,
                'key_size': 1024,
                'quantum_resistant': False,
                'hard_problem': 'Discrete Logarithm Problem (DLP)'
            }
        else:
            return {
                'bit_strength': 0,
                'key_size': 0,
                'quantum_resistant': False,
                'hard_problem': 'Unknown'
            }

    def show_security_info(self):
        from Rabin.rabin import encrypt
        from ECC.utils import transform_msg
        from ELGamal.utils import encode_message

        algorithms = ['Rabin', 'ECC', 'ElGamal']
        funcs = {
            'Rabin': encrypt,
            'ECC': transform_msg,
            'ElGamal': encode_message
        }

        simplicity = [self.evaluate_simplicity(funcs[name]) for name in algorithms]
        flexibility = [self.evaluate_flexibility(funcs[name]) for name in algorithms]
        security_data = [self.evaluate_security(name) for name in algorithms]

        bit_strengths = [data['bit_strength'] for data in security_data]
        key_sizes = [data['key_size'] for data in security_data]
        summary_text = (
    "🔹 Rabin має найменшу складність реалізації серед трьох алгоритмів завдяки простоті коду, низькій цикломатичній "
    "складності та мінімальним залежностям. Його гнучкість обмежена через використання фіксованих параметрів, але він "
    "забезпечує високу криптостійкість при великих розмірах ключів (2048 біт).\n\n"
    
    "🔹 ECC (еліптична криптографія) має помірну складність реалізації через складніший математичний апарат. Водночас вона "
    "є дуже гнучкою — дозволяє змінювати типи кривих, поля та інші параметри. При цьому ECC забезпечує найвищу криптостійкість "
    "серед усіх трьох алгоритмів навіть при невеликому розмірі ключа (256 біт).\n\n"
    
    "🔹 ElGamal має найвищу складність реалізації, оскільки потребує більш об’ємного та складного коду. Проте він найбільш гнучкий — "
    "підтримує зміну багатьох параметрів, таких як генератор, група тощо. Його криптостійкість нижча за ECC і Rabin при однакових умовах, "
    "оскільки потребує довших ключів (зазвичай 1024 біти) для досягнення схожого рівня безпеки."
)
        # Set up layout: 3 plots in row + 1 text block below
        fig = plt.figure(figsize=(15, 10))
        gs = gridspec.GridSpec(2, 3, height_ratios=[4, 1.2])  # more space to plots, less to text

        # Plot 1: Simplicity
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(algorithms, simplicity, color='skyblue')
        ax1.set_title("Простота реалізації")
        ax1.set_ylabel("Індекс складності")
        ax1.grid(axis='y')

        # Plot 2: Flexibility
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.bar(algorithms, flexibility, color='lightgreen')
        ax2.set_title("Гнучкість")
        ax2.set_ylabel("Кількість аргументів")
        ax2.grid(axis='y')

        # Plot 3: Security
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.bar(algorithms, bit_strengths, color='salmon')
        ax3.set_title("Криптостійкість")
        ax3.set_ylabel("Біти безпеки")
        ax3.grid(axis='y')

        # Summary Text Block
        ax_text = fig.add_subplot(gs[1, :])
        ax_text.axis('off')
        ax_text.text(0.5, 0.5, summary_text, ha='center', va='center', wrap=True, fontsize=10, family='monospace')

        # Move everything upward
        fig.subplots_adjust(top=0.93, bottom=0.08, hspace=0.5)
        fig.suptitle("Порівняння криптографічних алгоритмів", fontsize=16)
        plt.show()

        
            # SINGLE TEXT BLOCK
        ax_text = fig.add_subplot(gs[1, :])
        ax_text.axis('off')
        ax_text.text(0.5, 0.5, summary_text, ha='center', va='center', wrap=True, fontsize=10, family='monospace')

        fig.suptitle("Порівняння криптографічних алгоритмів", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    def show_ecc_info(self):
        self.ecc_window = QWidget()
        self.ecc_window.setWindowTitle("Про ECC")
        layout = QVBoxLayout()
        label = QLabel(
            "<h3>Про ECC (еліптична криптографія)</h3>"
            "<b>1. У чому відмінність від RSA, Rabin, ElGamal?</b><br>"
            "ECC базується не на теорії чисел, а на складності обчислення точок"
            "на еліптичних кривих. Це дозволяє досягати тієї ж безпеки при значно менших ключах.<br><br>"
            "<b>2. Які переваги?</b><br>"
            "- Менші ключі: ECC-256 ≈ RSA-3072 за рівнем безпеки<br>"
            "- Швидка генерація ключів<br>"
            "- Менше використання памʼяті<br><br>"
            "<b>3. Наскільки складна реалізація?</b><br>"
            "Реалізація ECC складніша за RSA чи Rabin, бо потребує знань роботи з точками на кривій, "
            "обчислень у полях та контролю над випадками нескінченних точок.<br><br>"
            "<b>4. У яких сценаріях виграє або програє?</b><br>"
            "ECC виграє у мобільних, вбудованих системах, де критичні розміри ключів і швидкість.<br>"
            "Програє там, де є обмеження на складність реалізації або де стандартом є RSA.<br>"
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        self.ecc_window.setLayout(layout)
        self.ecc_window.resize(600, 400)
        self.ecc_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
