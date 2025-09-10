import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont


class PictureTextApp(QWidget):
    def __init__(self, image_path, text):
        super().__init__()
        self.result = None
        self.setWindowTitle("Chip SN Confirmation")

        # Ensure text is at most 50 characters
        if len(text) > 50:
            text = text[:50]

        # Layout
        layout = QVBoxLayout()

        # Display Image
        self.image_label = QLabel(self)
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaledToWidth(400))
        layout.addWidget(self.image_label)

        # Display Text (large, bold, dark green)
        self.text_label = QLabel(text, self)
        font = QFont()
        font.setPointSize(14)      # Larger font
        font.setBold(True)         # Bold
        self.text_label.setFont(font)
        self.text_label.setStyleSheet("color: darkgreen;")
        layout.addWidget(self.text_label)

        # Buttons in one row
        button_layout = QHBoxLayout()

        self.match_button = QPushButton("Match", self)
        self.mismatch_button = QPushButton("Mismatch", self)

        button_layout.addWidget(self.match_button)
        button_layout.addWidget(self.mismatch_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect buttons
        self.match_button.clicked.connect(self.return_match)
        self.mismatch_button.clicked.connect(self.return_mismatch)

    def return_match(self):
        msg = QMessageBox()
        msg.setWindowTitle("Confirm Match")
        msg.setText("You selected Match. Confirm?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        choice = msg.exec_()

        if choice == QMessageBox.Ok:
            self.result = 1
            self.close()

    def return_mismatch(self):
        msg = QMessageBox()
        msg.setWindowTitle("Confirm Mismatch")
        msg.setText("You selected Mismatch. Confirm?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        choice = msg.exec_()

        if choice == QMessageBox.Ok:
            self.result = 0
            self.close()

def run_sn_match_gui(image_path, text):
    app = QApplication(sys.argv)
    window = PictureTextApp(image_path, text)
    window.show()
    app.exec_()
    return window.result



if __name__ == "__main__":
    result = run_sn_match_gui("C:/SGAO/ColdTest/Tested/DAT_LArASIC_QC/B002T0008//images/SN_OCR/SN_002_03777_Tray_50_20250910143721.bmp", "This is sample text up to 50 characters.")
    print("Returned value:", result)

