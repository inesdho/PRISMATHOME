from tkinter import *
from tkinter.messagebox import showinfo

fenetre = Tk()

label = Label(fenetre, text="Hello World")
label.pack()


def recupere():
    showinfo("Alerte", entree.get())


value = StringVar()

value.set("Valeur")
entree = Entry(fenetre, textvariable=value, width=50)
entree.pack()

bouton = Button(fenetre, text="Valider", command=recupere)
bouton.pack()

fenetre.mainloop()
