import sys
import view
from PyQt5.QtWidgets import QApplication


if __name__== "__main__":

  app = QApplication(sys.argv)
  mainWindow = view.View()
  sys.exit(app.exec_())