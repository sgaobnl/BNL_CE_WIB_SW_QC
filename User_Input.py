#4 vertical rows:
#
#Checkboxes: LArASIC, ColdADC, COLDATA
#
#Text inputs: Name, Email, Confirm Email
#
#Email mismatch raises a warning
#
#Tray ID input: must match format BdddTdddd
#
#Invalid format raises a warning
#
#Confirm button: validates all inputs and prints values if valid

import sys
import os
import re
from set_rootpath import rootdir_cs
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QButtonGroup
)
from PyQt5.QtCore import Qt


class FourRowForm(QWidget):
    def __init__(self):
        super().__init__()
#        self.ask_user()
        self.setWindowTitle("User input")
        self.setFixedSize(550, 500)
        self.summary_dict = {}

        # Disable minimize and close buttons
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        main_layout = QVBoxLayout()

        # ── Row 1: Checkboxes ────────────────────────────
        self.check_larasic = QCheckBox("LArASIC")
        self.check_coldadc = QCheckBox("ColdADC")
        self.check_coldata = QCheckBox("COLDATA")

        self.chip_group = QButtonGroup()
        self.chip_group.setExclusive(True)
        for cb in [self.check_larasic, self.check_coldadc, self.check_coldata]:
            self.chip_group.addButton(cb)
        self.check_larasic.setChecked(True)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Select one chip:"))
        row1.addWidget(self.check_larasic)
        row1.addWidget(self.check_coldadc)
        row1.addWidget(self.check_coldata)
        row1.addStretch()
        main_layout.addLayout(row1)

        # ── Row 2: Name and Email ───────────────────────
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")

        self.email1_input = QLineEdit()
        self.email1_input.setPlaceholderText("your@email.com")

        self.email2_input = QLineEdit()
        self.email2_input.setPlaceholderText("Re-enter your email")

        row2_name = QHBoxLayout()
        row2_name.addWidget(QLabel("Name:"))
        row2_name.addWidget(self.name_input)

        row2_email1 = QHBoxLayout()
        row2_email1.addWidget(QLabel("Email:"))
        row2_email1.addWidget(self.email1_input)

        row2_email2 = QHBoxLayout()
        row2_email2.addWidget(QLabel("Confirm Email:"))
        row2_email2.addWidget(self.email2_input)

        main_layout.addLayout(row2_name)
        main_layout.addLayout(row2_email1)
        main_layout.addLayout(row2_email2)

        # ── Row 3: Tray ID + confirmation ───────────────
        self.tray_input = QLineEdit()
        self.tray_input.setPlaceholderText("e.g., B123T4567")

        self.tray_confirm_input = QLineEdit()
        self.tray_confirm_input.setPlaceholderText("Re-enter Tray ID")

        row3a = QHBoxLayout()
        row3a.addWidget(QLabel("Tray ID:"))
        row3a.addWidget(self.tray_input)

        row3b = QHBoxLayout()
        row3b.addWidget(QLabel("Confirm Tray ID:"))
        row3b.addWidget(self.tray_confirm_input)

        main_layout.addLayout(row3a)
        main_layout.addLayout(row3b)

        # ── Row 4: Confirm + Force Exit buttons ─────────
        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setMinimumHeight(40)
        self.confirm_btn.setMinimumWidth(160)
        self.confirm_btn.setStyleSheet("font-size: 16px;")
        self.confirm_btn.clicked.connect(self.validate_form)

        self.force_btn = QPushButton("Force Exit")
        self.force_btn.setMinimumHeight(36)
        self.force_btn.setMinimumWidth(100)
        self.force_btn.setStyleSheet("color: red; font-weight: bold;")
        self.force_btn.clicked.connect(self.force_exit)

        row4 = QHBoxLayout()
        row4.addStretch()
        row4.addWidget(self.confirm_btn)
        row4.addSpacing(20)
        row4.addWidget(self.force_btn)
        row4.addStretch()

        main_layout.addLayout(row4)
        self.setLayout(main_layout)

    def validate_form(self):
        name = self.name_input.text().strip()
        email1 = self.email1_input.text().strip()
        email2 = self.email2_input.text().strip()
        tray_id = self.tray_input.text().strip()
        tray_id_confirm = self.tray_confirm_input.text().strip()

        email_pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        tray_pattern = re.compile(r"B\d{3}T\d{4}")

        if not name:
            QMessageBox.warning(self, "Missing Name", "Name cannot be empty.")
            return

        if not email_pattern.fullmatch(email1):
            QMessageBox.warning(self, "Invalid Email", "Email format is not valid.")
            return

        if email1 != email2:
            QMessageBox.warning(self, "Email Mismatch", "The two email fields must match.")
            return

        if not tray_pattern.fullmatch(tray_id):
            QMessageBox.warning(self, "Invalid Tray ID", "Tray ID must match format: BdddTdddd (e.g., B123T4567).")
            return

        if tray_id != tray_id_confirm:
            QMessageBox.warning(self, "Tray ID Mismatch", "Tray ID confirmation does not match.")
            return

        selected_chip = next(
            (cb.text() for cb in [self.check_larasic, self.check_coldadc, self.check_coldata] if cb.isChecked()),
            "None"
        )

        if 'LArASIC' in selected_chip:

            rootdir = rootdir_cs('FE') +"/" + tray_id + "/"
        elif 'ColdADC' in selected_chip:
            rootdir = rootdir_cs('ADC') +"/" + tray_id + "/"
        elif 'COLDATA' in selected_chip :
            rootdir = rootdir_cs('CD') +"/" + tray_id + "/"
        else:
            rootdir = ""

        if os.path.exists(rootdir):
            reply = QMessageBox.question(
                self,
                "Folder exists",
                f"'{rootdir}' exists, \n Continue?",
                QMessageBox.Ok | QMessageBox.No,
                QMessageBox.Ok
            )
    
            if reply == QMessageBox.No:
                return

        summary = f"Name: {name}\nEmail: {email1}\nTray ID: {tray_id}\nDUT type: {selected_chip}"
        self.summary_dict.update({
            "Name": name,
            "Email": email1,
            "Tray_ID": tray_id,
            "DUTtype": selected_chip
        })

        csvfp = "./asic_info.csv"
        if os.path.isfile(csvfp):
            tmps = []
            with open(csvfp, 'r') as fp:
                for cl in fp:
                    tmp = cl.split(",")
                    if "tester" in tmp[0]:
                        tmp[1] = self.summary_dict['Name']
                    if "DUT" in tmp[0][0:3]:
                        tmp[1] = self.summary_dict['DUTtype']
                    if "Email" in tmp[0][0:5]:
                        tmp[1] = self.summary_dict['Email']
                    if "Tray_ID" in tmp[0][0:7]:
                        tmp[1] = self.summary_dict['Tray_ID']
                    cln=','.join(tmp)
                    tmps.append(cln)
    
            with open(csvfp, 'w') as fp:
                for cl in tmps:
                    fp.write(cl)

            csvtext = "asic_info.csv is updated. \n"
        else:
            csvtext = "asic_info.csv not exist. \n"

        reply = QMessageBox.question(
            self,
            "Success",
            f"{summary}\n\n" + csvtext + "Confirm and close?",
            QMessageBox.Ok | QMessageBox.No,
            QMessageBox.Ok
        )

        if reply == QMessageBox.Ok:
            if "updated" in csvtext:
                self.close()

#    def ask_user(self):
#        reply = QMessageBox.question(
#            None,
#            "Robot Start",
#            "Robot Start?",
#            QMessageBox.Yes | QMessageBox.No,
#            QMessageBox.No
#        )
#    
#        if reply == QMessageBox.Yes:
#            pass
#            #print("Starting robot...")
#            # You can call your robot start logic here
#        else:
#            print("Please start the robot and run the script again.")
#            sys.exit()

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


def get_user_input():
    app = QApplication(sys.argv)
    form = FourRowForm()
    form.show()
    app.exec_()
    return form.summary_dict


if __name__ == "__main__":
    result = get_user_input()
    print("Returned summary_dict:", result)


