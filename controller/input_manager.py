import tkinter as tk
from tkinter import ttk

class Input:
    def __init__(self, master, min, max, password):
        self.master = master
        self.frame = ttk.Frame(self.master)

        self.max = max
        self.min = min
        self.password = password

        self.create_an_entry()


    def create_an_entry(self):
        self.frame = ttk.Frame(self.master)
        self.frame.pack()

        self.entry_var = tk.StringVar()
        self.entry_var.trace_add("write", self.on_entry_change)

        if self.password:
            self.entry = ttk.Entry(self.frame, show="*", textvariable=self.entry_var)
        else:
            self.entry = ttk.Entry(self.frame, textvariable=self.entry_var)

        self.entry.pack(pady=10)

        self.entry.configure(validate="key",validatecommand=self.check_entry)
        self.entry.bind("<Key>", self.which_key)

    def which_key(self, event):
        self.key=event

    def check_entry(self):
        return (self.key.char in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") or (self.key.keysym == "BackSpace")

    def get(self):
        return self.entry.get()

    def on_entry_change(self, *args):
        entry_text = self.entry.get()
        if len(entry_text) < self.min:
            # Doesn't allow to have a value under the minimum character required
            self.entry_var.set("Require min " + str(self.min) + " character")
        if len(entry_text) > self.max:
            # Doesn't allow to have a value under the minimum character required
            self.entry_var.set(entry_text[:self.max])