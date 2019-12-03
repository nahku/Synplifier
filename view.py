from tkinter import *
from tkinter import filedialog
#import TreeBuilder

def build_view(TreeBuilder):
    colours = ['red','green','orange','white','yellow','blue']

    r = 0
    for node in TreeBuilder.nodes_dictionary:
        Label(text=node.value, relief=RIDGE,width=45).grid(row=r,column=0)
        Entry(bg=colours[1], relief=SUNKEN,width=10).grid(row=r,column=1)
        r = r + 1

    mainloop()


def NewFile():
    print("New File!")
def OpenFile():
    name = filedialog.askopenfilename(filetypes = (("Text File", "*.txt"),("All Files","*.*")))
    print(name)
def About():
    print("This is a simple example of a menu")

def scrollbar(Treebuilder):
    master = Tk()

    menu = Menu(master)

    filemenu = Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="New", command=NewFile)
    filemenu.add_command(label="Open...", command=OpenFile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=master.quit)

    helpmenu = Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About...", command=About)
    master.config(menu=menu)

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


