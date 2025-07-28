import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QLineEdit, QTextEdit, QPushButton
)
from PyQt5.QtGui import QPixmap

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 GUI Example")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        # Display Image
        self.image_label = QLabel(self)
        pixmap = QPixmap("E:/tmp\ocr/run2\images/20250714144301_OCR_POST/tray_1_180.bmp")  # Replace with your image file
        self.image_label.setPixmap(pixmap.scaledToWidth(200))
        layout.addWidget(self.image_label)

        # Display Static Text
        self.text_label = QLabel("This is a sample text.")
        layout.addWidget(self.text_label)

        # Text Input Field
        self.input_label = QLabel("Enter something:")
        layout.addWidget(self.input_label)

        self.text_input = QLineEdit()
        layout.addWidget(self.text_input)

        # Optional: Multiline Text Display (like a log or output)
        self.output_area = QTextEdit()
        self.output_area.setPlaceholderText("Output will appear here...")
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        # Button
        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.on_button_click)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def on_button_click(self):
        user_text = self.text_input.text()
        self.output_area.append(f"You entered: {user_text}")
        self.text_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
