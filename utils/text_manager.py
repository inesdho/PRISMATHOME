"""!
@file text_manager.py
@brief This file allows to create a custom text input with an input control (ex : nb of characters min and max, default
value, type of characters that are accepted etc...)
@author Naviis-Brain
@version 1.0
@date
"""

import tkinter as tk
from tkinter import ttk, messagebox

# Default min and max value for the number of characters allowed in the text widget
NB_MIN_CHAR = 0
NB_MAX_CHAR = 100

class TextManager:
    def __init__(self, frame, min=NB_MIN_CHAR, max=NB_MAX_CHAR, auto_pack=None, has_width=None, has_height=None,
                 default_text=None, **kwargs):
        """!
        @brief The __init__ function set the variable depending on the user input and create the frame that wil contain the
        entry
        @param self : the instance
        @param frame : the frame in witch the text will be located
        @param min : minimal number of character allowed on the text
        @param min : maximal number of character allowed on the text
        @param auto_pack : determine if the text has to be packed by this instance or no (by default yes)
        @param has_width : determine if the text has to be of a certain width (by default no width is assigned)
        @param has_height : determine if the text has to be of a certain height (by default no height is assigned)
        @param default_text : the text that will be displayed when the entry is initialized
        @return Nothing
        """

        # Saving the frame in which the entry will be created
        self.frame = frame

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

        # If the user set a auto_pack value it will be saved, otherwise auto_pack is set to true
        if not auto_pack is None:
            self.auto_pack = auto_pack
        else:
            self.auto_pack = True

        # If the user set a has_width value it will be saved, otherwise has_width stays at None
        if not has_width is None:
            self.has_width = has_width
        else:
            self.has_width = None

        # If the user set a has_height value it will be saved, otherwise has_height stays at None
        if not has_height is None:
            self.has_height = has_height
        else:
            self.has_height = None

        # If the user set a default_text value it will be saved, otherwise default_text is set to an empty char
        if not default_text is None:
            self.default_text = default_text
        else:
            self.default_text = ""

        # Set the focs of the user to true so that no error message will be display yet regarding the length of the
        # text char
        self.focus = True

        # Start the creation of the entry
        self.create_a_text()

    def create_a_text(self):
        """!
        @brief The create_an_text function creates an entry based on the values set by the __init__ function
        @param self : the instance
        @return Nothing
        """
        # Creation of the text widget
        self.text = tk.Text(self.frame, width=self.has_width, height=self.has_height, wrap="word")

        # Insertion of the default text in the entry bar
        self.text.insert(0.1, self.default_text)

        # Checking if the entry needs to be packed by this function
        if self.auto_pack:
            # Otherwise the entry is packed using some padding
            self.text.pack(pady=10)

        # Binding each key use to the function on_key_press
        self.text.bind("<Key>", self.which_key)

        # Binding the focus on the entry
        #self.text.bind("<FocusOut>", self.on_text_focus_out)
        #self.text.bind("<FocusIn>", self.on_text_focus_in)


    def which_key(self, event):
        """!
        @brief This function saves the key pressing event into a variable
        @param
        self : the instance
        event : the key pressing event
        @return Nothing
        """
        self.key = event

    def on_text_focus_out(self, event):
        """!
       @brief This function detects when the user exit the entry and set the focus variable to False and call the
       on_text_change function to check if the event is allowed
       @param self : the instance
       @param event : the focus out event
       @return Nothing
       """
        self.focus = False
        self.on_text_change()

    def on_text_focus_in(self, event):
        """!
        @brief This function detects when the user curser is in the entry and set the focus variable to True
        @param self : the instance
        @param event : the focus in event
        @return Nothing
        """
        self.focus = True

    def get(self):
        """!
        @brief This function returns the text value
        @param self : the instance
        @return The entry value
        """
        return self.text.get("1.0", "end-1c")

    def on_text_change(self, *args):
        """!
        @brief The on_event checks that the number of characters is inside the limits define by the user or the default
        values
        @param self : the instance
        @return Nothing
        """
        current_text = self.text.get("1.0", "end-1c")
        if len(current_text) < self.min:
            # Doesn't allow to have a value under the minimum character required and so displays a message
            messagebox.showerror("Input error", "At least {} char is required.".format(self.min))
            # Set the cursor of the user back in the text widget so that it can not be left empty
            self.text.focus_set()
        if len(current_text) > self.max:
            # Delete the last character if it's over the limit
            self.text.delete("end-2c", "end-1c")
            return "break"