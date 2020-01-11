import functools
from collections import namedtuple
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QTreeWidget, QMainWindow, QMenu, QWidget, QHeaderView
import sys
import GraphBuilder
import InputOutput

def scrollbar(graphBuilder):
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(window)

    tableView = createTableView(graphBuilder)

    openTPTPFileAction = QAction('&Open TPTP Grammar File')
    openTPTPFileAction.setShortcut('Ctrl+O')
    openTPTPFileAction.triggered.connect(functools.partial(openTPTPGrammarFile,graphBuilder,tableView))

    openControlFileAction = QAction('&Reduce TPTP Grammar with Control File')
    openControlFileAction.setShortcut('Ctrl+R')
    #openControlFileAction.triggered.connect(self.reduceTPTPGrammarWithControlFile)

    produceReducedTPTPGrammarAction = QAction('&Reduced TPTP Grammar with Selection', window)
    produceReducedTPTPGrammarAction.setShortcut('Ctrl+B')
    #produceReducedTPTPGrammarAction.triggered.connect(self.reduceTPTPGrammarWithSelection)

    produceControlFileAction = QAction('&Produce Control File from Selection', window)
    produceControlFileAction.setShortcut('Ctrl+D')
    produceControlFileAction.triggered.connect(functools.partial(produceControlFile,tableView))
    menubar = QtWidgets.QMenuBar()

    actionFile = menubar.addMenu("Commands")
    actionFile.addAction(openTPTPFileAction)
    actionFile.addAction(openControlFileAction)
    actionFile.addAction(produceReducedTPTPGrammarAction)
    actionFile.addAction(produceControlFileAction)
    actionFile.addSeparator()
    actionFile.addAction("Quit")
    menubar.addMenu("Edit")
    menubar.addMenu("View")
    menubar.addMenu("Help")
    layout.addWidget(menubar)
    layout.addWidget(tableView)
    window.show()

    sys.exit(app.exec_())

def createTableView(graphBuilder: GraphBuilder.TPTPGraphBuilder) -> QtWidgets.QTreeWidget:
    tableView = QtWidgets.QTreeWidget()
    tableView.setHeaderLabels(['Non Terminal', 'Production Type', 'Production'])
    tableView.setAlternatingRowColors(True)
    nodesList = list(graphBuilder.nodes_dictionary.values())
    nodesList.sort(key=lambda x: x.position)
    for node in nodesList:
        rule_type = ""
        if (node.rule_type == GraphBuilder.RuleType.GRAMMAR):
            rule_type = "GRAMMAR"
        elif (node.rule_type == GraphBuilder.RuleType.STRICT):
            rule_type = "STRICT"
        elif (node.rule_type == GraphBuilder.RuleType.MACRO):
            rule_type = "MACRO"
        elif (node.rule_type == GraphBuilder.RuleType.TOKEN):
            rule_type = "TOKEN"
        item = QtWidgets.QTreeWidgetItem([node.value, rule_type, ''])
        for production in node.productions_list.list:
            child_item = QtWidgets.QTreeWidgetItem(['', '', InputOutput.get_production_string(production)])
            child_item.setCheckState(0, QtCore.Qt.Checked)
            item.addChild(child_item)
        tableView.addTopLevelItem(item)

    return tableView

def produceControlFile(treeView):
    fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None,"QFileDialog.getOpenFileName()", "", "Control File (*.txt);;")

    Entry = namedtuple("Entry", ["value", "rule_type"])
    entry_dictionary = {}
    for item in treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
        parent = item.parent()

        if((item.checkState(0) == 0) and (parent is not None)):
            rule_type = parent.text(1)
            entry = None
            if (rule_type == "GRAMMAR"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.GRAMMAR)
            elif (rule_type == "STRICT"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.STRICT)
            elif (rule_type == "MACRO"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.MACRO)
            elif (rule_type == "TOKEN"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.TOKEN)
            print(item.text(1) + " " + item.text(2), item.checkState(0))
            parent = item.parent()
            indexOfChild = parent.indexOfChild(item)
            if entry not in entry_dictionary:
                entry_dictionary[entry] = [indexOfChild]
            else:
                entry_dictionary[entry].append(indexOfChild)

    control_string = ""
    for key, value in entry_dictionary.items():
        rule_string = ""
        if (key.rule_type == GraphBuilder.RuleType.GRAMMAR):
            rule_string = "::="
        elif (key.rule_type == GraphBuilder.RuleType.STRICT):
            rule_string = ":=="
        elif (key.rule_type == GraphBuilder.RuleType.MACRO):
            rule_string = ":::"
        elif (key.rule_type == GraphBuilder.RuleType.TOKEN):
            rule_string = "::-"
        control_string += key.value + "," + rule_string + ","
        control_string += ','.join(map(str, value)) # add indexes separated by comma
        control_string += "\n"

    with open(fileName, "w") as text_file:
        text_file.write(control_string)

def openTPTPGrammarFile(self,graphBuilder: GraphBuilder.TPTPGraphBuilder):
    fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open TPTP Grammar File", "","TPTP Grammar File (*.txt);;")
    if fileName:
        print(fileName)
    graphBuilder.run(fileName)
    tableView = createTableView(graphBuilder)
    #return  tableView

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        openTPTPFileAction = QAction('&Open TPTP Grammar File', self)
        openTPTPFileAction.setShortcut('Ctrl+O')
        openTPTPFileAction.triggered.connect(self.openTPTPGrammarFile)

        openControlFileAction = QAction('&Reduce TPTP Grammar with Control File', self)
        openControlFileAction.setShortcut('Ctrl+R')
        openControlFileAction.triggered.connect(self.reduceTPTPGrammarWithControlFile)

        produceReducedTPTPGrammarAction = QAction('&Reduced TPTP Grammar with Selection', self)
        produceReducedTPTPGrammarAction.setShortcut('Ctrl+B')
        produceReducedTPTPGrammarAction.triggered.connect(self.reduceTPTPGrammarWithSelection)

        produceControlFileAction = QAction('&Produce Control File from Selection', self)
        produceControlFileAction.setShortcut('Ctrl+D')
        produceControlFileAction.triggered.connect(self.produceControlFile)

        menubar = QtWidgets.QMenuBar()
        self.layout.addWidget(menubar, 0, 0)
        actionFile = menubar.addMenu("Commands")
        actionFile.addAction(openTPTPFileAction)
        actionFile.addAction(openControlFileAction)
        actionFile.addAction(produceReducedTPTPGrammarAction)
        actionFile.addAction(produceControlFileAction)
        actionFile.addSeparator()
        actionFile.addAction("Quit")
        menubar.addMenu("Edit")
        menubar.addMenu("View")
        menubar.addMenu("Help")

        ##
        #app = QtWidgets.QApplication(sys.argv)
        #window = QtWidgets.QWidget()
        #self.button.clicked.connect(self.openTPTPGrammarFile)

    def addTreeView(self):
        return



    def reduceTPTPGrammarWithControlFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "","Control File (*.txt);;")
        if fileName:
            print(fileName)

    def reduceTPTPGrammarWithSelection(self):
        print("")

    def produceControlFile(self, treeView):
        Entry = namedtuple("Entry", ["value", "rule_type"])
        entry_dictionary = {}
        for item in treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            parent = item.parent()
            rule_type = parent.text(1)
            entry = None
            if (rule_type == "GRAMMAR"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.GRAMMAR)
            elif (rule_type == "STRICT"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.STRICT)
            elif (rule_type == "MACRO"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.MACRO)
            elif (rule_type == "TOKEN"):
                entry = Entry(parent.text(0), GraphBuilder.RuleType.TOKEN)

            if ((item.checkState(0) == 0) and (parent is not None)):
                print(item.text(1) + " " + item.text(2), item.checkState(0))
                parent = item.parent()
                indexOfChild = parent.indexOfChild(item)
                if entry not in entry_dictionary:
                    entry_dictionary[entry] = [indexOfChild]
                else:
                    entry_dictionary[entry].append(indexOfChild)
        print("")



        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "QFileDialog.getOpenFileName()", "","Control File (*.txt);;")
        if fileName:
            print(fileName)



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.treeView = None
        self.graphBuilder = None
        self.initUI()

    def initUI(self):
        openTPTPFileAction = QAction('&Open TPTP Grammar File',self)
        openTPTPFileAction.setShortcut('Ctrl+O')
        openTPTPFileAction.triggered.connect(self.openTPTPGrammarFile)

        #openControlFileAction = QAction('&Reduce TPTP Grammar with Control File')
        #openControlFileAction.setShortcut('Ctrl+R')
        # openControlFileAction.triggered.connect(self.reduceTPTPGrammarWithControlFile)

        #produceReducedTPTPGrammarAction = QAction('&Reduced TPTP Grammar with Selection', self)
        #produceReducedTPTPGrammarAction.setShortcut('Ctrl+B')
        # produceReducedTPTPGrammarAction.triggered.connect(self.reduceTPTPGrammarWithSelection)

        #produceControlFileAction = QAction('&Produce Control File from Selection', self)
        #produceControlFileAction.setShortcut('Ctrl+D')
        #produceControlFileAction.triggered.connect(functools.partial(produceControlFile, tableView))
        menubar = QtWidgets.QMenuBar()
        self.setMenuBar(menubar)
        menu = menubar.addMenu("Commands")
        # menu.addAction(openControlFileAction)
        # menu.addAction(produceReducedTPTPGrammarAction)
        # menu.addAction(produceControlFileAction)
        #menu.addSeparator()
        #menu.addAction("Quiti")
        menu.addAction(openTPTPFileAction)
        #self.setGeometry(300, 300, 600, 600)
        self.setWindowTitle('TPTP Grammar Reducer')
        self.showFullScreen()

    def initTreeView(self,graphBuilder: GraphBuilder.TPTPGraphBuilder) -> QtWidgets.QTreeWidget:
        self.treeView = QtWidgets.QTreeWidget()
        self.treeView.setHeaderLabels(['Non Terminal', 'Production Type', 'Production'])
        self.treeView.setAlternatingRowColors(True)
        self.treeView.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.treeView.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.treeView.header().setSectionResizeMode(2, QHeaderView.Stretch)
        nodesList = list(graphBuilder.nodes_dictionary.values())
        nodesList.sort(key=lambda x: x.position)
        for node in nodesList:
            rule_type = ""
            if (node.rule_type == GraphBuilder.RuleType.GRAMMAR):
                rule_type = "GRAMMAR"
            elif (node.rule_type == GraphBuilder.RuleType.STRICT):
                rule_type = "STRICT"
            elif (node.rule_type == GraphBuilder.RuleType.MACRO):
                rule_type = "MACRO"
            elif (node.rule_type == GraphBuilder.RuleType.TOKEN):
                rule_type = "TOKEN"
            item = QtWidgets.QTreeWidgetItem([node.value, rule_type, ''])
            for production in node.productions_list.list:
                child_item = QtWidgets.QTreeWidgetItem(['', '', InputOutput.get_production_string(production)])
                child_item.setCheckState(0, QtCore.Qt.Checked)
                item.addChild(child_item)
            self.treeView.addTopLevelItem(item)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.treeView)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def produceControlFile(self, treeView):
        return

    def reduceTPTPGrammarWithControlFile(self):
        return

    def openTPTPGrammarFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open TPTP Grammar File", "","TPTP Grammar File (*.txt);;")
        self.graphBuilder = GraphBuilder.TPTPGraphBuilder(fileName)
        self.initTreeView(self.graphBuilder)