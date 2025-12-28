




import tkinter as tk

def select_test_states():
    """Tkinter GUI that returns a list of selected step numbers (vertical layout, no groups)."""

    # === Define all test steps (no grouping) ===
    all_steps = [
        (1, "CE Test Structure"),
        (2, "Cables Connections"),
        (3, "Warm QC"),
        (4, "Cold QC"),
        (5, "Post-QC Checkout"),
        (6, "CE Test Structure Disassembly")
    ]

    # === Create main window ===
    root = tk.Tk()
    root.title("Operation Selection")
    root.configure(bg="white")

    vars = {}
    selected_steps = []

    def toggle_all():
        """Toggle all checkboxes based on master checkbox"""
        state = master_var.get()
        for var in vars.values():
            var.set(state)

    def confirm_selection():
        selected = [num for num, var in vars.items() if var.get()]
        selected_steps.extend(selected)
        root.destroy()

    # === Main container frame ===
    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(padx=30, pady=20)

    # === Master "Select All" checkbox ===
    master_var = tk.BooleanVar(value=True)
    master_chk = tk.Checkbutton(
        main_frame,
        text="Select All Operations",
        variable=master_var,
        font=("Arial", 12, "bold"),
        bg="white",
        activebackground="white",
        command=toggle_all
    )
    master_chk.pack(anchor="w", pady=(0, 15))

    # === Separator line ===
    separator = tk.Frame(main_frame, height=2, bg="#cccccc")
    separator.pack(fill="x", pady=(0, 10))

    # === Individual step checkboxes (vertical) ===
    for num, label in all_steps:
        var = tk.BooleanVar(value=True)
        vars[num] = var

        chk = tk.Checkbutton(
            main_frame,
            text=f"{num}. {label}",
            variable=var,
            anchor="w",
            justify="left",
            font=("Arial", 10),
            bg="white",
            activebackground="white"
        )
        chk.pack(anchor="w", pady=3)

    # === Confirm button ===
    btn = tk.Button(
        root,
        text="Confirm Selection",
        command=confirm_selection,
        font=("Arial", 11, "bold"),
        bg="#d9ead3",
        activebackground="#c5e0b4",
        padx=20,
        pady=8
    )
    btn.pack(pady=15)

    root.mainloop()
    return selected_steps


# Example usage
if __name__ == "__main__":
    selected = select_test_states()
    print("✅ You selected:", selected)



















# import tkinter as tk
#
# def select_test_states():
#     """Tkinter GUI that returns a list of selected step numbers (no borders, flat white layout)."""
#
#     # === Define grouped test steps ===
#     # step_groups = [
#     #     [(11, "Input Information\nand Assembly Test Structure")],  # Initial
#     #     [(21, "Warm Power On"), (22, "Warm Initial"), (23, "Warm Checkout"),
#     #      (24, "Warm QC"), (25, "Warm Power Off")],  # Warm QC
#     #     [(31, "Cold Down"), (32, "Cold Power On"), (33, "Cold Initial"),
#     #      (34, "Cold Checkout"), (35, "Cold QC"), (36, "Cold Power Off")],  # Cold QC
#     #     [(41, "Warm Up"), (42, "Warm Power On"), (43, "Warm Initial"),
#     #      (44, "Warm Checkout"), (45, "Warm Power Off")],  # Final Check
#     #     [(51, "Disassembly and Package")]  # Final
#     # ]
#
#     step_groups = [
#         [(11, "Input Information\nand Assembly Test Structure")],  # Initial
#         [(21, "Warm Power On")],  # Warm QC
#         [(31, "Cold Down")],  # Cold QC
#         [(41, "Warm Up")],  # Final Check
#         [(51, "Disassembly and Package")]  # Final
#     ]
#
#     group_titles = ["Initial", "Warm QC", "Cold QC", "Final Check", "Final"]
#
#     # === Create main window ===
#     root = tk.Tk()
#     root.title("Operation Selection")
#     root.configure(bg="white")  # 🌟 Full white background
#
#     vars = {}
#     selected_steps = []
#
#     def toggle_column(col_vars, master_var):
#         for var in col_vars:
#             var.set(master_var.get())
#
#     def confirm_selection():
#         selected = [num for num, var in vars.items() if var.get()]
#         selected_steps.extend(selected)
#         root.destroy()
#
#     # === Layout configuration ===
#     for col, (group, title) in enumerate(zip(step_groups, group_titles)):
#         # Backgrounds — all white
#         bg_color = "white"
#
#         # Column frame — no visible border
#         outer_frame = tk.Frame(root, bg=bg_color)
#         outer_frame.grid(row=0, column=col, padx=20, pady=10, sticky="n")
#
#         col_var = tk.BooleanVar(value=True)
#         col_vars = []
#
#         # Group title and "Select All"
#         master_chk = tk.Checkbutton(
#             outer_frame,
#             text=f"{title}\n(Select All)",
#             variable=col_var,
#             anchor="w",
#             justify="left",
#             font=("Arial", 10, "bold"),
#             bg=bg_color,
#             activebackground=bg_color,
#             command=lambda vlist=col_vars, v=col_var: toggle_column(vlist, v)
#         )
#         master_chk.pack(anchor="w", pady=(0, 5))
#
#         # Step checkboxes
#         for num, label in group:
#             var = tk.BooleanVar(value=True)
#             vars[num] = var
#             col_vars.append(var)
#
#             chk = tk.Checkbutton(
#                 outer_frame,
#                 text=f"{num}. {label}",
#                 variable=var,
#                 anchor="w",
#                 justify="left",
#                 wraplength=180,
#                 bg=bg_color,
#                 activebackground=bg_color
#             )
#             chk.pack(anchor="w", pady=2)
#
#     # Confirm button
#     btn = tk.Button(
#         root, text="Confirm Selection",
#         command=confirm_selection,
#         bg="#d9ead3", activebackground="#c5e0b4"
#     )
#     btn.grid(row=1, column=0, columnspan=len(step_groups), pady=10)
#
#     root.mainloop()
#     return selected_steps
#
#
# # Example usage
# if __name__ == "__main__":
#     selected = select_test_states()
#     print("✅ You selected:", selected)
