
from PyQt5.Qt import QApplication
from MainWindow import MainWindow
import sys

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

