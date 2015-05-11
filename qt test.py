__author__ = 'Michel'

from PySide.QtCore import *
from PySide.QtGui import *

import sys
import time


app = QApplication(sys.argv)

message = "Alert!"

window = QMainWindow()
window.setWindowFlags(Qt.WindowFrameSection)

QTimer.singleShot(10000, app.quit)
app.exec_()