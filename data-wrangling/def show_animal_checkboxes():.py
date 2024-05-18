def show_animal_checkboxes():
    if exclude_animals_var.get():
        new_window = tk.Toplevel(root)
        new_window.title("Select Animals to Exclude")

        animal_vars = []
        for i in range(32):
            var = tk.BooleanVar()
            animal_vars.append(var)
            checkbutton = tk.Checkbutton(new_window, text=f"Animal {i+1}", variable=var)
            checkbutton.pack()

exclude_animals_checkbutton = tk.Checkbutton(root, text="Exclude Animals", variable=exclude_animals_var, command=show_animal_checkboxes)