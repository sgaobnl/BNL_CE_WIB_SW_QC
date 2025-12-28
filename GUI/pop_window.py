import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def show_image_popup(
    title="Image Viewer",
    image_path=None
):
    """
    Display a fullscreen popup showing an image.
    Press ESC to exit fullscreen or click 'Close' to quit.
    """

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def close_window():
        root.destroy()

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # === Image display ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Fit image to screen (keeping aspect ratio)
            img_ratio = img.height / img.width
            target_width = screen_width - 100
            target_height = int(target_width * img_ratio)

            # If image too tall, scale by height instead
            if target_height > screen_height - 150:
                target_height = screen_height - 150
                target_width = int(target_height / img_ratio)

            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.pack(expand=True)
        except Exception as e:
            print(f"Error loading image: {e}")
            ttk.Label(main_frame, text="Error loading image.", font=("Arial", 24)).pack(expand=True)

    # === Bottom Close Button ===
    ttk.Button(
        main_frame,
        text="Confirm",
        command=close_window
    ).pack(padx=40,pady=40)

    root.mainloop()

def show_checkbox_popup(
    options,
    title="Select Options",
    image_path=None
):
    selected_options = []

    def toggle_all():
        state = select_all_var.get()
        for var in checkbox_vars:
            var.set(state)

    def on_submit():
        nonlocal selected_options
        selected_options = [
            options[i] for i, var in enumerate(checkbox_vars) if var.get()
        ]
        root.destroy()

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Font ===
    font_style = ("Arial", 24)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Grid configuration: left (fixed), right (stretch)
    main_frame.columnconfigure(0, weight=0)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Fixed width for 60 characters ===
    char_width_px = 12  # estimate for 24pt font
    target_width = 40 * char_width_px  # ~840 px

    checkbox_frame = ttk.Frame(main_frame, width=target_width)
    checkbox_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 20))
    checkbox_frame.grid_rowconfigure(99, weight=1)
    checkbox_frame.grid_propagate(False)

    # "Select All"
    select_all_var = tk.BooleanVar()
    tk.Checkbutton(
        checkbox_frame,
        text="{}".format(title),
        variable=select_all_var,
        command=toggle_all,
        font=font_style
    ).grid(row=0, column=0, sticky="w", pady=(0, 10))

    # Checkboxes with auto-wrapping labels
    checkbox_vars = []
    for i, opt in enumerate(options, start=1):
        var = tk.BooleanVar()
        tk.Checkbutton(
            checkbox_frame,
            text=opt,
            variable=var,
            font=font_style,
            wraplength=target_width - 40,  # wrap to fit inside column
            justify="left"
        ).grid(row=i, column=0, sticky="w", pady=4)
        checkbox_vars.append(var)

    # Submit button at bottom-left
    tk.Button(
        checkbox_frame,
        text="Submit",
        command=on_submit,
        font=font_style
    ).grid(row=99, column=0, sticky="sw", pady=(20, 0))

    # === RIGHT COLUMN: Image ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Set width to 2/3 of screen, minus padding
            img_width = int((screen_width * 2 / 3) - 100)
            img_ratio = img.height / img.width
            img_height = int(img_width * img_ratio)

            # Clamp if too tall
            if img_height > screen_height - 100:
                img_height = screen_height - 100
                img_width = int(img_height / img_ratio)

            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.grid(row=0, column=1, sticky="nsew", padx=40)
        except Exception as e:
            print(f"Error loading image: {e}")

    root.mainloop()
    return selected_options
