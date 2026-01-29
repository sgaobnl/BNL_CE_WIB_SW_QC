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


def show_disassembly_validation_popup(
    title="Disassembly Validation",
    image_path=None,
    test_passed=True,
    slot_name="",
    original_ids=None
):
    """
    Display a popup for disassembly validation with:
    - Image at the top
    - Test result banner (PASS=green, FAIL=red)
    - ID verification section with original IDs on left, scan inputs on right

    Args:
        title: Window title
        image_path: Path to instruction image (e.g., 18.png or 22.png)
        test_passed: Boolean - True for PASS (green), False for FAIL (red)
        slot_name: "TOP" or "BOTTOM"
        original_ids: dict with keys: 'femb_sn', 'ce_box_sn', 'cover_last4', 'hwdb_qr'

    Returns:
        dict with scanned IDs and validation results
    """
    if original_ids is None:
        original_ids = {'femb_sn': '', 'ce_box_sn': '', 'cover_last4': '', 'hwdb_qr': ''}

    validation_results = {
        'femb_sn': {'scanned': '', 'match': False},
        'ce_box_sn': {'scanned': '', 'match': False},
        'cover_last4': {'scanned': '', 'match': False},
        'hwdb_qr': {'scanned': '', 'match': False},
        'all_valid': False
    }

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def check_match(entry_widget, label_widget, original_value, key):
        """Check if scanned value matches original and update colors"""
        scanned = entry_widget.get().strip()
        validation_results[key]['scanned'] = scanned

        if scanned == original_value and scanned != '':
            validation_results[key]['match'] = True
            entry_widget.config(bg='#90EE90')  # Light green
            label_widget.config(bg='#90EE90')
        elif scanned != '':
            validation_results[key]['match'] = False
            entry_widget.config(bg='#FFB6C1')  # Light red
            label_widget.config(bg='#FFB6C1')
        else:
            validation_results[key]['match'] = False
            entry_widget.config(bg='white')
            label_widget.config(bg='#f0f0f0')

        # Check if all are valid
        check_all_valid()

    def check_all_valid():
        """Check if all IDs match and update submit button"""
        all_match = all(validation_results[k]['match'] for k in ['femb_sn', 'ce_box_sn', 'cover_last4', 'hwdb_qr'])
        validation_results['all_valid'] = all_match
        if all_match:
            submit_btn.config(state='normal', bg='#4CAF50', fg='white', text="✓ Confirm & Continue")
            error_label.config(text="")
        else:
            submit_btn.config(state='normal', bg='#FF9800', fg='white', text="Confirm & Continue")

    def on_submit():
        """Only allow submit if all IDs match"""
        all_match = all(validation_results[k]['match'] for k in ['femb_sn', 'ce_box_sn', 'cover_last4', 'hwdb_qr'])
        validation_results['all_valid'] = all_match
        if all_match:
            root.destroy()
        else:
            # Show error message and stay on popup
            error_label.config(text="⚠ All IDs must match before continuing! Please check and re-scan.", fg='#E74C3C')
            # Highlight mismatched fields
            for key in ['femb_sn', 'ce_box_sn', 'cover_last4', 'hwdb_qr']:
                if not validation_results[key]['match']:
                    entries[key].focus_set()
                    break

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)
    root.configure(bg='#2C3E50')

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = tk.Frame(root, bg='#2C3E50', padx=20, pady=10)
    main_frame.pack(fill="both", expand=True)

    # === TOP: Image display ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Scale image to fit upper portion (about 3/4 of screen height)
            img_ratio = img.height / img.width
            target_height = int(screen_height * 0.70)
            target_width = int(target_height / img_ratio)

            # Limit width
            if target_width > screen_width - 100:
                target_width = screen_width - 100
                target_height = int(target_width * img_ratio)

            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = tk.Label(main_frame, image=photo, bg='#2C3E50')
            image_label.image = photo
            image_label.pack(pady=(0, 5))
        except Exception as e:
            print(f"Error loading image: {e}")

    # === TEST RESULT BANNER ===
    result_frame = tk.Frame(main_frame, padx=20, pady=15)
    if test_passed:
        result_frame.configure(bg='#27AE60')  # Green
        result_text = f"✓ {slot_name} SLOT - TEST RESULT: PASS"
        result_color = '#27AE60'
    else:
        result_frame.configure(bg='#E74C3C')  # Red
        result_text = f"✗ {slot_name} SLOT - TEST RESULT: FAIL"
        result_color = '#E74C3C'
    result_frame.pack(fill='x', pady=(0, 15))

    result_label = tk.Label(
        result_frame,
        text=result_text,
        font=("Arial", 28, "bold"),
        fg='white',
        bg=result_color
    )
    result_label.pack()

    # === ID VERIFICATION SECTION ===
    verify_frame = tk.Frame(main_frame, bg='#34495E', padx=20, pady=15)
    verify_frame.pack(fill='x', pady=(0, 10))

    # Header
    header_label = tk.Label(
        verify_frame,
        text="📋 ID Verification - Scan to Confirm",
        font=("Arial", 20, "bold"),
        fg='white',
        bg='#34495E'
    )
    header_label.pack(pady=(0, 15))

    # Grid for ID verification
    grid_frame = tk.Frame(verify_frame, bg='#34495E')
    grid_frame.pack(fill='x')

    # Column headers
    tk.Label(grid_frame, text="Component", font=("Arial", 14, "bold"), fg='#BDC3C7', bg='#34495E', width=15).grid(row=0, column=0, padx=5, pady=5)
    tk.Label(grid_frame, text="Original ID", font=("Arial", 14, "bold"), fg='#BDC3C7', bg='#34495E', width=25).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(grid_frame, text="Scan/Enter ID", font=("Arial", 14, "bold"), fg='#BDC3C7', bg='#34495E', width=25).grid(row=0, column=2, padx=5, pady=5)
    tk.Label(grid_frame, text="Status", font=("Arial", 14, "bold"), fg='#BDC3C7', bg='#34495E', width=10).grid(row=0, column=3, padx=5, pady=5)

    # ID fields configuration
    id_fields = [
        ('FEMB ID', 'femb_sn', original_ids.get('femb_sn', '')),
        ('CE Box SN', 'ce_box_sn', original_ids.get('ce_box_sn', '')),
        ('Cover (last 4)', 'cover_last4', original_ids.get('cover_last4', '')),
        ('Foam Box QR', 'hwdb_qr', original_ids.get('hwdb_qr', ''))
    ]

    entries = {}
    status_labels = {}

    for i, (label_text, key, orig_value) in enumerate(id_fields, start=1):
        # Component name
        tk.Label(
            grid_frame,
            text=label_text,
            font=("Arial", 14),
            fg='white',
            bg='#34495E',
            width=15,
            anchor='w'
        ).grid(row=i, column=0, padx=5, pady=8, sticky='w')

        # Original ID (left side)
        orig_label = tk.Label(
            grid_frame,
            text=orig_value,
            font=("Arial", 14, "bold"),
            fg='#2C3E50',
            bg='#f0f0f0',
            width=25,
            relief='sunken',
            padx=10
        )
        orig_label.grid(row=i, column=1, padx=5, pady=8)

        # Scan input (right side)
        entry = tk.Entry(
            grid_frame,
            font=("Arial", 14),
            width=25,
            relief='sunken'
        )
        entry.grid(row=i, column=2, padx=5, pady=8)
        entries[key] = entry

        # Status label
        status_label = tk.Label(
            grid_frame,
            text="⏳",
            font=("Arial", 14),
            fg='white',
            bg='#34495E',
            width=10
        )
        status_label.grid(row=i, column=3, padx=5, pady=8)
        status_labels[key] = status_label

        # Bind entry to check on change
        def make_check_handler(e, ol, ov, k, sl):
            def handler(event=None):
                scanned = e.get().strip()
                validation_results[k]['scanned'] = scanned
                if scanned == ov and scanned != '':
                    validation_results[k]['match'] = True
                    e.config(bg='#90EE90')
                    ol.config(bg='#90EE90')
                    sl.config(text="✓", fg='#27AE60')
                elif scanned != '':
                    validation_results[k]['match'] = False
                    e.config(bg='#FFB6C1')
                    ol.config(bg='#FFB6C1')
                    sl.config(text="✗", fg='#E74C3C')
                else:
                    validation_results[k]['match'] = False
                    e.config(bg='white')
                    ol.config(bg='#f0f0f0')
                    sl.config(text="⏳", fg='white')
                check_all_valid()
            return handler

        handler = make_check_handler(entry, orig_label, orig_value, key, status_label)
        entry.bind('<KeyRelease>', handler)
        entry.bind('<FocusOut>', handler)

    # === SUBMIT BUTTON ===
    button_frame = tk.Frame(main_frame, bg='#2C3E50')
    button_frame.pack(fill='x', pady=10)

    submit_btn = tk.Button(
        button_frame,
        text="Confirm & Continue",
        command=on_submit,
        font=("Arial", 16, "bold"),
        bg='#FF9800',
        fg='white',
        padx=30,
        pady=10,
        relief='raised',
        cursor='hand2'
    )
    submit_btn.pack()

    # Error label for validation feedback
    error_label = tk.Label(
        button_frame,
        text="",
        font=("Arial", 14, "bold"),
        fg='#E74C3C',
        bg='#2C3E50'
    )
    error_label.pack(pady=(5, 0))

    # Focus on first entry
    entries['femb_sn'].focus_set()

    root.mainloop()
    return validation_results
