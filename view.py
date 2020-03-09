import copy
from collections import namedtuple
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAction, QMainWindow, QWidget, QMessageBox, QFileDialog, QMenuBar, QTreeWidget, \
    QTreeWidgetItem, QVBoxLayout, QInputDialog, QLineEdit
import GraphBuilder
import InputOutput


class MultipleStartSymbolsError(Exception):
    """Multiple Start Symbols Error"""
    pass


class NoStartSymbolError(Exception):
    """No Start Symbol Error"""
    pass


class NoImportedGrammarError(Exception):
    """No Imported Grammar Error"""
    pass


class View(QMainWindow):

    def __init__(self):
        super().__init__()
        self.treeView = None
        self.graphBuilder = None
        self.commentStatus = False
        self.initUI()

    def initUI(self):
        importTPTPFileAction = QAction('&Import TPTP Grammar File', self)
        importTPTPFileAction.setShortcut('Ctrl+O')
        importTPTPFileAction.triggered.connect(self.openTPTPGrammarFile)

        importTPTPFileFromWebAction = QAction('&Import TPTP Grammar File from Web', self)
        importTPTPFileFromWebAction.setShortcut('Ctrl+I')
        importTPTPFileFromWebAction.triggered.connect(self.getTPTPFileFromWeb)

        saveWithControlFileAction = QAction('&Reduce and save TPTP Grammar with Control File', self)
        saveWithControlFileAction.setShortcut('Ctrl+R')
        saveWithControlFileAction.triggered.connect(self.outputTPTPGrammarFromControlFileWithoutComments)

        saveTPTPGrammarFileFromSelectionAction = QAction('&Save TPTP Grammar File from Selection', self)
        saveTPTPGrammarFileFromSelectionAction.setShortcut('Ctrl+R')
        saveTPTPGrammarFileFromSelectionAction.triggered.connect(self.createTPTPGrammarFileFromSelectionWithoutComments)

        produceReducedTPTPGrammarAction = QAction('&Reduce TPTP Grammar with Selection', self)
        produceReducedTPTPGrammarAction.setShortcut('Ctrl+B')
        produceReducedTPTPGrammarAction.triggered.connect(self.reduceTPTPGrammarWithSelection)

        saveControlFileAction = QAction('&Produce and save Control File from Selection', self)
        saveControlFileAction.setShortcut('Ctrl+D')
        saveControlFileAction.triggered.connect(self.outputControlFile)

        toggleCommentsAction = QAction('&Toggle Comments', self)
        toggleCommentsAction.setShortcut('Ctrl+C')
        toggleCommentsAction.triggered.connect(self.toggleComments)

        importControlFileAction = QAction('&Import Control File', self)
        importControlFileAction.setShortcut('Ctrl+C+I')
        importControlFileAction.triggered.connect(self.loadControlFile)

        saveWithControlFileCommentsAction = QAction('&Reduce and save TPTP Grammar with Control File with external Comments', self)
        saveWithControlFileCommentsAction.triggered.connect(self.outputTPTPGrammarFromControlFileWithComments)

        saveTPTPGrammarFileFromSelectionCommentsAction = QAction('&Create TPTP Grammar File from Selection with external Comments', self)
        saveTPTPGrammarFileFromSelectionCommentsAction.triggered.connect(self.createTPTPGrammarFileFromSelectionWithComments)

        menubar = QMenuBar()
        self.setMenuBar(menubar)
        menubar.setNativeMenuBar(False)

        import_menu = menubar.addMenu("Import")
        import_menu.addAction(importTPTPFileAction)
        import_menu.addAction(importTPTPFileFromWebAction)
        import_menu.addAction(importControlFileAction)

        save_menu = menubar.addMenu("Save")
        save_menu.addAction(saveTPTPGrammarFileFromSelectionAction)
        save_menu.addAction(saveWithControlFileAction)
        save_menu.addAction(saveControlFileAction)
        save_menu.addSeparator()
        save_menu.addAction(saveWithControlFileCommentsAction)
        save_menu.addAction(saveTPTPGrammarFileFromSelectionCommentsAction)

        reduce_menu = menubar.addMenu("Reduce")
        reduce_menu.addAction(produceReducedTPTPGrammarAction)

        view_menu = menubar.addMenu("View")
        view_menu.addAction(toggleCommentsAction)

        self.setWindowTitle('TPTP Grammar Reducer')
        self.showMaximized()

    def initTreeView(self, graphBuilder: GraphBuilder.TPTPGraphBuilder) -> None:
        self.treeView = QTreeWidget()
        self.treeView.setHeaderLabels(['Non Terminal', 'Production Type', 'Production'])
        nodesList = list(graphBuilder.nodes_dictionary.values())
        nodesList.sort(key=lambda x: x.position)
        for node in nodesList:
            if (node.position >= 0):
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
                if (node.comment_block is not None):
                    comment = "\n".join(node.comment_block.comment_lines)
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
        self.treeView.resizeColumnToContents(0)

    def toggleComments(self):
        """Shows/hides comments in gui.

        """
        new_status = not self.commentStatus
        if self.treeView is not None:
            for item in self.treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                flags = item.flags()
                if (not (Qt.ItemIsUserCheckable & flags)):
                    item.setHidden(new_status)
            self.commentStatus = new_status

    def loadControlFile(self):
        """Loads control file and checks tree view items accordingly.

        """
        if self.treeView is not None:
            control_filename, _ = QFileDialog.getOpenFileName(None, "Open Control File", "", "Control File (*.txt);;")

            # uncheck all left symbols, check all right symbols
            for item in self.treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                if item.parent() is None:
                    flags = item.flags()
                    if (Qt.ItemIsUserCheckable & flags):
                        #item is not a comment
                        item.setCheckState(0, QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(0,QtCore.Qt.Checked)

            if control_filename:
                disable_rules_string = InputOutput.read_text_from_file(control_filename)

                lines = disable_rules_string.splitlines()
                start_symbol = lines[0]
                for item in self.treeView.findItems(start_symbol, Qt.MatchFixedString | Qt.MatchRecursive):
                    item.setCheckState(0, QtCore.Qt.Checked)
                del lines[0]

                for i in lines:
                    data = i.split(",")
                    nt_name = data[0]
                    rule_symbol = data[1]
                    del data[0:2]
                    data = list(map(int, data))
                    rule_type_name = ""
                    if rule_symbol == "::=":
                        rule_type_name = "GRAMMAR"
                    elif rule_symbol == "::-":
                        rule_type_name = "TOKEN"
                    elif rule_symbol == ":==":
                        rule_type_name = "STRICT"
                    elif rule_symbol == ":::":
                        rule_type_name = "MACRO"

                    # find nt
                    for item in self.treeView.findItems(nt_name, Qt.MatchFixedString | Qt.MatchRecursive):
                        if item.parent() is None and item.text(1) == rule_type_name:
                            for index in data:
                                child = item.child(index)
                                #if child exists
                                if child is not None:
                                    child = item.child(index)
                                    child.setCheckState(0, QtCore.Qt.Unchecked)

    def outputControlFile(self):
        try:
            control_string, _ = self.produceControlFile()
            filename, _ = QFileDialog.getSaveFileName(None, "QFileDialog.getOpenFileName()", "",
                                                      "Control File (*.txt);;")
            InputOutput.save_text_to_file(control_string, filename)
        except NoStartSymbolError:
            QMessageBox.about(self, "Error", "A start symbol has to be selected")
        except MultipleStartSymbolsError:
            QMessageBox.about(self, "Error", "Multiple start symbols are not allowed")
        except NoImportedGrammarError:
            QMessageBox.about(self, "Error", "No grammar imported")

    def produceControlFile(self):
        """Produces control file string from gui selection.

        :return:

        :raises:
            NoImportedGrammarError: No grammar has been imported.
            MultipleStartSymbolsError: Multiple start symbols have been selected.
            NoStartSymbolError: No start symbol has been selected.
        """
        Entry = namedtuple("Entry", ["value", "rule_type"])
        entry_dictionary = {}
        start_symbol_selection = []
        if self.treeView is None:
            raise NoImportedGrammarError

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
                parent = item.parent()
                indexOfChild = parent.indexOfChild(item)
                if entry not in entry_dictionary:
                    entry_dictionary[entry] = [indexOfChild]
                else:
                    entry_dictionary[entry].append(indexOfChild)
            elif ((item.checkState(0) > 0) and (parent is None)):
                start_symbol_selection.append(item.text(0))

        # if multiple start symbols are selected
        multiple_start_symbols = not all(elem == start_symbol_selection[0] for elem in start_symbol_selection)
        if multiple_start_symbols:
            raise MultipleStartSymbolsError("Multiple start symbols have been selected")

        if (len(start_symbol_selection) == 0):
            raise NoStartSymbolError("Multiple start symbols have been selected")

        control_string = start_symbol_selection[0] + "\n"
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
        try:
            control_string, start_symbol = self.produceControlFile()
            self.graphBuilder.reduce_grammar(control_string)
            self.initTreeView(self.graphBuilder)
            self.checkStartsymbol(start_symbol)
        except NoStartSymbolError:
            QMessageBox.about(self, "Error", "A start symbol has to be selected")
        except MultipleStartSymbolsError:
            QMessageBox.about(self, "Error", "Multiple start symbols are not allowed")
        except NoImportedGrammarError:
            QMessageBox.about(self, "Error", "No grammar imported")

    def createTPTPGrammarFileFromSelectionWithComments(self):
        self.createTPTPGrammarFileFromSelection(withComments=True)

    def createTPTPGrammarFileFromSelectionWithoutComments(self):
        self.createTPTPGrammarFileFromSelection(withComments=False)

    def createTPTPGrammarFileFromSelection(self,withComments: bool):
        filename, _ = QFileDialog.getSaveFileName(None, "Save TPTP Grammar File", "", "TPTP Grammar File(*.txt);;")
        if filename:
            try:
                control_string, start_symbol = self.produceControlFile()
                graphBuilder = GraphBuilder.TPTPGraphBuilder()
                graphBuilder.nodes_dictionary = self.graphBuilder.nodes_dictionary
                graphBuilder.init_tree(start_symbol)
                self.graphBuilder.reduce_grammar(control_string)
                start_node = self.graphBuilder.nodes_dictionary.get(
                    GraphBuilder.Node("<start_symbol>", GraphBuilder.RuleType.GRAMMAR))
                if (start_node is not None):
                    if withComments:
                        InputOutput.save_ordered_rules_from_graph_with_comments(filename, start_node)
                    else:
                        InputOutput.save_ordered_rules_from_graph(filename, start_node)
                else:
                    InputOutput.save_text_to_file("", filename)
            except NoStartSymbolError:
                QMessageBox.about(self, "Error", "A start symbol has to be selected")
            except MultipleStartSymbolsError:
                QMessageBox.about(self, "Error", "Multiple start symbols are not allowed")
            except NoImportedGrammarError:
                QMessageBox.about(self, "Error", "No grammar imported")

    def outputTPTPGrammarFromControlFileWithComments(self):
        self.outputTPTPGrammarFromControlFile(withComments=True)

    def outputTPTPGrammarFromControlFileWithoutComments(self):
        self.outputTPTPGrammarFromControlFile(withComments=False)

    def outputTPTPGrammarFromControlFile(self, withComments: bool):
        control_filename, _ = QFileDialog.getOpenFileName(None, "Open Control File", "", "Control File (*.txt);;")
        if control_filename:
            save_filename, _ = QFileDialog.getSaveFileName(None, "Save TPTP Grammar File", "",
                                                           "TPTP Grammar File (*.txt);;")
            if save_filename:
                control_string = InputOutput.read_text_from_file(control_filename)
                if self.treeView is not None:
                    graphBuilder = GraphBuilder.TPTPGraphBuilder()
                    graphBuilder.nodes_dictionary = copy.deepcopy(self.graphBuilder.nodes_dictionary)
                    graphBuilder.init_tree(control_string.splitlines()[0])
                    graphBuilder.reduce_grammar(control_string)
                    start_node = graphBuilder.nodes_dictionary.get(
                        GraphBuilder.Node("<start_symbol>", GraphBuilder.RuleType.GRAMMAR))
                    if (start_node is not None):
                        if withComments:
                            InputOutput.save_ordered_rules_from_graph_with_comments(save_filename, start_node)
                        else:
                            InputOutput.save_ordered_rules_from_graph(save_filename, start_node)
                    else:
                        InputOutput.save_text_to_file("", save_filename)
                else:
                    QMessageBox.about(self, "Error", "No grammar imported")

    def openTPTPGrammarFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open TPTP Grammar File", "", "TPTP Grammar File (*.txt);;")
        # if filename is not empty
        if filename:
            start_symbol, ok_pressed = QInputDialog.getText(self, "Input the desired start symbol", "Start Symbol:",
                                                            QLineEdit.Normal, "<TPTP_file>")
            if ok_pressed:
                if start_symbol == '':
                    QMessageBox.about(self, "Error", "A start symbol has to be specified")
                else:
                    # todo check if start symbol exists
                    self.createTPTPView(start_symbol, None, filename)

    def getTPTPFileFromWeb(self):
        file = InputOutput.import_tptp_grammar_from_web()
        start_symbol, okPressed = QInputDialog.getText(self, "Input the desired start symbol", "Start Symbol:",
                                                       QLineEdit.Normal, "<TPTP_file>")
        if okPressed and start_symbol != '':
            self.createTPTPView(start_symbol, file, None)

    def createTPTPView(self, start_symbol, file=None, filename=None):
        self.graphBuilder = GraphBuilder.TPTPGraphBuilder()
        self.graphBuilder.run(start_symbol=start_symbol, file=file, filename=filename)
        self.initTreeView(self.graphBuilder)
        self.checkStartsymbol(start_symbol)

    def checkStartsymbol(self, start_symbol):
        for item in self.treeView.findItems(start_symbol, Qt.MatchFixedString | Qt.MatchRecursive):
            item.setCheckState(0, QtCore.Qt.Checked)
