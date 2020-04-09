import copy
from collections import namedtuple
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAction, QMainWindow, QWidget, QMessageBox, QFileDialog, QMenuBar, QTreeWidget, \
    QTreeWidgetItem, QVBoxLayout, QInputDialog, QLineEdit
import GraphBuilder
import Input
import Output


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
        self.init_gui()

    def init_gui(self):
        import_tptp_file_action = QAction('&Import TPTP syntax file', self)
        import_tptp_file_action.setShortcut('Ctrl+O')
        import_tptp_file_action.triggered.connect(self.load_tptp_syntax_file)

        import_tptp_file_from_web_action = QAction('&Import TPTP syntax file from web', self)
        import_tptp_file_from_web_action.setShortcut('Ctrl+I')
        import_tptp_file_from_web_action.triggered.connect(self.get_tptp_syntax_from_web)

        save_with_control_file_action = QAction('&Reduce and save TPTP syntax with control file', self)
        save_with_control_file_action.setShortcut('Ctrl+R')
        save_with_control_file_action.triggered.connect(self.output_tptp_syntax_from_control_file_without_comments)

        save_tptp_grammar_file_from_selection_action = QAction('&Reduce and save TPTP syntax with selection', self)
        save_tptp_grammar_file_from_selection_action.setShortcut('Ctrl+R')
        save_tptp_grammar_file_from_selection_action.triggered.connect(self.create_tptp_syntax_file_from_selection_without_comments)

        produce_reduced_tptp_grammar_action = QAction('&Reduce TPTP syntax with selection', self)
        produce_reduced_tptp_grammar_action.setShortcut('Ctrl+B')
        produce_reduced_tptp_grammar_action.triggered.connect(self.reduce_tptp_syntax_with_selection)

        save_control_file_action = QAction('&Produce and save control file from selection', self)
        save_control_file_action.setShortcut('Ctrl+D')
        save_control_file_action.triggered.connect(self.output_control_file)

        toggle_comments_action = QAction('&Toggle comments', self)
        toggle_comments_action.setShortcut('Ctrl+C')
        toggle_comments_action.triggered.connect(self.toggle_comments)

        import_control_file_action = QAction('&Import control file', self)
        import_control_file_action.setShortcut('Ctrl+C+I')
        import_control_file_action.triggered.connect(self.load_control_file)

        save_with_control_file_comments_action = QAction('&Reduce and save TPTP syntax with control file with external comment syntax', self)
        save_with_control_file_comments_action.triggered.connect(self.create_tptp_syntax_from_control_file_with_comments)

        save_tptp_grammar_file_from_selection_comments_action = QAction('&Reduce and save TPTP syntax from selection with external comment syntax', self)
        save_tptp_grammar_file_from_selection_comments_action.triggered.connect(self.create_tptp_syntax_file_from_selection_with_comments)

        menubar = QMenuBar()
        self.setMenuBar(menubar)
        menubar.setNativeMenuBar(False)

        import_menu = menubar.addMenu("Import syntax")
        import_menu.addAction(import_tptp_file_action)
        import_menu.addAction(import_tptp_file_from_web_action)

        save_menu = menubar.addMenu("Save syntax")
        save_menu.addAction(save_tptp_grammar_file_from_selection_action)
        save_menu.addAction(save_with_control_file_action)
        save_menu.addSeparator()
        save_menu.addAction(save_with_control_file_comments_action)
        save_menu.addAction(save_tptp_grammar_file_from_selection_comments_action)

        reduce_menu = menubar.addMenu("Reduce")
        reduce_menu.addAction(produce_reduced_tptp_grammar_action)

        control_file_menu = menubar.addMenu("Control file")
        control_file_menu.addAction(import_control_file_action)
        control_file_menu.addAction(save_control_file_action)

        view_menu = menubar.addMenu("View")
        view_menu.addAction(toggle_comments_action)

        self.setWindowTitle('TPTP sub-syntax extractor')
        self.showMaximized()

    def init_tree_view(self) -> None:
        self.treeView = QTreeWidget()
        self.treeView.setHeaderLabels(['Non Terminal', 'Production Type', 'Production'])
        nodes_list = list(self.graphBuilder.nodes_dictionary.values())
        nodes_list.sort(key=lambda x: x.position)
        for node in nodes_list:
            if node.position >= 0:
                rule_type = ""
                if node.rule_type == GraphBuilder.RuleType.GRAMMAR:
                    rule_type = "GRAMMAR"
                elif node.rule_type == GraphBuilder.RuleType.STRICT:
                    rule_type = "STRICT"
                elif node.rule_type == GraphBuilder.RuleType.MACRO:
                    rule_type = "MACRO"
                elif node.rule_type == GraphBuilder.RuleType.TOKEN:
                    rule_type = "TOKEN"
                item = QTreeWidgetItem([node.value, rule_type, ''])
                item.setCheckState(0, QtCore.Qt.Unchecked)

                light_gray = QColor(237, 244, 248)
                item.setBackground(0, light_gray)
                item.setBackground(1, light_gray)
                item.setBackground(2, light_gray)
                for production in node.productions_list.list:
                    child_item = QTreeWidgetItem(['', '', Output.get_production_string(production)])
                    child_item.setCheckState(0, QtCore.Qt.Checked)
                    item.addChild(child_item)
                if node.comment_block is not None:
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

    def toggle_comments(self):
        """Shows/hides comments in gui.

        """
        new_status = not self.commentStatus
        if self.treeView is not None:
            for item in self.treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                flags = item.flags()
                if not (Qt.ItemIsUserCheckable & flags):
                    item.setHidden(new_status)
            self.commentStatus = new_status

    def check_start_symbol(self, start_symbol: str):
        for item in self.treeView.findItems(start_symbol, Qt.MatchFixedString | Qt.MatchRecursive):
            item.setCheckState(0, QtCore.Qt.Checked)

    def load_control_file(self):
        """Loads control file and checks tree view items accordingly.

        """
        if self.treeView is not None:
            control_filename, _ = QFileDialog.getOpenFileName(None, "Open Control File", "", "Control File (*.txt);;")

            if control_filename:
                # uncheck all left symbols, check all right symbols
                for item in self.treeView.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                    if item.parent() is None:
                        flags = item.flags()
                        if Qt.ItemIsUserCheckable & flags:
                            # item is not a comment
                            item.setCheckState(0, QtCore.Qt.Unchecked)
                    else:
                        item.setCheckState(0, QtCore.Qt.Checked)

                disable_rules_string = Input.read_text_from_file(control_filename)

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
                                # if child exists
                                if child is not None:
                                    child = item.child(index)
                                    child.setCheckState(0, QtCore.Qt.Unchecked)

    def output_control_file(self):
        try:
            control_string, _ = self.produce_control_file()
            filename, _ = QFileDialog.getSaveFileName(None, "QFileDialog.getOpenFileName()", "",
                                                      "Control File (*.txt);;")
            Output.save_text_to_file(control_string, filename)
        except NoStartSymbolError:
            QMessageBox.about(self, "Error", "A start symbol has to be selected")
        except MultipleStartSymbolsError:
            QMessageBox.about(self, "Error", "Multiple start symbols are not allowed")
        except NoImportedGrammarError:
            QMessageBox.about(self, "Error", "No grammar imported")

    def produce_control_file(self):
        """Produces control file string from gui selection.

        :return: control file string and
        :rtype: (str,str)
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

            if (item.checkState(0) == 0) and (parent is not None):
                rule_type = parent.text(1)
                entry = None
                if rule_type == "GRAMMAR":
                    entry = Entry(parent.text(0), GraphBuilder.RuleType.GRAMMAR)
                elif rule_type == "STRICT":
                    entry = Entry(parent.text(0), GraphBuilder.RuleType.STRICT)
                elif rule_type == "MACRO":
                    entry = Entry(parent.text(0), GraphBuilder.RuleType.MACRO)
                elif rule_type == "TOKEN":
                    entry = Entry(parent.text(0), GraphBuilder.RuleType.TOKEN)
                parent = item.parent()
                indexOfChild = parent.indexOfChild(item)
                if entry not in entry_dictionary:
                    entry_dictionary[entry] = [indexOfChild]
                else:
                    entry_dictionary[entry].append(indexOfChild)
            elif (item.checkState(0) > 0) and (parent is None):
                start_symbol_selection.append(item.text(0))

        # if multiple start symbols are selected
        multiple_start_symbols = not all(elem == start_symbol_selection[0] for elem in start_symbol_selection)
        if multiple_start_symbols:
            raise MultipleStartSymbolsError("Multiple start symbols have been selected")

        if len(start_symbol_selection) == 0:
            raise NoStartSymbolError("Multiple start symbols have been selected")

        control_string = start_symbol_selection[0] + "\n"
        for key, value in entry_dictionary.items():
            rule_string = ""
            if key.rule_type == GraphBuilder.RuleType.GRAMMAR:
                rule_string = "::="
            elif key.rule_type == GraphBuilder.RuleType.STRICT:
                rule_string = ":=="
            elif key.rule_type == GraphBuilder.RuleType.MACRO:
                rule_string = ":::"
            elif key.rule_type == GraphBuilder.RuleType.TOKEN:
                rule_string = "::-"
            control_string += key.value + "," + rule_string + ","
            control_string += ','.join(map(str, value))  # add indexes separated by comma
            control_string += "\n"
        return control_string, start_symbol_selection[0]

    def reduce_tptp_syntax_with_selection(self):
        try:
            control_string, start_symbol = self.produce_control_file()
            self.graphBuilder.disable_rules(control_string)
            self.init_tree_view()
            self.check_start_symbol(start_symbol)
        except NoStartSymbolError:
            QMessageBox.about(self, "Error", "A start symbol has to be selected")
        except MultipleStartSymbolsError:
            QMessageBox.about(self, "Error", "Multiple start symbols are not allowed")
        except NoImportedGrammarError:
            QMessageBox.about(self, "Error", "No grammar imported")

    def create_tptp_syntax_file_from_selection_with_comments(self):
        self.create_tptp_syntax_file_from_selection(with_comments=True)

    def create_tptp_syntax_file_from_selection_without_comments(self):
        self.create_tptp_syntax_file_from_selection(with_comments=False)

    def create_tptp_syntax_file_from_selection(self, with_comments: bool):
        filename, _ = QFileDialog.getSaveFileName(None, "Save TPTP Grammar File", "", "TPTP Grammar File(*.txt);;")
        if filename:
            try:
                control_string, start_symbol = self.produce_control_file()
                graphBuilder = GraphBuilder.TPTPGraphBuilder()
                graphBuilder.nodes_dictionary = copy.deepcopy(self.graphBuilder.nodes_dictionary)
                graphBuilder.init_tree(start_symbol)
                graphBuilder.disable_rules(control_string)
                start_node = graphBuilder.nodes_dictionary.get(
                    GraphBuilder.Node_Key("<start_symbol>", GraphBuilder.RuleType.GRAMMAR))
                if start_node is not None:
                    if with_comments:
                        Output.save_ordered_rules_from_graph_with_comments(filename, start_node)
                    else:
                        Output.save_ordered_rules_from_graph(filename, start_node)
                else:
                    Output.save_text_to_file("", filename)
            except NoStartSymbolError:
                QMessageBox.about(self, "Error", "A start symbol has to be selected")
            except MultipleStartSymbolsError:
                QMessageBox.about(self, "Error", "Multiple start symbols are not allowed")
            except NoImportedGrammarError:
                QMessageBox.about(self, "Error", "No grammar imported")

    def create_tptp_syntax_from_control_file_with_comments(self):
        self.create_tptp_syntax_from_control_file(with_comments=True)

    def output_tptp_syntax_from_control_file_without_comments(self):
        self.create_tptp_syntax_from_control_file(with_comments=False)

    def create_tptp_syntax_from_control_file(self, with_comments: bool):
        control_filename, _ = QFileDialog.getOpenFileName(None, "Open Control File", "", "Control File (*.txt);;")
        if control_filename:
            save_filename, _ = QFileDialog.getSaveFileName(None, "Save TPTP Grammar File", "",
                                                           "TPTP Grammar File (*.txt);;")
            if save_filename:
                control_string = Input.read_text_from_file(control_filename)
                if self.treeView is not None:
                    graphBuilder = GraphBuilder.TPTPGraphBuilder()
                    graphBuilder.nodes_dictionary = copy.deepcopy(self.graphBuilder.nodes_dictionary)
                    graphBuilder.init_tree(control_string.splitlines()[0])
                    graphBuilder.disable_rules(control_string)
                    start_node = graphBuilder.nodes_dictionary.get(
                        GraphBuilder.Node_Key("<start_symbol>", GraphBuilder.RuleType.GRAMMAR))
                    if start_node is not None:
                        if with_comments:
                            Output.save_ordered_rules_from_graph_with_comments(save_filename, start_node)
                        else:
                            Output.save_ordered_rules_from_graph(save_filename, start_node)
                    else:
                        Output.save_text_to_file("", save_filename)
                else:
                    QMessageBox.about(self, "Error", "No grammar imported")

    def load_tptp_syntax_file(self):
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
                    self.create_tptp_view(start_symbol, Input.read_text_from_file(filename))

    def get_tptp_syntax_from_web(self):
        file = Input.import_tptp_syntax_from_web()
        start_symbol, okPressed = QInputDialog.getText(self, "Input the desired start symbol", "Start Symbol:",
                                                       QLineEdit.Normal, "<TPTP_file>")
        if okPressed and start_symbol != '':
            self.create_tptp_view(start_symbol, file)

    def create_tptp_view(self, start_symbol:str, file:str):
        self.graphBuilder = GraphBuilder.TPTPGraphBuilder()
        self.graphBuilder.run(start_symbol=start_symbol, file=file)
        self.init_tree_view()
        self.check_start_symbol(start_symbol)

