import sys

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from argparse import Namespace

import main_template_analysis as t_analyze

class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(tk.END, str)
        self.widget.see(tk.END)

    def flush(self):
        pass  # This is needed for the file-like object.

def run_main_script():
    try:
        args = Namespace(
            directory=directory_entry.get(),
            start_time=start_time_entry.get(),
            end_time=end_time_entry.get(),
            morning_ramp=morning_ramp_entry.get(),
            evening_ramp=evening_ramp_entry.get(),
            night_start=night_start_entry.get(),
            ramp_duration=float(ramp_duration_entry.get()),
            DD_start_date=DD_start_date_entry.get(),
            running_average=int(running_average_entry.get())
        )

        messagebox.info("Initializing global analysis variables...")

        t_analyze.main(args, exclude_animals=exclude_animals_var.get())

        messagebox.info("Initialization complete.")


    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Damn Simple: A GUI for Simple Visualization of DAM Data")

font_size = 12

directory_label = tk.Label(root, text="Directory name (contains the data .txt files):", font=('sans',font_size, 'bold'))
directory_label.pack()
directory_entry = tk.Entry(root, font=('sans',font_size))
directory_entry.pack()

start_time_label = tk.Label(root, text="Start datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:", font=('sans',font_size, 'bold'))
start_time_label.pack()
start_time_entry = tk.Entry(root, font=('sans',font_size))
start_time_entry.pack()

end_time_label = tk.Label(root, text="End datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:", font=('sans',font_size, 'bold'))
end_time_label.pack()
end_time_entry = tk.Entry(root, font=('sans',font_size))
end_time_entry.pack()

DD_start_date_label = tk.Label(root, text="Start date for DD analysis (YYYY-MM-DD):", font=('sans',font_size, 'bold'))
DD_start_date_label.pack()
DD_start_date_entry = tk.Entry(root, font=('sans',font_size))
DD_start_date_entry.pack()

morning_ramp_label = tk.Label(root, text="Morning ramp time (HH:MM), e.g., 6:00 for 6 AM:", font=('sans',font_size, 'bold'))
morning_ramp_label.pack()
morning_ramp_entry = tk.Entry(root, font=('sans',font_size))
morning_ramp_entry.pack()

evening_ramp_label = tk.Label(root, text="Evening ramp time (HH:MM), e.g., 18:00 for 6 PM:", font=('sans',font_size, 'bold'))
evening_ramp_label.pack()
evening_ramp_entry = tk.Entry(root, font=('sans',font_size))
evening_ramp_entry.pack()

night_start_label = tk.Label(root, text="Night start time (HH:MM), e.g., 21:00 for 9 PM:", font=('sans',font_size, 'bold'))
night_start_label.pack()
night_start_entry = tk.Entry(root, font=('sans',font_size))
night_start_entry.pack()

ramp_duration_label = tk.Label(root, text="Duration of ramp in hours (e.g., 1.5):", font=('sans',font_size, 'bold'))
ramp_duration_label.pack()
ramp_duration_entry = tk.Entry(root, font=('sans',font_size))
ramp_duration_entry.pack()

running_average_label = tk.Label(root, text="Running average window size (e.g., 30):", font=('sans',font_size, 'bold'))
running_average_label.pack()
running_average_entry = tk.Entry(root, font=('sans',font_size))
running_average_entry.pack()

exclude_animals_var = tk.BooleanVar()
exclude_animals_checkbutton = tk.Checkbutton(root, text="Exclude Animals? Check for 'yes':",
                                            variable=exclude_animals_var,
                                            font=('sans',font_size))
exclude_animals_checkbutton.pack()

run_button = tk.Button(root, text="Run analysis", command=run_main_script)
run_button.pack()

output_text = tk.Text(root)
output_text.pack()

sys.stdout = TextRedirector(output_text)


root.mainloop()