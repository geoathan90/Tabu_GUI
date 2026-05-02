import tkinter as tk
from tkinter import ttk, messagebox


def add_numbers(event=None):
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())
        result_var.set(str(a + b))
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers in both fields.")


root = tk.Tk()
root.title("Adder GUI")
root.geometry("320x240")
root.minsize(320, 240)

main = ttk.Frame(root, padding=16)
main.pack(fill="both", expand=True)

entry_a = ttk.Entry(main, width=20)
entry_b = ttk.Entry(main, width=20)
result_var = tk.StringVar(value="")

ttk.Label(main, text="First number").grid(row=0, column=0, sticky="w", pady=(0, 4))
entry_a.grid(row=1, column=0, sticky="ew", pady=(0, 10))

ttk.Label(main, text="Second number").grid(row=2, column=0, sticky="w", pady=(0, 4))
entry_b.grid(row=3, column=0, sticky="ew", pady=(0, 10))

ttk.Button(main, text="Add", command=add_numbers).grid(row=4, column=0, sticky="ew", pady=(0, 10))

ttk.Label(main, text="Result").grid(row=5, column=0, sticky="w", pady=(0, 4))
result_entry = ttk.Entry(main, textvariable=result_var, state="readonly", width=20)
result_entry.grid(row=6, column=0, sticky="ew")

main.columnconfigure(0, weight=1)
root.bind("<Return>", add_numbers)

root.mainloop()