import sys
import View
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = View.View()
    sys.exit(app.exec_())
