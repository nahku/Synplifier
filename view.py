from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction
import sys
import GraphBuilder

def scrollbar(treeBuilder):
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()
    #
    # master = Tk()
    # master.title("TPTP Sublanguage Extractor")
    # menu = Menu(master)
    #
    # filemenu = Menu(menu)
    # menu.add_cascade(label="File", menu=filemenu)
    # filemenu.add_command(label="New", command=NewFile)
    # filemenu.add_command(label="Open TPTP Grammar File", command=OpenTPTPGrammarFile)
    # filemenu.add_command(label="Reduce TPTP Grammar with Control File", command=OpenControlFile)
    # filemenu.add_command(label="Produce Control File from Selection", command=CreateControlFile)
    # filemenu.add_separator()
    # filemenu.add_command(label="Exit", command=master.quit)
    #
    # helpmenu = Menu(menu)
    # menu.add_cascade(label="Help", menu=helpmenu)
    # helpmenu.add_command(label="About...", command=About)
    # master.config(menu=menu)
    #
    #
    # table = ttk.Treeview(master)
    # table.heading('#0', text='Non Terminal')
    # table.column("#0", width=220, stretch=NO)
    # table["columns"] = ("one", "two")
    # table.column("one",width=100, stretch= NO)
    # table.column("two")
    # table.heading("one", text="Production Type")
    # table.heading("two", text="Production")
    #
    # exists = set()
    # for node in treeBuilder.nodes_dictionary.values():
    #     if(node.value not in exists):
    #         exists.add(node.value)
    #         id = table.insert("",1,node.value,text=node.value)
    #         #print("")
    #     else:
    #         id = node.value
    #     r = 0
    #     rule_type = ""
    #     if (node.rule_type == TreeBuilder.RuleType.GRAMMAR):
    #         rule_type = "GRAMMAR"
    #     elif (node.rule_type == TreeBuilder.RuleType.STRICT):
    #         rule_type = "STRICT"
    #     elif (node.rule_type == TreeBuilder.RuleType.MACRO):
    #         rule_type = "MACRO"
    #     elif (node.rule_type == TreeBuilder.RuleType.TOKEN):
    #         rule_type = "TOKEN"
    #     for production in node.productions_list.list:
    #         table.insert(id,"end",node.value + rule_type + str(r),text="",values=(rule_type,treeBuilder.get_production_string(production)))
    #         r = r + 1
    # table.pack(expand=True, fill='both')

    #scrollbar = Scrollbar(master)
    #scrollbar.pack(side=RIGHT, fill=Y)

    #listbox = Listbox(master, width=45,yscrollcommand=scrollbar.set)
    #for node in Treebuilder.nodes_dictionary:
    #    var1 = IntVar()
    #    listbox.insert(END, str(node.value))
    #listbox.pack(side=LEFT, fill=BOTH)

    #scrollbar.config(command=listbox.yview)

    #master.geometry("500x500")
    #OpenFile()
    #master.mainloop()
    sys.exit(app.exec_())

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World")
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        openTPTPFileAction = QAction('&Open TPTP Grammar File', self)
        openTPTPFileAction.setShortcut('Ctrl+O')
        #openTPTPFileAction.setStatusTip('New document')
        openTPTPFileAction.triggered.connect(self.openTPTPGrammarFile)

        openControlFileAction = QAction('&Reduce TPTP Grammar with Control File', self)
        openControlFileAction.setShortcut('Ctrl+R')
        #openControlFileAction.setStatusTip('New document')
        openControlFileAction.triggered.connect(self.reduceTPTPGrammarWithControlFile)

        produceReducedTPTPGrammarAction = QAction('&Reduced TPTP Grammar with Selection', self)
        produceReducedTPTPGrammarAction.setShortcut('Ctrl+R')
        # openControlFileAction.setStatusTip('New document')
        produceReducedTPTPGrammarAction.triggered.connect(self.reduceTPTPGrammarWithSelection)

        produceControlFileAction = QAction('&Produce Control File from Selection', self)
        produceControlFileAction.setShortcut('Ctrl+R')
        # openControlFileAction.setStatusTip('New document')
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


        self.button.clicked.connect(self.openTPTPGrammarFile)

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

    def produceControlFile(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "QFileDialog.getOpenFileName()", "","Control File (*.txt);;")
        if fileName:
            print(fileName)