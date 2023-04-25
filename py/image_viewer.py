import glob
import os
import math
import sys
import sorterlib
from collections import namedtuple

from PyQt5.QtCore import QAbstractTableModel, Qt, QSize, QByteArray
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QStyledItemDelegate

# Create a custom namedtuple class to hold our data.
preview = namedtuple("preview", "id title image")

NUMBER_OF_COLUMNS = 10
CELL_PADDING = 0 # all sides

class PreviewDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        # data is our preview object
        data = index.model().data(index, Qt.DisplayRole)
        if data is None:
            return

        width = option.rect.width() - CELL_PADDING * 2
        height = option.rect.height() - CELL_PADDING * 2

        # option.rect holds the area we are painting on the widget (our table cell)
        # scale our pixmap to fit
        scaled = data.image.scaled(
            width,
            height,
            aspectRatioMode=Qt.KeepAspectRatio,
        )
        # Position in the middle of the area.
        x = CELL_PADDING + (width - scaled.width()) // 2
        y = CELL_PADDING + (height - scaled.height()) // 2

        painter.drawImage(option.rect.x() + x, option.rect.y() + y, scaled)

    def sizeHint(self, option, index):
        # All items the same size.
        return QSize(160, 160)


class PreviewModel(QAbstractTableModel):
    def __init__(self, todos=None):
        super().__init__()
        # .data holds our data for display, as a list of Preview objects.
        self.previews = []

    def data(self, index, role):
        try:
            data = self.previews[index.row() * 4 + index.column() ]
        except IndexError:
            # Incomplete last row.
            return

        if role == Qt.DisplayRole:
            return data   # Pass the data to our delegate to draw.

        if role == Qt.ToolTipRole:
            return data.title

    def columnCount(self, index):
        return NUMBER_OF_COLUMNS

    def rowCount(self, index):
        n_items = len(self.previews)
        return math.ceil(n_items / NUMBER_OF_COLUMNS)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.view = QTableView()
        self.view.horizontalHeader().hide()
        self.view.verticalHeader().hide()
        self.view.setGridStyle(Qt.NoPen)

        delegate = PreviewDelegate()
        self.view.setItemDelegate(delegate)
        self.model = PreviewModel()
        self.view.setModel(self.model)

        self.setCentralWidget(self.view)

        # Add a bunch of images.
        os.chdir(sys.argv[1])
        for n, fn in enumerate(sorted(os.listdir())):
            with open(fn, 'rb') as file:
                img_data = file.read()
            (bead_color, pixels) = sorterlib.bead_color(img_data)
            print(bead_color)
            image = QImage(40, 40, QImage.Format_RGB888)
            for idx in range(40*30):
                if idx in pixels:
                    rgb_int = 0xffff0000
                else:
                    rgb = sorterlib._rgb_for_pixel(img_data, idx)
                    rgb_int = 0xff000000 | (rgb.r << 16) | (rgb.g << 8) | rgb.b
                image.setPixel(idx%40, idx//40, rgb_int)
            bead_rgb_int = 0xff000000 | (bead_color.r << 16) | (bead_color.g << 8) | bead_color.b
            for idx in range(40*30, 40*40):
                image.setPixel(idx%40, idx//40, bead_rgb_int)

            item = preview(n, fn, image)
            self.model.previews.append(item)
        self.model.layoutChanged.emit()

        self.view.resizeRowsToContents()
        self.view.resizeColumnsToContents()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
