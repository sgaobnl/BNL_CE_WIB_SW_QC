import sys
from functools import partial
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QGridLayout, QDesktopWidget, QMessageBox
)

MAX_LEN = 50


class ImageWall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Wall")
        self.setFixedSize(1500, 900)

        grid = QGridLayout()
        grid.setHorizontalSpacing(50)
        grid.setVerticalSpacing(50)
        grid.setContentsMargins(0, 0, 0, 0)

        placeholder = QPixmap(200, 200)
        placeholder.fill(QColor("lightgray"))

        for row in range(3):
            for col in range(5):
                wrapper = QWidget()
                vbox = QVBoxLayout(wrapper)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.setSpacing(5)

                # image ----------------------------------------------------
                img = QLabel()
                img.setFixedSize(200, 200)
                img.setPixmap(placeholder)
                img.setStyleSheet("border: 1px solid black;")

                # caption --------------------------------------------------
                raw = f"Example caption for image {row*5 + col + 1}"
                caption_txt = raw if len(raw) <= MAX_LEN else raw[:MAX_LEN-1] + "…"
                caption = QLabel(caption_txt, alignment=Qt.AlignCenter)
                caption.setWordWrap(True)
                caption.setFixedWidth(200)

                if (row, col) == (0, 0):
                    caption.setStyleSheet("color: green;")
                elif (row, col) == (0, 1):
                    caption.setStyleSheet("color: red;")

                # Select button -------------------------------------------
                select_btn = QPushButton("Select")
                select_btn.setFixedWidth(200)

                # text input + Save button (initially hidden) -------------
                entry = QLineEdit(caption_txt)
                entry.setFixedWidth(200)
                entry.setMaxLength(50)
                entry.hide()

                save_btn = QPushButton("Save")
                save_btn.setFixedWidth(200)
                save_btn.hide()

                # reveal widgets
                select_btn.clicked.connect(
                    partial(self.reveal_widgets, entry, save_btn)
                )
                # confirm-on-save
                save_btn.clicked.connect(
                    partial(self.handle_save, entry)
                )

                # assemble -------------------------------------------------
                for w in (img, caption, select_btn, entry, save_btn):
                    vbox.addWidget(w, alignment=Qt.AlignHCenter)

                grid.addWidget(wrapper, row, col)

        self.setLayout(grid)
        self.center_on_screen()

    # ---------- helpers ----------------------------------------------------
    @staticmethod
    def reveal_widgets(entry, save_btn):
        entry.show()
        save_btn.show()

    def handle_save(self, entry):
        """Ask for confirmation, then (placeholder) 'save' the text."""
        text = entry.text()
        reply = QMessageBox.question(
            self,
            "Confirm Save",
            #"Save this text?",
            text,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            text = entry.text()
            # ↳ Replace this print with real save logic
            print("Saved:", text)

    def center_on_screen(self):
        geom = self.frameGeometry()
        geom.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(geom.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wall = ImageWall()
    wall.show()
    sys.exit(app.exec_())



exit()
import sys
from functools import partial
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QGridLayout, QDesktopWidget
)

MAX_LEN = 50                                      # caption limit


class ImageWall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Wall")
        self.setFixedSize(1500, 900)

        grid = QGridLayout()
        grid.setHorizontalSpacing(50)             # 200-px image + 50-px gap
        grid.setVerticalSpacing(50)
        grid.setContentsMargins(0, 0, 0, 0)

        # placeholder pixmap (swap with real images)
        placeholder = QPixmap(200, 200)
        placeholder.fill(QColor("lightgray"))

        for row in range(3):                      # 3 rows
            for col in range(5):                  # 5 images per row
                wrapper = QWidget()
                vbox    = QVBoxLayout(wrapper)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.setSpacing(5)

                # --- image -------------------------------------------------
                img = QLabel()
                img.setFixedSize(200, 200)
                img.setPixmap(placeholder)
                img.setStyleSheet("border: 1px solid black;")

                # --- caption (<=50 chars) ---------------------------------
                raw = f"Example caption for image {row*5 + col + 1}"
                caption_txt = raw if len(raw) <= MAX_LEN else raw[:MAX_LEN - 1] + "…"
                caption = QLabel(caption_txt, alignment=Qt.AlignCenter)
                caption.setWordWrap(True)
                caption.setFixedWidth(200)

                # color-code first two captions
                if (row, col) == (0, 0):
                    caption.setStyleSheet("color: green;")
                elif (row, col) == (0, 1):
                    caption.setStyleSheet("color: red;")

                # --- primary button ---------------------------------------
                select_btn = QPushButton("Select")
                select_btn.setFixedWidth(200)

                # --- hidden text input & second button --------------------
                entry = QLineEdit(caption_txt)
                entry.setFixedWidth(200)
                entry.setMaxLength(50)
                entry.hide()

                save_btn = QPushButton("Save")
                save_btn.setFixedWidth(200)
                save_btn.hide()

                # reveal entry + save button when Select is clicked
                select_btn.clicked.connect(
                    partial(self.reveal_widgets, entry, save_btn)
                )

                # assemble cell
                for w in (img, caption, select_btn, entry, save_btn):
                    vbox.addWidget(w, alignment=Qt.AlignHCenter)

                grid.addWidget(wrapper, row, col)

        self.setLayout(grid)
        self.center_on_screen()

    # ---------- helper slots ----------------------------------------------
    @staticmethod
    def reveal_widgets(entry, save_btn):
        entry.show()
        save_btn.show()

    def center_on_screen(self):
        geom = self.frameGeometry()
        geom.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(geom.topLeft())


if __name__ == "__main__":
    app  = QApplication(sys.argv)
    wall = ImageWall()
    wall.show()
    sys.exit(app.exec_())



exit()
import sys
from functools import partial

from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QGridLayout, QDesktopWidget
)

MAX_LEN = 50                        # caption limit


class ImageWall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Wall")
        self.setFixedSize(1500, 900)

        grid = QGridLayout()
        grid.setHorizontalSpacing(50)      # 200-px image + 50-px gap
        grid.setVerticalSpacing(50)
        grid.setContentsMargins(0, 0, 0, 0)

        # ----- placeholder pixmap (replace with real images) ---------------
        placeholder = QPixmap(200, 200)
        placeholder.fill(QColor("lightgray"))

        for row in range(3):               # 3 rows
            for col in range(5):           # 5 images per row
                # ---------- per-cell wrapper ------------------------------
                wrapper = QWidget()
                vbox = QVBoxLayout(wrapper)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.setSpacing(5)

                # image
                img = QLabel()
                img.setFixedSize(200, 200)
                img.setPixmap(placeholder)
                img.setStyleSheet("border: 1px solid black;")

                # caption (≤ 50 chars, truncated if needed)
                raw_caption = f"Example caption for image {row*5 + col + 1}"
                caption_text = raw_caption if len(raw_caption) <= MAX_LEN else raw_caption[:MAX_LEN - 1] + "…"

                caption = QLabel(caption_text)

                caption.setAlignment(Qt.AlignCenter)
                caption.setWordWrap(True)
                caption.setFixedWidth(200)
                caption = QLabel(caption_text)
                caption.setStyleSheet("color: green;")

                # button
                btn = QPushButton("Select")
                btn.setFixedWidth(200)

                # hidden text input (shows on button click)
                entry = QLineEdit()
                entry.setFixedWidth(200)
                entry.setPlaceholderText("Enter comment…")
                entry.setMaxLength(50)   
                entry.setText(caption_text)         # ← default content matches caption
                entry.hide()               # start invisible

                # connect button → show the entry
                btn.clicked.connect(partial(entry.show))

                # assemble cell
                for w in (img, caption, btn, entry):
                    vbox.addWidget(w, alignment=Qt.AlignHCenter)

                grid.addWidget(wrapper, row, col)

        self.setLayout(grid)
        self.center_on_screen()            # center once it’s built

    # ---------- helper ------------------------------------------------------
    def center_on_screen(self):
        """Center the window on the current primary monitor."""
        frame = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(screen_center)
        self.move(frame.topLeft())


if __name__ == "__main__":
    app  = QApplication(sys.argv)
    wall = ImageWall()
    wall.show()
    app.exec_()
    print ("great job")
    sys.exit()

exit()

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QGridLayout
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget   # add with your other imports

MAX_LEN = 50     # caption limit


class ImageWall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Wall")
        self.setFixedSize(1500, 900)


        grid = QGridLayout()
        grid.setHorizontalSpacing(50)       # 200-px image + 50-px gap
        grid.setVerticalSpacing(50)
        grid.setContentsMargins(50, 0, 0, 0)


        # build layouts, images, captions, buttons …
        self.setLayout(grid)
        self.center_on_screen()    # <— new line


        placeholder = QPixmap(200, 200)
        placeholder.fill(QColor("lightgray"))  # swap with real QPixmaps

        for row in range(3):                # 3 rows
            for col in range(5):            # 5 images per row
                # --- per-cell wrapper --------------------------------------
                wrapper = QWidget()
                vbox = QVBoxLayout(wrapper)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.setSpacing(5)

                # image
                img = QLabel()
                img.setFixedSize(200, 200)
                img.setPixmap(placeholder)
                img.setStyleSheet("border: 1px solid black;")

                # caption (≤50 chars)
                raw_caption = f"This is a sample caption for image {row*5+col+1}"
                caption_text = (raw_caption[:MAX_LEN - 3] + '…') if len(raw_caption) > MAX_LEN else raw_caption
                caption = QLabel(caption_text)
                caption.setWordWrap(True)
                caption.setAlignment(Qt.AlignCenter)
                caption.setFixedWidth(200)

                # button
                btn = QPushButton("Select")
                btn.setFixedWidth(200)

                # assemble wrapper
                vbox.addWidget(img)
                vbox.addWidget(caption)
                vbox.addWidget(btn)

                # drop wrapper into the main grid
                grid.addWidget(wrapper, row, col)

        self.setLayout(grid)

    def center_on_screen(self):
        """Move the window so its center aligns with the screen’s center."""
        geom = self.frameGeometry()                       # window’s rectangle
        screen_center = QDesktopWidget().availableGeometry().center()
        geom.moveCenter(screen_center)
        self.move(geom.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wall = ImageWall()
    wall.show()
    sys.exit(app.exec_())


exit()
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QGridLayout
)
from PyQt5.QtGui import QPixmap, QColor


class ImageWall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Wall")
        self.setFixedSize(1500, 900)

        grid = QGridLayout()
        grid.setHorizontalSpacing(50)        # 200-px image + 50-px gap = 250-px cell width
        grid.setVerticalSpacing(50)
        grid.setContentsMargins(0, 0, 0, 0)

        placeholder = QPixmap(200, 200)
        placeholder.fill(QColor("lightgray"))  # swap with real images

        for row in range(3):                 # 3 rows
            for col in range(5):             # 5 images per row
                # --- per-cell wrapper ---------------------------------------
                wrapper = QWidget()
                vbox    = QVBoxLayout(wrapper)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.setSpacing(5)           # gap between image and button

                # image
                lbl = QLabel()
                lbl.setFixedSize(200, 200)
                lbl.setPixmap(placeholder)
                lbl.setStyleSheet("border: 1px solid black;")

                # button
                btn = QPushButton("Select")
                btn.setFixedWidth(200)       # align with image width

                # assemble wrapper
                vbox.addWidget(lbl)
                vbox.addWidget(btn)

                # drop wrapper into the main grid
                grid.addWidget(wrapper, row, col)

        self.setLayout(grid)


if __name__ == "__main__":
    app  = QApplication(sys.argv)
    wall = ImageWall()
    wall.show()
    sys.exit(app.exec_())



exit()
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap, QColor

class ImageWall(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Wall")
        self.setFixedSize(1500, 900)

        grid = QGridLayout()
        grid.setHorizontalSpacing(50)     # 100-px image + 50-px gap = 150-px spacing
        grid.setVerticalSpacing(50)
        grid.setContentsMargins(0, 0, 0, 0)

        pix = QPixmap(200, 200)
        pix.fill(QColor("lightgray"))      # placeholder; replace with real images

        for row in range(3):               # 3 rows
            for col in range(5):          # 10 images per row
                lbl = QLabel()
                lbl.setFixedSize(200, 200)
                lbl.setPixmap(pix)
                grid.addWidget(lbl, row, col)
                lbl.setStyleSheet("border: 1px solid black;")
                grid.addWidget(lbl, row, col)
        self.setLayout(grid)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wall = ImageWall()
    wall.show()
    sys.exit(app.exec_())

