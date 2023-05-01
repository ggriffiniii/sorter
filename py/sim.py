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
preview = namedtuple("preview", "title image")

class Tube(object):
  def __init__(self, idx, color):
    self.idx = idx
    self.colors = [color]
    self.count = 1

  def rgb_min_dist(self, color):
    return min((sorterlib.rgb_dist(color, tube_color) for tube_color in self.colors))

  def __str__(self):
    return f'Tube({self.idx}, colors={self.colors}, count={self.count})'


class PreviewDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        # data is our preview object
        data = index.model().data(index, Qt.DisplayRole)
        if data is None:
            return

        width = option.rect.width()
        height = option.rect.height()

        # option.rect holds the area we are painting on the widget (our table cell)
        # scale our pixmap to fit
        scaled = data.image.scaled(
            width,
            height,
            aspectRatioMode=Qt.KeepAspectRatio,
        )
        # Position in the middle of the area.
        x = (width - scaled.width()) // 2
        y = (height - scaled.height()) // 2

        painter.drawImage(option.rect.x() + x, option.rect.y() + y, scaled)

    def sizeHint(self, option, index):
        # All items the same size.
        return QSize(80, 80)


class PreviewModel(QAbstractTableModel):
    def __init__(self, todos=None):
        super().__init__()
        # .data holds our data for display, as a list of Preview objects.
        self.tubes = []
        self.beads = []

    def data(self, index, role):
        try:
            data = self.beads[index.row()][index.column()]
        except IndexError:
            # Incomplete last row.
            return

        if role == Qt.DisplayRole:
            return data   # Pass the data to our delegate to draw.

        if role == Qt.ToolTipRole:
            return data.title

    def columnCount(self, index):
        try:
          return max((len(beads) for beads in self.beads))
        except ValueError:
          return 0

    def rowCount(self, index):
        return len(self.tubes)


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
        for fn in sorted(os.listdir()):
            with open(fn, 'rb') as file:
                img_data = file.read()
            (bead_color, pixels) = sorterlib.bead_color_and_path(img_data)
            image = QImage(40, 40, QImage.Format_RGB888)
            for idx in range(40*30):
                rgb = sorterlib._rgb_for_pixel(img_data, idx)
                rgb_int = 0xff000000 | (rgb.r << 16) | (rgb.g << 8) | rgb.b
                if idx in pixels:
                    rgb_int = 0xffff0000
                image.setPixel(idx%40, idx//40, rgb_int)
            bead_rgb_int = 0xff000000 | (bead_color.r << 16) | (bead_color.g << 8) | bead_color.b
            for idx in range(40*30, 40*40):
                image.setPixel(idx%40, idx//40, bead_rgb_int)
            item = preview(fn, image)
            (closest_tube, dist) = min(((tube, tube.rgb_min_dist(bead_color)) for tube in self.model.tubes), key=lambda pair: pair[1], default=(None, 2**31))
            if dist < 35:
              print(f'{fn} {bead_color} is {dist} from {closest_tube}; assigning')
              self.model.beads[closest_tube.idx].append(item)
              closest_tube.count += 1
            elif len(self.model.tubes) < 30:
              print(f'{fn} {bead_color} is {dist} from {closest_tube}; allocating')
              tube_idx = len(self.model.tubes)
              self.model.tubes.append(Tube(tube_idx, bead_color))
              self.model.beads.append([item])
            else:
              furthest_tube = max(self.model.tubes, key=lambda tube: tube.rgb_min_dist(bead_color))
              print(f'{fn} {bead_color} is {dist} from {closest_tube}; overflow assigning to {furthest_tube}')
              self.model.beads[furthest_tube.idx].append(item)
              furthest_tube.count += 1
              furthest_tube.colors.append(bead_color)

        self.model.layoutChanged.emit()

        self.view.resizeRowsToContents()
        self.view.resizeColumnsToContents()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
