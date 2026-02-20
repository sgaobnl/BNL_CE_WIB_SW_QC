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
    image_path=None,
    test_result=None,
    test_message=""
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
        # If test_result is provided, show results instead of closing
        if test_result is not None:
            show_test_result()
        else:
            root.destroy()

    def show_test_result():
        # Hide submit button
        submit_btn.grid_forget()

        # Show result display
        result_frame.grid(row=100, column=0, sticky="sw", pady=(20, 0))

        # Set result color and text
        if test_result == 'pass':
            result_text = "PASS"
            result_color = "green"
        elif test_result == 'fail':
            result_text = "FAIL"
            result_color = "red"
        else:
            result_text = "WARNING"
            result_color = "orange"

        result_status_label.config(text=result_text, fg=result_color)
        if test_message:
            result_msg_label.config(text=test_message)

        # Show continue button
        continue_btn.grid(row=1, column=0, pady=(10, 0))

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
    submit_btn = tk.Button(
        checkbox_frame,
        text="Submit",
        command=on_submit,
        font=font_style
    )
    submit_btn.grid(row=99, column=0, sticky="sw", pady=(20, 0))

    # Result display frame (hidden initially)
    result_frame = ttk.Frame(checkbox_frame)

    result_status_label = tk.Label(
        result_frame,
        text="",
        font=("Arial", 36, "bold")
    )
    result_status_label.grid(row=0, column=0, pady=(5, 5))

    result_msg_label = tk.Label(
        result_frame,
        text="",
        font=("Arial", 18)
    )
    result_msg_label.grid(row=0, column=1, padx=(20, 0), pady=(5, 5))

    continue_btn = tk.Button(
        result_frame,
        text="Continue",
        command=root.destroy,
        font=font_style,
        width=12
    )
    # continue_btn will be shown after test result is displayed

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


def show_input_popup(
    title="Scan QR Code",
    image_path=None,
    prompt="Scan WIB QR Code:",
    require_confirmation=True
):
    """
    Display a fullscreen popup showing an image with a text input field for QR scanning.
    If require_confirmation is True, user must scan twice to confirm.
    Press ESC to exit fullscreen.
    Returns the scanned value, or empty string if skipped/cancelled.
    """
    result = {"value": ""}

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def close_window():
        root.destroy()

    def on_skip():
        result["value"] = ""
        root.destroy()

    def show_confirm_button():
        """Show confirm button after successful match"""
        # Hide entry and other buttons
        entry.config(state="disabled")
        submit_btn.pack_forget()
        skip_btn.pack_forget()

        # Show confirm button
        confirm_btn = tk.Button(
            button_frame,
            text="Confirm",
            command=root.destroy,
            font=("Arial", 24, "bold"),
            width=15,
            bg="#4CAF50",
            fg="white"
        )
        confirm_btn.pack(pady=10)
        confirm_btn.focus_set()

    def on_submit(event=None):
        value = entry_var.get().strip().replace('/', '_')

        if value == "":
            # Empty = skip
            status_label.config(text="Slot will be skipped (empty)", foreground="orange")
            result["value"] = ""
            root.after(800, root.destroy)
            return

        if len(value) < 3:
            status_label.config(text="ID too short! Please scan again.", foreground="red")
            entry_var.set("")
            entry.focus_set()
            return

        if require_confirmation:
            if not hasattr(on_submit, 'first_scan') or on_submit.first_scan is None:
                # First scan
                on_submit.first_scan = value
                entry_var.set("")
                prompt_label.config(text="Scan again to confirm:")
                status_label.config(text=f"First scan: {value}", foreground="blue")
                entry.focus_set()
            else:
                # Second scan - check match
                if value == on_submit.first_scan:
                    result["value"] = value
                    status_label.config(text=f"ID Matched: {value}", foreground="green")
                    prompt_label.config(text="Click Confirm to proceed")
                    entry_var.set(value)
                    show_confirm_button()
                else:
                    status_label.config(
                        text=f"Mismatch! ({on_submit.first_scan} vs {value}) - Try again",
                        foreground="red"
                    )
                    on_submit.first_scan = None
                    entry_var.set("")
                    prompt_label.config(text=prompt)
                    entry.focus_set()
        else:
            result["value"] = value
            root.destroy()

    on_submit.first_scan = None

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Font ===
    font_large = ("Arial", 28)
    font_medium = ("Arial", 20)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Grid: left column for input, right column for image
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=2)
    main_frame.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Input area ===
    input_frame = ttk.Frame(main_frame)
    input_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 40))

    # Title label
    title_label = tk.Label(input_frame, text=title, font=("Arial", 32, "bold"))
    title_label.pack(pady=(50, 30))

    # Prompt label
    prompt_label = tk.Label(input_frame, text=prompt, font=font_large)
    prompt_label.pack(pady=(20, 10))

    # Entry field for QR scanning
    entry_var = tk.StringVar()
    entry = tk.Entry(input_frame, textvariable=entry_var, font=font_large, width=30, justify="center")
    entry.pack(pady=10, ipady=10)
    entry.bind("<Return>", on_submit)
    entry.focus_set()



    # Status label for feedback
    status_label = tk.Label(input_frame, text="Scan QR code or press Enter to skip", font=font_medium)
    status_label.pack(pady=(10, 10))

    # Notification label below text box
    notification_label = tk.Label(
        input_frame,
        text="After Scan, Please verify the WIB ID",
        font=("Arial", 18),
        fg="blue"
    )
    notification_label.pack(pady=(10, 10))

    # Buttons frame
    button_frame = ttk.Frame(input_frame)
    button_frame.pack(pady=30)

    submit_btn = tk.Button(
        button_frame,
        text="Submit",
        command=on_submit,
        font=font_medium,
        width=12
    )
    submit_btn.pack(side="left", padx=10)

    skip_btn = tk.Button(
        button_frame,
        text="Skip (Empty)",
        command=on_skip,
        font=font_medium,
        width=12
    )
    skip_btn.pack(side="left", padx=10)

    # === RIGHT COLUMN: Image ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Set width to ~60% of screen
            img_width = int(screen_width * 0.55)
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
            image_label.grid(row=0, column=1, sticky="nsew", padx=20)
        except Exception as e:
            print(f"Error loading image: {e}")

    root.mainloop()
    return result["value"]


def show_result_popup(
    title="Test Result",
    result_status="pass",
    message="",
    detail_link=None
):
    """
    Display a fullscreen popup showing test result.
    result_status: 'pass', 'fail', or 'warning'
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
    main_frame = ttk.Frame(root, padding=40)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = tk.Label(main_frame, text=title, font=("Arial", 36, "bold"))
    title_label.pack(pady=(50, 30))

    # Result display with color
    if result_status == 'pass':
        result_text = "PASS"
        result_color = "green"
    elif result_status == 'fail':
        result_text = "FAIL"
        result_color = "red"
    else:
        result_text = "WARNING"
        result_color = "orange"

    result_label = tk.Label(
        main_frame,
        text=result_text,
        font=("Arial", 72, "bold"),
        fg=result_color
    )
    result_label.pack(pady=(30, 20))

    # Message
    if message:
        msg_label = tk.Label(main_frame, text=message, font=("Arial", 24))
        msg_label.pack(pady=(20, 20))

    # Detail link
    if detail_link:
        link_label = tk.Label(
            main_frame,
            text=f"Report: {detail_link}",
            font=("Arial", 18),
            fg="blue"
        )
        link_label.pack(pady=(10, 10))

    # Close button
    tk.Button(
        main_frame,
        text="Continue",
        command=close_window,
        font=("Arial", 24),
        width=15
    ).pack(pady=40)

    root.mainloop()


def show_email_input_popup(
    title="Enter Email Address",
    prompt="Enter your email for test notifications:"
):
    """
    Display a popup to get email address from user.
    Returns the email address or empty string if cancelled.
    """
    result = {"email": ""}

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def on_submit(event=None):
        email = entry_var.get().strip()
        if email and '@' in email:
            result["email"] = email
            root.destroy()
        elif email == "":
            result["email"] = ""
            root.destroy()
        else:
            status_label.config(text="Please enter a valid email address", foreground="red")

    def on_skip():
        result["email"] = ""
        root.destroy()

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Font ===
    font_large = ("Arial", 28)
    font_medium = ("Arial", 20)

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=40)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = tk.Label(main_frame, text=title, font=("Arial", 36, "bold"))
    title_label.pack(pady=(100, 30))

    # Prompt
    prompt_label = tk.Label(main_frame, text=prompt, font=font_large)
    prompt_label.pack(pady=(20, 10))

    # Entry field
    entry_var = tk.StringVar()
    entry = tk.Entry(main_frame, textvariable=entry_var, font=font_large, width=40, justify="center")
    entry.pack(pady=20, ipady=10)
    entry.bind("<Return>", on_submit)
    entry.focus_set()

    # Status label
    status_label = tk.Label(main_frame, text="", font=font_medium)
    status_label.pack(pady=(10, 10))

    # Buttons frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=30)

    tk.Button(
        button_frame,
        text="Submit",
        command=on_submit,
        font=font_medium,
        width=12
    ).pack(side="left", padx=10)

    tk.Button(
        button_frame,
        text="Skip",
        command=on_skip,
        font=font_medium,
        width=12
    ).pack(side="left", padx=10)

    root.mainloop()
    return result["email"]


def show_dual_input_popup(
    title="Scan IDs",
    image_path=None,
    prompt1="Scan Foam Box ID:",
    prompt2="Scan WIB ID:",
    require_confirmation=True
):
    """
    Display a fullscreen popup with TWO text input fields for scanning.
    Both fields require double-scan confirmation.
    Returns a tuple (foam_box_id, wib_id).
    """
    result = {"foam_box_id": "", "wib_id": ""}

    # State tracking for each field
    state = {
        "esd_checked": False,
        "field1_first_scan": None,
        "field1_confirmed": False,
        "field2_first_scan": None,
        "field2_confirmed": False,
    }

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def update_field_status(field_num, text, color):
        if field_num == 1:
            status1_label.config(text=text, foreground=color)
        else:
            status2_label.config(text=text, foreground=color)

    def check_all_confirmed():
        """Check if both fields are confirmed and show final confirm button"""
        if state["field1_confirmed"] and state["field2_confirmed"]:
            # Hide submit button
            submit2_btn.pack_forget()

            # Show final confirm button
            final_confirm_btn = tk.Button(
                button2_frame,
                text="Confirm All",
                command=root.destroy,
                font=("Arial", 24, "bold"),
                width=20,
                bg="#4CAF50",
                fg="white"
            )
            final_confirm_btn.pack(pady=10)
            final_confirm_btn.focus_set()

    def on_esd_check():
        """Handle ESD check checkbox"""
        state["esd_checked"] = esd_check_var.get()
        if state["esd_checked"]:
            esd_status_label.config(text="ESD bag verified", foreground="green")
        else:
            esd_status_label.config(text="Please verify ESD bag condition", foreground="orange")

    def on_submit1(event=None):
        if state["field1_confirmed"]:
            entry2.focus_set()
            return

        value = entry1_var.get().strip().replace('/', '_')

        if value == "":
            update_field_status(1, "Please scan Foam Box ID", "red")
            entry1.focus_set()
            return

        if len(value) < 3:
            update_field_status(1, "ID too short! Please scan again.", "red")
            entry1_var.set("")
            entry1.focus_set()
            return

        if require_confirmation:
            if state["field1_first_scan"] is None:
                # First scan
                state["field1_first_scan"] = value
                entry1_var.set("")
                prompt1_label.config(text="Scan Foam Box ID again to confirm:")
                update_field_status(1, f"First scan: {value}", "blue")
                entry1.focus_set()
            else:
                # Second scan - check match
                if value == state["field1_first_scan"]:
                    result["foam_box_id"] = value
                    state["field1_confirmed"] = True
                    update_field_status(1, f"Foam Box ID Confirmed: {value}", "green")
                    prompt1_label.config(text="Foam Box ID:")
                    entry1_var.set(value)
                    entry1.config(state="disabled")
                    submit1_btn.config(state="disabled", text="Confirmed")
                    # Move to next field
                    entry2.focus_set()
                    check_all_confirmed()
                else:
                    update_field_status(1, f"Mismatch! ({state['field1_first_scan']} vs {value}) - Try again", "red")
                    state["field1_first_scan"] = None
                    entry1_var.set("")
                    prompt1_label.config(text=prompt1)
                    entry1.focus_set()
        else:
            result["foam_box_id"] = value
            state["field1_confirmed"] = True
            entry1.config(state="disabled")
            submit1_btn.config(state="disabled", text="Confirmed")
            entry2.focus_set()
            check_all_confirmed()

    def on_submit2(event=None):
        if state["field2_confirmed"]:
            return

        value = entry2_var.get().strip().replace('/', '_')

        if value == "":
            update_field_status(2, "Please scan WIB ID", "red")
            entry2.focus_set()
            return

        if len(value) < 3:
            update_field_status(2, "ID too short! Please scan again.", "red")
            entry2_var.set("")
            entry2.focus_set()
            return

        if require_confirmation:
            if state["field2_first_scan"] is None:
                # First scan
                state["field2_first_scan"] = value
                entry2_var.set("")
                prompt2_label.config(text="Scan WIB ID again to confirm:")
                update_field_status(2, f"First scan: {value}", "blue")
                entry2.focus_set()
            else:
                # Second scan - check match
                if value == state["field2_first_scan"]:
                    result["wib_id"] = value
                    state["field2_confirmed"] = True
                    update_field_status(2, f"WIB ID Confirmed: {value}", "green")
                    prompt2_label.config(text="WIB ID:")
                    entry2_var.set(value)
                    entry2.config(state="disabled")
                    check_all_confirmed()
                else:
                    update_field_status(2, f"Mismatch! ({state['field2_first_scan']} vs {value}) - Try again", "red")
                    state["field2_first_scan"] = None
                    entry2_var.set("")
                    prompt2_label.config(text=prompt2)
                    entry2.focus_set()
        else:
            result["wib_id"] = value
            state["field2_confirmed"] = True
            entry2.config(state="disabled")
            check_all_confirmed()

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Font ===
    font_large = ("Arial", 24)
    font_medium = ("Arial", 18)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Grid: left column for inputs, right column for image
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=2)
    main_frame.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Input area ===
    input_frame = ttk.Frame(main_frame)
    input_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 40))

    # Title label
    title_label = tk.Label(input_frame, text=title, font=("Arial", 28, "bold"))
    title_label.pack(pady=(20, 15))

    # === Step 1: Foam Box ID ===
    field1_frame = ttk.LabelFrame(input_frame, text="Step 1", padding=10)
    field1_frame.pack(fill="x", pady=(5, 10))

    prompt1_label = tk.Label(field1_frame, text=prompt1, font=font_large)
    prompt1_label.pack(pady=(5, 5))

    entry1_var = tk.StringVar()
    entry1 = tk.Entry(field1_frame, textvariable=entry1_var, font=font_large, width=25, justify="center")
    entry1.pack(pady=5, ipady=8)
    entry1.bind("<Return>", on_submit1)

    status1_label = tk.Label(field1_frame, text="Scan QR code (will require confirmation)", font=("Arial", 14))
    status1_label.pack(pady=(5, 5))

    submit1_btn = tk.Button(
        field1_frame,
        text="Submit Foam Box ID",
        command=on_submit1,
        font=font_medium,
        width=18
    )
    submit1_btn.pack(pady=(5, 10))

    # === Open Box: ESD Check ===
    esd_frame = ttk.LabelFrame(input_frame, text="Open Box", padding=10)
    esd_frame.pack(fill="x", pady=(5, 10))

    esd_check_var = tk.BooleanVar()
    esd_checkbox = tk.Checkbutton(
        esd_frame,
        text="Open box, check if the ESD bag is good",
        variable=esd_check_var,
        command=on_esd_check,
        font=font_medium
    )
    esd_checkbox.pack(pady=(5, 5), anchor="w")

    esd_status_label = tk.Label(esd_frame, text="Please verify ESD bag condition", font=("Arial", 14), fg="orange")
    esd_status_label.pack(pady=(0, 5))

    # === Step 2: WIB ID ===
    field2_frame = ttk.LabelFrame(input_frame, text="Step 2", padding=10)
    field2_frame.pack(fill="x", pady=(5, 10))

    prompt2_label = tk.Label(field2_frame, text=prompt2, font=font_large)
    prompt2_label.pack(pady=(5, 5))

    entry2_var = tk.StringVar()
    entry2 = tk.Entry(field2_frame, textvariable=entry2_var, font=font_large, width=25, justify="center")
    entry2.pack(pady=5, ipady=8)
    entry2.bind("<Return>", on_submit2)

    status2_label = tk.Label(field2_frame, text="Scan QR code (will require confirmation)", font=("Arial", 14))
    status2_label.pack(pady=(5, 5))

    # Submit button for Step 2 (inside Step 2 frame)
    button2_frame = ttk.Frame(field2_frame)
    button2_frame.pack(pady=(5, 10))

    submit2_btn = tk.Button(
        button2_frame,
        text="Submit WIB ID",
        command=on_submit2,
        font=font_medium,
        width=18
    )
    submit2_btn.pack(pady=5)

    # Focus on first entry
    entry1.focus_set()

    # === RIGHT COLUMN: Image ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Set width to ~55% of screen
            img_width = int(screen_width * 0.55)
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
            image_label.grid(row=0, column=1, sticky="nsew", padx=20)
        except Exception as e:
            print(f"Error loading image: {e}")

    root.mainloop()
    return result["foam_box_id"], result["wib_id"]
