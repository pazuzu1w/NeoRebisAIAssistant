import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QGridLayout, QPushButton

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Basic PyQt6 Calculator')
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.display = QLineEdit()
        self.grid.addWidget(self.display, 0, 0, 1, 4)  # Span across 4 columns

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+',
            'C', 'AC'
        ]

        row = 1
        col = 0
        for button_text in buttons:
            button = QPushButton(button_text)
            button.clicked.connect(self.handle_button_click)
            self.grid.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def handle_button_click(self):
        button = self.sender()
        text = button.text()

        if text == '=':
            try:
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except:
                self.display.setText("Error")
        elif text == 'C':
            self.display.setText(self.display.text()[:-1])
        elif text == 'AC':
            self.display.clear()
        else:
            self.display.setText(self.display.text() + text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())