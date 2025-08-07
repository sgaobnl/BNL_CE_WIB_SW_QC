import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont  # add at top if not present


class InitChecklist(QWidget):
    def __init__(self):
        super().__init__()
        self.LN2_flg=False
        self.setWindowTitle("Initialization Checklist")
        self.setFixedSize(400, 300)

        # Disable minimize and close buttons
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout()

        # Checkboxes
        self.chk_tray      = QCheckBox("Tray in position with label")
        self.chk_tray.setFont(QFont("Arial", 14))
        self.chk_tray.setStyleSheet("QCheckBox::indicator { width: 24px; height: 24px; }")

        self.chk_enclosure = QCheckBox("Enclosure closed")
        self.chk_enclosure.setFont(QFont("Arial", 14))
        self.chk_enclosure.setStyleSheet("QCheckBox::indicator { width: 24px; height: 24px; }")

        self.chk_robot  = QCheckBox("Robot Server Start?")
        self.chk_robot.setFont(QFont("Arial", 14))
        self.chk_robot.setStyleSheet("QCheckBox::indicator { width: 24px; height: 24px; }")

        self.chk_coldtest  = QCheckBox("Cold test")
        self.chk_coldtest.setFont(QFont("Arial", 14))
        self.chk_coldtest.setStyleSheet("QCheckBox::indicator { width: 24px; height: 24px; }")

        layout.addWidget(QLabel("Checklist:"))
        layout.addWidget(self.chk_tray)
        layout.addWidget(self.chk_enclosure)
        layout.addWidget(self.chk_robot)
        layout.addWidget(self.chk_coldtest)

        # Buttons
        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setStyleSheet("font-size: 14px; padding: 6px;")
        self.confirm_btn.clicked.connect(self.confirm)

        self.force_exit_btn = QPushButton("Force Exit")
        self.force_exit_btn.setStyleSheet("color: red; font-weight: bold; padding: 6px;")
        self.force_exit_btn.clicked.connect(self.force_exit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.force_exit_btn)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def confirm(self):
        checks = {
            "Tray in position with label": self.chk_tray.isChecked(),
            "Enclosure closed": self.chk_enclosure.isChecked(),
            "Robot Server Start?": self.chk_robot.isChecked(),
            "Cold test": self.chk_coldtest.isChecked()
        }
        if self.chk_coldtest.isChecked():
            self.LN2_flg = True
        else:
            self.LN2_flg = False

        summary = "\n".join([f"[{'X' if v else ' '}] {k}" for k, v in checks.items()])

        reply = QMessageBox.question(
            self,
            "Confirm Checklist",
            f"You selected:\n\n{summary}\n\nProceed and close?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.close()

    def force_exit(self):
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to forcefully exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            sys.exit(0)

    def closeEvent(self, event):
        # Override top-right X button
        if self.chk_tray.isChecked() and self.chk_robot.isChecked() and self.chk_robot.isChecked():
            if self.chk_coldtest.isChecked():
                text = "Cold test? "
            else:
                text = "Warm test only? "
            reply = QMessageBox.question(
                self,
                "Exit",
                text,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

def init_chk():
    app = QApplication(sys.argv)
    gui = InitChecklist()
    gui.show()
    app.exec_()
    return gui.LN2_flg


if __name__ == "__main__":
    x = init_chk()
    print (x)

