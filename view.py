from tkinter import *
from tkinter import filedialog
from tkinter import ttk
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
    table["columns"] = ("one", "two")
    table.column("one", width=100)
    table.column("two", width=100)
    table.heading("one", text="Production Type")
    table.heading("two", text="Production")


    for node in treeBuilder.nodes_dictionary.values():
        if(node.rule_type == TreeBuilder.RuleType.GRAMMAR):
            id = table.insert("",1,node.value,text=node.value)

            r = 0
            for production in node.productions_list.list:
                # node production property to string umsetzen
                table.insert(id,"end",node.value + " " + str(r),text="",values=("GRAMMAR",treeBuilder.get_production_string(production)))
                r = r + 1
        #Label(text=node.value, relief=RIDGE, width=45).grid(row=r, column=0)
        #Entry(bg=colours[1], relief=SUNKEN, width=10).grid(row=r, column=1)


    #table.insert("", 0, text="Line 1", values=("1A", "1b"))

    id2 = table.insert("", 1, "dir2", text="<TPTP_file>")
    table.insert(id2, "end", "dir 2", text="", values=("GRAMMAR", "<TPTP_Input>*"))

    ##alternatively:
    table.insert("", 3, "dir3", text="Dir 3")
    table.insert("dir3", 3, text=" sub dir 3", values=("3A", " 3B"))

    table.pack()

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


