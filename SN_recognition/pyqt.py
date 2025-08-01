"""
image_wall.py  –  3 × 5 image grid demo
• captions come from a dictionary `chip_ds` (15 entries)
• caption text ≤ 35 chars (auto-truncated)
• caption #1 → green, caption #2 → red
• “Select” → shows red QLineEdit + “Save”, hides itself
• “Save → Yes” →
      – QLineEdit text turns green
      – caption text updated & green
      – button turns light-green
      – chip_ds entry updated
• 50-px blank strip at bottom
• Close button asks for confirmation
"""

import sys
from functools import partial
from typing import Dict
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QGridLayout, QDesktopWidget, QMessageBox
)

# ─── Config ────────────────────────────────────────────────────────────────
ROWS, COLS       = 3, 5            # grid dimensions (15 cells)
CELL_IMG_SIZE    = 200             # px width & height for placeholder image
CAPTION_MAX_LEN  = 35              # char limit (display)
BIG_FONT         = QFont("Arial", 10)
GRID_H_SPACING   = 20              # px between columns
GRID_V_SPACING   = 20              # px between rows
GRID_MARGINS     = (100, 0, 100, 50)  # left, top, right, bottom
WINDOW_SIZE      = (1500, 900)     # px (w, h)

# Colours
#CAPTION_COLORS   = {0: "green", 1: "red"}
ENTRY_RED_CSS    = "color: red;"
ENTRY_GREEN_CSS  = "color: green;"
SAVE_GREEN_CSS   = "background-color: lightgreen;"
SAVE_RED_CSS   = "background-color: red;"
SELECT_RED_CSS   = "background-color: red;"


class ImageWall(QWidget):
    def __init__(self, chip_ds: Dict[int, list]) -> None:
        super().__init__()
        self.chip_ds = chip_ds
        keys         = list(chip_ds.keys())

        self.setWindowTitle("Image Wall")
        self.setFixedSize(*WINDOW_SIZE)

        grid = QGridLayout()
        grid.setHorizontalSpacing(GRID_H_SPACING)
        grid.setVerticalSpacing(GRID_V_SPACING)
        grid.setContentsMargins(*GRID_MARGINS)

        # Placeholder pixmap (replace with real images if desired)
        placeholder = QPixmap(CELL_IMG_SIZE, CELL_IMG_SIZE)
        placeholder.fill(QColor("lightgray"))

        idx = 0
        for row in range(ROWS):
            for col in range(COLS):
                if idx>= len(keys):
                    resized_pixmap = placeholder
                else:
                    key   = keys[idx]            # dictionary key for this cell
                    raw   = ''.join([chip_ds[key][3],chip_ds[key][4], chip_ds[key][5], chip_ds[key][6],chip_ds[key][2],chip_ds[key][1]])
                    pixmap = QPixmap(chip_ds[key][7])  # Replace with your image path
                    resized_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)


                wrapper = QWidget()
                vbox    = QVBoxLayout(wrapper)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.setSpacing(5)

                # ── image ────────────────────────────────────────────────
                img = QLabel()
                img.setPixmap(resized_pixmap)
                img.setFixedSize(CELL_IMG_SIZE, CELL_IMG_SIZE)
                img.setStyleSheet("border: 1px solid black;")

                # ── caption ──────────────────────────────────────────────
                if idx>= len(keys):
                    display = ""
                else:
                    display = raw if len(raw) <= CAPTION_MAX_LEN else raw[:CAPTION_MAX_LEN - 1] + "…"
                caption = QLabel(display, alignment=Qt.AlignLeft)
                caption.setWordWrap(True)
                caption.setFixedWidth(CELL_IMG_SIZE + 100)  # a bit wider than image
                caption.setFont(BIG_FONT)

                caption.setStyleSheet(f"color: red;")

                # ── buttons / entry ─────────────────────────────────────
                select_btn = QPushButton("Correct?")
                select_btn.setFixedWidth(CELL_IMG_SIZE)
#                select_btn.setStyleSheet(SELECT_RED_CSS)
                if idx>= len(keys):
                    select_btn.hide()

                entry = QLineEdit(display)
                entry.setFixedWidth(CELL_IMG_SIZE + 100)
                entry.setMaxLength(CAPTION_MAX_LEN)
                entry.setFont(BIG_FONT)
                entry.setStyleSheet(ENTRY_RED_CSS)
                entry.hide()

                save_btn = QPushButton("Save")
                save_btn.setFixedWidth(CELL_IMG_SIZE)
                save_btn.hide()

                # wiring
                select_btn.clicked.connect(
                    partial(self._reveal_widgets, entry, save_btn, select_btn)
                )
                save_btn.clicked.connect(
                    partial(self._handle_save, entry, caption, key, save_btn, display)
                )

                # stack widgets
                for w in (img, caption, select_btn, entry, save_btn):
                    vbox.addWidget(w, alignment=Qt.AlignHCenter)

                grid.addWidget(wrapper, row, col)
                idx += 1

 
        self.setLayout(grid)
        self._center_on_screen()

    # ── slots ───────────────────────────────────────────────────────────────
    @staticmethod
    def _reveal_widgets(entry: QLineEdit, save_btn: QPushButton, select_btn: QPushButton) -> None:
        select_btn.hide()
        entry.show()
        save_btn.show()

    def _handle_save(
        self,
        entry: QLineEdit,
        caption: QLabel,
        key: int,
        save_btn: QPushButton,
        display
    ) -> None:
        new_text = entry.text()
        if QMessageBox.question(
            #self, "Confirm Save", "Save this text?",
            self, "Confirm Update", new_text,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.Yes:

            # 1) visual updates
            caption.setText(
                new_text if len(new_text) <= CAPTION_MAX_LEN else new_text[:CAPTION_MAX_LEN - 1] + "…"
            )
            ocr_text = new_text
            bnl_pos = ocr_text.find('BNLLArASICVersionP5B')
            sls_pos = ocr_text.find('/')
            if sls_pos > 2:
                chip_wf = ocr_text[sls_pos-2:sls_pos+3]
                chip_sn = ocr_text[sls_pos+3:sls_pos+3+9]
                pat1_flg = re.fullmatch(r"\d{2}/\d{2}", chip_wf)
                pat2_flg = re.fullmatch(r"\d{3}-\d{5}", chip_sn)
            else:
                chip_wf = "00/00"
                chip_sn = "000-00000"
                pat1_flg = False
                pat2_flg = False
            if (bnl_pos >= 0) and pat1_flg and pat2_flg:
                entry.setStyleSheet(ENTRY_GREEN_CSS)
                caption.setStyleSheet("color: green;")
                save_btn.setStyleSheet(SAVE_GREEN_CSS)
                self.chip_ds[key] = [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B', self.chip_ds[key][-1]]

                print(f"{key}: {self.chip_ds[key]}")
            else:
                entry.setStyleSheet(ENTRY_RED_CSS)
                caption.setStyleSheet("color: red;")
                save_btn.setStyleSheet(SAVE_RED_CSS)

        else:
            caption.setStyleSheet("color: red;")
            save_btn.setStyleSheet(SAVE_RED_CSS)

    # ── housekeeping ───────────────────────────────────────────────────────
    def _center_on_screen(self) -> None:
        g = self.frameGeometry()
        g.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(g.topLeft())

    # confirm on window close
    def closeEvent(self, event) -> None:  # type: ignore[override]
        if QMessageBox.question(
            self, "Confirm Exit", "No red text or button! \n Check and correct all?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


# ── launch ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # dummy data (15 identical items)
    rootdir = "E:/tmp/ocr/run3/"
    import pickle
    with open(rootdir + "ocr_results.bin", 'rb') as fn:
        chip_ds = pickle.load( fn)
    bad_chip_ds = {}
#    for key in list(chip_ds.keys()):
#        if not chip_ds[key][0] :
#            bad_chip_ds[key]= chip_ds[key]

    for key in range(6):
        if key in list(chip_ds.keys()):
            bad_chip_ds[key]= chip_ds[key]

    #chip_ds = {i: "placeholder caption" for i in range(ROWS * COLS)}

    wall = ImageWall(chip_ds=bad_chip_ds)
    wall.show()
    app.exec_()
    chip_ds.update(wall.chip_ds)
    print (chip_ds)

    sys.exit()


