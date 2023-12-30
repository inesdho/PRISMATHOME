"""!
@file input_manager.py
@brief This file allows to create a custom entry input with an input control (ex : nb of characters min and max, default
value, password management, type of characters that are accepted etc...)
@author Naviis-Brain
@version 1.0
@date
"""

import tkinter as tk
from tkinter import ttk

# Default min and max value for the number of characters allowed on the entry
NB_MIN_CHAR = 0
NB_MAX_CHAR = 100

class Input:
    """!
    @brief The __init__ function set the variable depending on the user input and create the frame that wil contain the
    entry
    @param
    self : the instance
    master : the frame in witch the entry will be located
    min : minimal number of character allowed on the entry
    min : maximal number of character allowed on the entry
    is_password : determine if the entry is to be considered a password entry (by dfault not)
    is_fill_x : determine if the entry has to be packed in order to fill the x value of the frame (by dfault not)
    has_special_char : determine if the entry can allow special character or not (by dfault not)
    default_text : the text that will be displayed when the entry is initialized
    @return Nothing
    """
    def __init__(self, master, min=NB_MIN_CHAR, max=NB_MAX_CHAR, is_password=None, is_fill_x=None, has_width=None,
                 has_special_char=None, default_text=None):

        # Creation of the frame that will contain the entry
        self.master = master
        self.frame = ttk.Frame(self.master)

        # If the user set a minimal character value allowed, it will be saved otherwise the default value is saved
        if not min == NB_MIN_CHAR:
            self.min = min
        else:
            self.min = NB_MIN_CHAR

        # If the user set a maximal character value allowed, it will be saved otherwise the default value is saved
        if not max == NB_MAX_CHAR:
            self.max = max
        else:
            self.max = NB_MAX_CHAR

        # If the user set a password value it will be saved, otherwise is_password is set to false
        if not is_password is None:
            self.is_password = is_password
        else:
            self.is_password = False

        # If the user set a fill_x value it will be saved, otherwise is_fill_x is set to false
        if not is_fill_x is None:
            self.is_fill_x = is_fill_x
        else:
            self.is_fill_x = False

        # If the user set a has_width value it will be saved, otherwise has_width stays at None
        if not has_width is None:
            self.has_width = has_width
        else:
            self.has_width = None

        # If the user set a has_special_char value it will be saved, otherwise has_special_char is set to false
        if not has_special_char is None:
            self.has_special_char = has_special_char
        else:
            self.has_special_char = False

        # If the user set a default_text value it will be saved, otherwise default_text is set to an empty char
        if not default_text is None:
            self.default_text = default_text
        else:
            self.default_text = ""

        # Start the creation of the entry
        self.create_an_entry()

    """!
    @brief The create_an_entry function creates an entry based on the values set by the __init__ function
    @param 
    self : the instance
    @return Nothing
    """
    def create_an_entry(self):
        # Pack this frame into the master frame
        self.frame = ttk.Frame(self.master)
        self.frame.pack()

        # Creation of a variable that will hold the value of the entry and can be modified by the code
        self.entry_var = tk.StringVar()
        self.entry_var.trace_add("write", self.on_entry_change)

        # Checking if the entry needs to be used for a password
        if self.is_password:
            # If the entry is for a password the visible values will only be *
            self.entry = ttk.Entry(self.frame, show="*", textvariable=self.entry_var, width=self.has_width)
        else:
            self.entry = ttk.Entry(self.frame, textvariable=self.entry_var, width=self.has_width)

        # Insertion of the default text in the entry bar
        self.entry.insert(-1, self.default_text)

        # Checking if the entry needs to be packed according to "x"
        if self.is_fill_x:
            # If yes the entry is packed with the following parameters
            self.entry.pack(expand=tk.TRUE, fill="x")
        else:
            # Otherwise the entry is packed using some padding
            self.entry.pack(pady=10)

        # Checking if the entry needs to be forbid the special char
        if self.has_special_char == False:
            # If yes the entry is configured
            self.entry.configure(validate="key", validatecommand=self.check_entry)

        # Binding each key use to the function which_key
        self.entry.bind("<Key>", self.which_key)

    """!
    @brief This function saves the key pressing event into a variable
    @param 
    self : the instance
    event : the key pressing event
    @return Nothing
    """
    def which_key(self, event):
        self.key=event

    """!
    @brief This function checks if the key pressed is authorized or not
    @param 
    self : the instance
    @return A char if it is allowed
    """
    def check_entry(self):
        # Checked if the char meets the requirements
        return (self.key.char in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ") \
            or (self.key.keysym == "BackSpace")

    """!
    @brief This function returns the entry value
    @param 
    self : the instance
    @return The entry value
    """
    def get(self):
        return self.entry.get()

    """!
    @brief This function checks for each key pressing events if the length of the char chain is sufficient or too much.
    If the length is not sufficient a message is displayed, if the length is too much no more characters can be added.
    @param 
    self : the instance
    @return The entry value
    """
    def on_entry_change(self, *args):
        entry_text = self.entry.get()
        # Checking if the length of the entry is sufficient
        if len(entry_text) < self.min:
            # Doesn't allow to have a value under the minimum character required and so displays a message
            self.entry_var.set("Require at least " + str(self.min) + " character(s)")
        # Checking if the length of the entry is too much
        if len(entry_text) > self.max:
            # Doesn't allow to have a value under the minimum character required and so doesn't allow any more
            # characters to be typed
            self.entry_var.set(entry_text[:self.max])