import PyQt5
from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant


class MyListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(MyListModel, self).__init__(parent)
        self._data = [70, 90, 20, 50]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=PyQt5.DisplayRole):
        if not index.isValid() or \
            not 0 <= index.row() < self.rowCount():
                return QVariant()

        row = index.row()
        if role == PyQt5.DisplayRole:
            return str(self._data[row])
        return QVariant()