import functools
from collections import namedtuple
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QTreeWidget
import sys
import GraphBuilder
import InputOutput

def scrollbar(graphBuilder):
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(window)

    tw = QtWidgets.QTreeWidget()
    tw.setHeaderLabels(['Non Terminal', 'Production Type', 'Production'])
    tw.setAlternatingRowColors(True)


    i = 0
    for node in graphBuilder.nodes_dictionary.values():
        rule_type = ""
        if (node.rule_type == GraphBuilder.RuleType.GRAMMAR):
            rule_type = "GRAMMAR"
        elif (node.rule_type == GraphBuilder.RuleType.STRICT):
            rule_type = "STRICT"
        elif (node.rule_type == GraphBuilder.RuleType.MACRO):
            rule_type = "MACRO"
        elif (node.rule_type == GraphBuilder.RuleType.TOKEN):
            rule_type = "TOKEN"
        item = QtWidgets.QTreeWidgetItem([node.value, rule_type,''])
        tw.addTopLevelItem(item)

        for production in node.productions_list.list:
            child_item = QtWidgets.QTreeWidgetItem(['', '',InputOutput.get_production_string(production)])
            child_item.setCheckState(0, QtCore.Qt.Checked)
            tw.topLevelItem(i).addChild(child_item)
            #table.insert(id,"end",node.value + rule_type + str(r),text="",values=(rule_type,graphBuilder.get_production_string(production)))
            #r = r + 1
        i += 1

    openTPTPFileAction = QAction('&Open TPTP Grammar File')
    openTPTPFileAction.setShortcut('Ctrl+O')
    #openTPTPFileAction.triggered.connect(self.openTPTPGrammarFile)

    openControlFileAction = QAction('&Reduce TPTP Grammar with Control File')
    openControlFileAction.setShortcut('Ctrl+R')
    #openControlFileAction.triggered.connect(self.reduceTPTPGrammarWithControlFile)

    produceReducedTPTPGrammarAction = QAction('&Reduced TPTP Grammar with Selection', window)
    produceReducedTPTPGrammarAction.setShortcut('Ctrl+B')
    #produceReducedTPTPGrammarAction.triggered.connect(self.reduceTPTPGrammarWithSelection)

    produceControlFileAction = QAction('&Produce Control File from Selection', window)
    produceControlFileAction.setShortcut('Ctrl+D')
    #produceControlFileAction.triggered.connect(produceControlFile)

    produceControlFileAction.triggered.connect(functools.partial(produceControlFile,tw))
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
    layout.addWidget(tw)
    window.show()

    sys.exit(app.exec_())

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


        #self.button.clicked.connect(self.openTPTPGrammarFile)

    def openTPTPGrammarFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open TPTP Grammar File", "","TPTP Grammar File (*.txt);;")
        if fileName:
            print(fileName)

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