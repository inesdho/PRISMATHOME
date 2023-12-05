import tkinter as tk
from tkinter import ttk

def create_gui():
    # Create the main window
    root = tk.Tk()
    root.title("PRISM@Home")

    # Set the window size
    root.geometry("800x400")

    # Logout Button
    logout_button = tk.Button(root, text="Log out")
    logout_button.place(relx=0.9, rely=0.01)  # Position the logout button above the frames

    # Left Frame for Scenario Selection
    left_frame = tk.Frame(root, bd=2, relief="sunken", padx=5, pady=5)
    left_frame.place(relx=0.02, rely=0.09, relwidth=0.46, relheight=0.50)  # Adjusted the rely value

    tk.Label(left_frame, text="Scenario name :").pack(anchor="nw")
    scenario_combobox = ttk.Combobox(left_frame, values=["Example", "Exemple 2", "Exemple 3"], state="readonly", width=30)
    scenario_combobox.set("Example")
    scenario_combobox.pack(fill="x")

    modify_button = tk.Button(left_frame, text="Modify the configuration")
    modify_button.pack(side="bottom", fill="x")

    # Right Frame for Scenario Creation
    right_frame = tk.Frame(root, bd=2, relief="sunken", padx=5, pady=5)
    right_frame.place(relx=0.50, rely=0.09, relwidth=0.48, relheight=0.50)  # Adjusted the rely value

    tk.Label(right_frame, text="Scenario name :").pack(anchor="nw")
    name_entry = tk.Entry(right_frame)
    name_entry.pack(fill="x")

    tk.Label(right_frame, text="Description :").pack(anchor="nw")
    description_entry = tk.Entry(right_frame)
    description_entry.pack(fill="x")

    create_button = tk.Button(right_frame, text="Create a configuration")
    create_button.pack(side="bottom", fill="x")

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()