import xml.etree.ElementTree as ET
from tkinter import filedialog, StringVar
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json

# Creates the window
window = ttk.Window(themename="darkly")
window.title("Yamma's XML Editor")
window.geometry("936x257")
window.resizable("false","false")

# Creates the main frame
mainFrame = ttk.Frame(window)
mainFrame['padding'] = 15
mainFrame['borderwidth'] = 2
mainFrame['relief'] = 'groove'
mainFrame.grid(column=0, row=0)

#Creates Variable Frame
variableFrame = ttk.Frame(mainFrame)
variableFrame['padding'] = 5
variableFrame.grid(column=1, row=0, padx=(0,5))

# Editing frame
editingFrame = ttk.Frame(mainFrame)
editingFrame['padding'] = 5
editingFrame.grid(column=0, row=1, padx=(0,5))

# Creates the treeview
treeview = ttk.Treeview(mainFrame, columns=("attributes", "text"))
treeview.heading("#0", text="Tag")
treeview.heading("attributes", text="Attributes")
treeview.heading("text", text="Text")
treeview.column("text", width=400)
treeview.grid(column=0, row=0, padx=(0,5))

# Tag Changed event
def tagChanged(var, index, mode):
    if tagVar.get() != "":
        treeview.item(selectedItem, text=tagVar.get())

# Tag GUI items for edit and variable string
tagLabel = ttk.Label(editingFrame, text="Tag: ")
tagLabel.grid(column=0, row=0)
tagVar = StringVar()
tagVar.trace_add('write', tagChanged)
tagEntry = ttk.Entry(editingFrame, textvariable=tagVar)
tagEntry.grid(column=1, row=0)

# Attribute Changed event
def attributeChanged(var, index, mode):
    if attributeVar.get() != "":
        treeview.item(selectedItem, values=(attributeVar.get(), details[1]))

# Attribute GUI items for edit and variable string
attributeLabel = ttk.Label(editingFrame, text="Attributes: ")
attributeLabel.grid(column=2, row=0)
attributeVar = StringVar()
attributeVar.trace_add('write', attributeChanged)
attributeEntry = ttk.Entry(editingFrame, textvariable=attributeVar)
attributeEntry.grid(column=3, row=0)

# Text Changed event
def textChanged(var, index, mode):
    if textVar.get() != "":
        treeview.item(selectedItem, values=(details[0], textVar.get()))

# Text GUI items for edit and variable string
textLabel = ttk.Label(editingFrame, text="Text: ")
textLabel.grid(column=4, row=0)
textVar = StringVar()
textVar.trace_add('write', textChanged)
textEntry = ttk.Entry(editingFrame, textvariable=textVar)
textEntry.grid(column=5, row=0)

# Get XML file
def pick_xml():
    # try to open file
    while True:
        try:
            openWindow = ttk.Window(themename="darkly")
            openWindow.withdraw()
            global xmlPath
            xmlPath = filedialog.askopenfilename(title="Select an XML file", filetypes=[("XML Files", "*.xml;")])
            # image not selected throw error
            if not xmlPath:
                raise FileNotFoundError()
            break
        except FileNotFoundError:
            pickButton.configure(bootstyle=DANGER)
            pickButton.grid(column=0, row=0)
            break
    # if file selected, open it and display success
    if (xmlPath != ""):
        build_tree()
        pickButton.configure(bootstyle=SUCCESS)
        pickButton.grid(column=0, row=0)
    openWindow.destroy()

#Item selection event
def item_selected(event):
    global selectedItem, details
    selectedItem = treeview.selection()[0]
    details = treeview.item(selectedItem, "values")

    #updates editing fields with selected item details
    tagEntry.delete(0,END)
    tagEntry.insert(0,treeview.item(selectedItem, "text"))
    attributeEntry.delete(0,END)
    attributeEntry.insert(0,details[0])
    textEntry.delete(0,END)
    textEntry.insert(0,details[1])

# Bind the item selection event to the treeview 
treeview.tag_bind("mytag", "<<TreeviewSelect>>", item_selected)

#initial build of tree after selecting a file
def build_tree():
    global tree, root
    tree = ET.parse(xmlPath)  
    root = tree.getroot()
    # Build Tree for XML
    counter = 0
    head = treeview.insert('', ttk.END, text=root.tag, values=(root.attrib, root.text, counter), tags=("mytag",))
    counter += 1
    for tail in root:     
        child = treeview.insert(head, ttk.END, text=tail.tag,  values=(tail.attrib, tail.text, counter), tags=("mytag",))
        counter += 1
        for subtail in tail:
            treeview.insert(child, ttk.END, text=subtail.tag,  values=(subtail.attrib, subtail.text, counter), tags=("mytag",))
            counter += 1

#Save the updated XML file
def save_xml():
    for head in treeview.get_children():
        root.tag = treeview.item(head, "text")
        root.attrib = json.loads(treeview.item(head, "values")[0].replace("'",'"'))
        root.text = treeview.item(head, "values")[1]

        tailCounter = 0
        for tail in treeview.get_children(head):
            root[tailCounter].tag = treeview.item(tail, "text")
            root[tailCounter].attrib = json.loads(treeview.item(tail, "values")[0].replace("'",'"'))
            root[tailCounter].text = treeview.item(tail, "values")[1] 
            subtailCounter = 0
            for subtail in treeview.get_children(tail):
                root[tailCounter][subtailCounter].tag = treeview.item(subtail, "text")
                root[tailCounter][subtailCounter].attrib = json.loads(treeview.item(subtail, "values")[0].replace("'",'"'))
                root[tailCounter][subtailCounter].text = treeview.item(subtail, "values")[1]
                subtailCounter += 1
            tailCounter += 1
    try:
        saveWindow = ttk.Window(themename="darkly")
        saveWindow.withdraw()

        save_path = filedialog.asksaveasfilename(title="Save as", defaultextension=".xml", filetypes=[("XML files", "*.xml")])

        if not save_path:
            raise ValueError()
        tree.write(save_path)
    except ValueError:
        saveButton.configure(bootstyle=DANGER)
        saveWindow.destroy()
        return
    saveButton.configure(bootstyle=SUCCESS)
    saveWindow.destroy()

#buttons 
pickButtonContainer = ttk.Frame(variableFrame, borderwidth=1, relief='groove')
pickButton = ttk.Button(pickButtonContainer, text="Pick XML", command=pick_xml)
pickButton.grid(column=0, row=0)

saveButtonContainer = ttk.Frame(variableFrame, borderwidth=1, relief='groove')
saveButton = ttk.Button(saveButtonContainer, text="Save XML", command=save_xml)
saveButton.grid(column=0, row=0)

pickButtonContainer.grid(column=1, row=0, pady=5)
saveButtonContainer.grid(column=1, row=1, pady=5)

# runs the program
window.mainloop()