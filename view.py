from tkinter import *
#import TreeBuilder

def build_view(TreeBuilder):
    colours = ['red','green','orange','white','yellow','blue']

    r = 0
    for node in TreeBuilder.nodes_dictionary:
        Label(text=node.value, relief=RIDGE,width=45).grid(row=r,column=0)
        Entry(bg=colours[1], relief=SUNKEN,width=10).grid(row=r,column=1)
        r = r + 1

    mainloop()

def scrollbar(Treebuilder):
    master = Tk()

    scrollbar = Scrollbar(master)
    scrollbar.pack(side=RIGHT, fill=Y)

    listbox = Listbox(master, width=45,yscrollcommand=scrollbar.set)
    for node in Treebuilder.nodes_dictionary:
        var1 = IntVar()
        listbox.insert(END, str(node.value))
    listbox.pack(side=LEFT, fill=BOTH)

    scrollbar.config(command=listbox.yview)

    master.geometry("500x500")
    master.mainloop()

