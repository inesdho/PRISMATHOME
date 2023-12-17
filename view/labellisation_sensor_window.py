import tkinter as tk

# Define the main application window
root = tk.Tk()
root.title("PRISM@Home")

# Define a frame to contain the form elements
frame = tk.Frame(root)
frame.pack(expand=True, padx=20, pady=20)

# Helper function to create a labeled entry with two text boxes, one for label and one for description
def create_labeled_entry(master, label_text):
    entry_frame = tk.Frame(master)
    entry_frame.pack(fill=tk.X, pady=5)
    label = tk.Label(entry_frame, text=label_text, width=20, anchor='w')
    label.pack(side=tk.LEFT)

    label_label = tk.Label(entry_frame, text="Label :", width=10)
    label_label.pack(side=tk.LEFT)
    entry_label = tk.Entry(entry_frame, width=20)
    entry_label.pack(side=tk.LEFT, padx=5)

    description_label = tk.Label(entry_frame, text="Description :", width=10)
    description_label.pack(side=tk.LEFT)
    entry_description = tk.Entry(entry_frame, width=50)
    entry_description.pack(side=tk.LEFT, padx=5)

# Create entries for sensors
sensor_labels = ['Presence sensor 1', 'Presence sensor 2', 'Opening sensor 1', 'Pressure sensor 1']
for label in sensor_labels:
    create_labeled_entry(frame, label)

# Add navigation buttons
button_frame = tk.Frame(frame)
button_frame.pack(fill=tk.X)
back_button = tk.Button(button_frame, text="Back")
back_button.pack(side=tk.LEFT, padx=5, pady=5)
next_button = tk.Button(button_frame, text="Next")
next_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Start the application
root.mainloop()