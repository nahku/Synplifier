from PyQt5.QtWidgets import QApplication
import sys
import view

if __name__== "__main__":

  app = QApplication(sys.argv)
  mainWindow = view.MainWindow()
  sys.exit(app.exec_())
