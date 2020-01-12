from collections import namedtuple
#from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAction, QMainWindow, QWidget, QMessageBox, QFileDialog, QMenuBar, QTreeWidget, \
    QTreeWidgetItem, QVBoxLayout
import GraphBuilder
import InputOutput
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.treeView = None
        self.graphBuilder = None
        self.commentStatus = False
        self.initUI()

    def initUI(self):
        openTPTPFileAction = QAction('&Open TPTP Grammar File',self)
        openTPTPFileAction.setShortcut('Ctrl+O')
        openTPTPFileAction.triggered.connect(self.openTPTPGrammarFile)

        openControlFileAction = QAction('&Reduce and save TPTP Grammar with Control File')
        openControlFileAction.setShortcut('Ctrl+R')
        openControlFileAction.triggered.connect(self.outputTPTPGrammarFromControlFile)

        outputTPTPGrammarFileFromSelectionAction = QAction('&Create TPTP Grammar File from Selection', self)
        outputTPTPGrammarFileFromSelectionAction.setShortcut('Ctrl+R')
        outputTPTPGrammarFileFromSelectionAction.triggered.connect(self.createTPTPGrammarFileFromSelection)

        produceReducedTPTPGrammarAction = QAction('&Reduced TPTP Grammar with Selection', self)
        produceReducedTPTPGrammarAction.setShortcut('Ctrl+B')
        produceReducedTPTPGrammarAction.triggered.connect(self.reduceTPTPGrammarWithSelection)

        outputControlFileAction = QAction('&Produce Control File from Selection', self)
        outputControlFileAction.setShortcut('Ctrl+D')
        outputControlFileAction.triggered.connect(self.outputControlFile)

        toggleCommentsAction = QAction('&Toggle Comments',self)
        toggleCommentsAction.setShortcut('Ctrl+C')
        toggleCommentsAction.triggered.connect(self.toggleComments)

        menubar = QMenuBar()
        self.setMenuBar(menubar)
        menubar.setNativeMenuBar(False)
        menu = menubar.addMenu("Commands")
        menu.addAction(produceReducedTPTPGrammarAction)
        menu.addAction(outputControlFileAction)
        menu.addAction(outputTPTPGrammarFileFromSelectionAction)
        menu.addAction(toggleCommentsAction)
        menu.addAction(openTPTPFileAction)
        self.setWindowTitle('TPTP Grammar Reducer')
        self.showFullScreen()

    def initTreeView(self,graphBuilder: GraphBuilder.TPTPGraphBuilder) -> None:
        self.treeView = QTreeWidget()
        self.treeView.setHeaderLabels(['Non Terminal', 'Production Type', 'Production'])
        #self.treeView.setAlternatingRowColors(True)
        #self.treeView.header().setSectionResizeMode(0, QHeaderView.Stretch)
        #self.treeView.header().setSectionResizeMode(1, QHeaderView.Stretch)
        #self.treeView.header().setSectionResizeMode(2, QHeaderView.Stretch)
        nodesList = list(graphBuilder.nodes_dictionary.values())
        nodesList.sort(key=lambda x: x.position)
        for node in nodesList:
            if(node.position >= 0):
                rule_type = ""
                if (node.rule_type == GraphBuilder.RuleType.GRAMMAR):
                    rule_type = "GRAMMAR"
                elif (node.rule_type == GraphBuilder.RuleType.STRICT):
                    rule_type = "STRICT"
                elif (node.rule_type == GraphBuilder.RuleType.MACRO):
                    rule_type = "MACRO"
                elif (node.rule_type == GraphBuilder.RuleType.TOKEN):
                    rule_type = "TOKEN"
                item = QTreeWidgetItem([node.value, rule_type, ''])
                item.setCheckState(0, QtCore.Qt.Unchecked)

                light_gray = QColor(237, 244, 248)
                item.setBackground(0, light_gray)
                item.setBackground(1, light_gray)
                item.setBackground(2, light_gray)
                for production in node.productions_list.list:
                    child_item = QTreeWidgetItem(['', '', InputOutput.get_production_string(production)])
                    child_item.setCheckState(0, QtCore.Qt.Checked)
                    item.addChild(child_item)
                if(node.comment_block is not None):
                    comment = "\n".join(node.comment_block.list)
                    comment_item = QTreeWidgetItem([comment])
                    self.treeView.addTopLevelItem(comment_item)
                    comment_item.setHidden(False)
                    comment_item.setFlags(item.flags() ^ Qt.ItemIsUserCheckable)
                self.treeView.addTopLevelItem(item)

        layout = QVBoxLayout()
        layout.addWidget(self.treeView)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def toggleComments(self):
        new_status = not self.commentStatus
        for item in self.treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            flags = item.flags()
            if(not(Qt.ItemIsUserCheckable & flags)):
                item.setHidden(new_status)
        self.commentStatus = new_status

    def outputControlFile(self):
        filename, _ = QFileDialog.getSaveFileName(None, "QFileDialog.getOpenFileName()", "", "Control File (*.txt);;")
        control_string = self.produceControlFile()
        if(control_string is not None):
            InputOutput.save_text_to_file(control_string,filename)

    def produceControlFile(self):
        Entry = namedtuple("Entry", ["value", "rule_type"])
        entry_dictionary = {}
        start_symbol_selection = []
        for item in self.treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            parent = item.parent()

            if ((item.checkState(0) == 0) and (parent is not None)):
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
                #print(item.text(1) + " " + item.text(2), item.checkState(0))
                parent = item.parent()
                indexOfChild = parent.indexOfChild(item)
                if entry not in entry_dictionary:
                    entry_dictionary[entry] = [indexOfChild]
                else:
                    entry_dictionary[entry].append(indexOfChild)
            elif((item.checkState(0) > 0) and (parent is None)):
                start_symbol_selection.append(item.text(0))

        #if multiple start symbols are selected
        multiple_start_symbols = not all(elem == start_symbol_selection[0] for elem in start_symbol_selection)
        if multiple_start_symbols:
            QMessageBox.about(self, "Error", "Multiple start symbols are not allowed")
            return None, None

        if (len(start_symbol_selection) == 0):
            QMessageBox.about(self, "Error", "A start symbol has to be selected")
            return None, None

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
            control_string += ','.join(map(str, value))  # add indexes separated by comma
            control_string += "\n"
        return control_string, start_symbol_selection[0]

    def reduceTPTPGrammarWithSelection(self):
        control_string, start_symbol = self.produceControlFile()
        if((control_string is not None) and (start_symbol is not None)):
            self.graphBuilder.disable_rules(control_string,start_symbol)
            self.initTreeView(self.graphBuilder)

    def createTPTPGrammarFileFromSelection(self):
        filename, _ = QFileDialog.getSaveFileName(None, "QFileDialog.getOpenFileName()", "", "Control File (*.txt);;")
        control_string, start_symbol = self.produceControlFile()
        if(start_symbol is not None):
            graphBuilder = GraphBuilder.TPTPGraphBuilder()
            graphBuilder.nodes_dictionary = self.graphBuilder.nodes_dictionary
            graphBuilder.init_tree(start_symbol)
            if(control_string is not None):
                self.graphBuilder.disable_rules(control_string,start_symbol)
                start_node = self.graphBuilder.nodes_dictionary.get(GraphBuilder.Node("<start_symbol>",GraphBuilder.RuleType.GRAMMAR))
            if(start_node is not None):
                InputOutput.save_ordered_rules_from_graph(filename,start_node)
            else:
                InputOutput.save_text_to_file("",filename)

    def openTPTPGrammarFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open TPTP Grammar File", "","TPTP Grammar File (*.txt);;")
        self.graphBuilder = GraphBuilder.TPTPGraphBuilder()
        self.graphBuilder.run(filename)
        self.initTreeView(self.graphBuilder)