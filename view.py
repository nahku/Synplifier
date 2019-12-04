from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PyQt5.QtWidgets import QApplication, QLabel
from tkinter import tix
import TreeBuilder
def build_view(TreeBuilder):
    colours = ['red','green','orange','white','yellow','blue']



    mainloop()


def NewFile():
    print("New File!")
def OpenTPTPGrammarFile():
    file = filedialog.askopenfile(filetypes = (("Text File", "*.txt"),("All Files","*.*")),mode = "r")
    print(file)
def OpenControlFile():
    file = filedialog.askopenfile(filetypes = (("Text File", "*.txt"),("All Files","*.*")),mode = "r")
    print(file)

def CreateControlFile():
    file = filedialog.askopenfile(filetypes=(("Text File", "*.txt"), ("All Files", "*.*")), mode="r")
    print(file)
def About():
    print("This is a simple example of a menu")

def selectItem(self, item):
    print(item, self.cl.getstatus(item))

def scrollbar(treeBuilder):
    master = Tk()
    master.title("TPTP Sublanguage Extractor")
    menu = Menu(master)

    filemenu = Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="New", command=NewFile)
    filemenu.add_command(label="Open TPTP Grammar File", command=OpenTPTPGrammarFile)
    filemenu.add_command(label="Reduce TPTP Grammar with Control File", command=OpenControlFile)
    filemenu.add_command(label="Produce Control File from Selection", command=CreateControlFile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=master.quit)

    helpmenu = Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About...", command=About)
    master.config(menu=menu)


    table = ttk.Treeview(master)
    table.heading('#0', text='Non Terminal')
    table.column("#0", width=220, stretch=NO)
    table["columns"] = ("one", "two")
    table.column("one",width=100, stretch= NO)
    table.column("two")
    table.heading("one", text="Production Type")
    table.heading("two", text="Production")

    exists = set()
    for node in treeBuilder.nodes_dictionary.values():
        if(node.value not in exists):
            exists.add(node.value)
            id = table.insert("",1,node.value,text=node.value)
            #print("")
        else:
            id = node.value
        r = 0
        rule_type = ""
        if (node.rule_type == TreeBuilder.RuleType.GRAMMAR):
            rule_type = "GRAMMAR"
        elif (node.rule_type == TreeBuilder.RuleType.STRICT):
            rule_type = "STRICT"
        elif (node.rule_type == TreeBuilder.RuleType.MACRO):
            rule_type = "MACRO"
        elif (node.rule_type == TreeBuilder.RuleType.TOKEN):
            rule_type = "TOKEN"
        for production in node.productions_list.list:
            table.insert(id,"end",node.value + rule_type + str(r),text="",values=(rule_type,treeBuilder.get_production_string(production)))
            r = r + 1
    table.pack(expand=True, fill='both')

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
    master.mainloop()


