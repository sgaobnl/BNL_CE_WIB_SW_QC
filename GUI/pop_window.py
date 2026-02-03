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

    # === Calculate responsive sizes based on screen dimensions ===
    # Base reference: 1920x1080 screen
    scale_factor = min(screen_width / 1920, screen_height / 1080)

    # Padding values (scaled with minimums)
    pad_main = max(10, int(20 * scale_factor))
    pad_button = max(20, int(40 * scale_factor))

    # Font size for error message (scaled)
    font_size_error = max(16, int(24 * scale_factor))

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=pad_main)
    main_frame.pack(fill="both", expand=True)

    # === Image display ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Fit image to screen (keeping aspect ratio)
            img_ratio = img.height / img.width
            margin = max(50, int(100 * scale_factor))
            target_width = screen_width - margin
            target_height = int(target_width * img_ratio)

            # If image too tall, scale by height instead
            bottom_margin = max(80, int(150 * scale_factor))
            if target_height > screen_height - bottom_margin:
                target_height = screen_height - bottom_margin
                target_width = int(target_height / img_ratio)

            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.pack(expand=True)
        except Exception as e:
            print(f"Error loading image: {e}")
            ttk.Label(main_frame, text="Error loading image.", font=("Arial", font_size_error)).pack(expand=True)

    # === Bottom Close Button ===
    ttk.Button(
        main_frame,
        text="Confirm",
        command=close_window
    ).pack(padx=pad_button, pady=pad_button)

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

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Calculate responsive sizes based on screen dimensions ===
    # Base reference: 1920x1080 screen
    scale_factor = min(screen_width / 1920, screen_height / 1080)

    # Font size (scaled with minimum)
    font_size = max(16, int(24 * scale_factor))
    font_style = ("Arial", font_size)

    # Padding values (scaled)
    pad_main = max(10, int(20 * scale_factor))
    pad_small = max(2, int(4 * scale_factor))
    pad_medium = max(5, int(10 * scale_factor))
    pad_large = max(10, int(20 * scale_factor))

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=pad_main)
    main_frame.pack(fill="both", expand=True)

    # Grid configuration: left (fixed), right (stretch)
    main_frame.columnconfigure(0, weight=0)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Width based on screen size ===
    # Scale character width estimate with font size
    char_width_px = max(8, int(12 * scale_factor))
    target_width = max(300, int(40 * char_width_px))  # Minimum 300px width

    checkbox_frame = ttk.Frame(main_frame, width=target_width)
    checkbox_frame.grid(row=0, column=0, sticky="nsw", padx=(0, pad_large))
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
    ).grid(row=0, column=0, sticky="w", pady=(0, pad_medium))

    # Checkboxes with auto-wrapping labels
    checkbox_vars = []
    for i, opt in enumerate(options, start=1):
        var = tk.BooleanVar()
        tk.Checkbutton(
            checkbox_frame,
            text=opt,
            variable=var,
            font=font_style,
            wraplength=target_width - max(20, int(40 * scale_factor)),  # wrap to fit inside column
            justify="left"
        ).grid(row=i, column=0, sticky="w", pady=pad_small)
        checkbox_vars.append(var)

    # Submit button at bottom-left
    tk.Button(
        checkbox_frame,
        text="Submit",
        command=on_submit,
        font=font_style
    ).grid(row=99, column=0, sticky="sw", pady=(pad_large, 0))

    # === RIGHT COLUMN: Image ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Set width to 2/3 of screen, minus padding (scaled)
            img_width = int((screen_width * 2 / 3) - max(50, int(100 * scale_factor)))
            img_ratio = img.height / img.width
            img_height = int(img_width * img_ratio)

            # Clamp if too tall
            max_img_height = screen_height - max(50, int(100 * scale_factor))
            if img_height > max_img_height:
                img_height = max_img_height
                img_width = int(img_height / img_ratio)

            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.grid(row=0, column=1, sticky="nsew", padx=max(20, int(40 * scale_factor)))
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

    # === Calculate responsive sizes based on screen dimensions ===
    # Base reference: 1920x1080 screen
    scale_factor = min(screen_width / 1920, screen_height / 1080)

    # Font sizes (scaled with minimum values)
    font_size_small = max(10, int(12 * scale_factor))
    font_size_medium = max(12, int(14 * scale_factor))
    font_size_large = max(14, int(16 * scale_factor))
    font_size_header = max(16, int(20 * scale_factor))
    font_size_banner = max(20, int(28 * scale_factor))
    font_size_error = max(11, int(14 * scale_factor))

    # Column widths (in characters, scaled)
    col_component_width = max(10, int(15 * scale_factor))
    col_id_width = max(25, int(45 * scale_factor))  # Reduced from 75 for better fit
    col_status_width = max(6, int(8 * scale_factor))

    # Padding values (scaled)
    pad_small = max(3, int(5 * scale_factor))
    pad_medium = max(5, int(10 * scale_factor))
    pad_large = max(10, int(20 * scale_factor))

    # === Main frame ===
    main_frame = tk.Frame(root, bg='#2C3E50', padx=pad_large, pady=pad_medium)
    main_frame.pack(fill="both", expand=True)

    # === SUBMIT BUTTON (pack FIRST to reserve space at bottom-right) ===
    button_frame = tk.Frame(main_frame, bg='#2C3E50')
    button_frame.pack(side='bottom', fill='x', pady=pad_medium)

    # Error label for validation feedback (left side)
    error_label = tk.Label(
        button_frame,
        text="",
        font=("Arial", font_size_error, "bold"),
        fg='#E74C3C',
        bg='#2C3E50'
    )
    error_label.pack(side='left', padx=(pad_large, 0))

    # Submit button (right side)
    submit_btn = tk.Button(
        button_frame,
        text="Confirm & Continue",
        command=on_submit,
        font=("Arial", font_size_large, "bold"),
        bg='#FF9800',
        fg='white',
        padx=max(15, int(30 * scale_factor)),
        pady=max(5, int(10 * scale_factor)),
        relief='raised',
        cursor='hand2'
    )
    submit_btn.pack(side='right', padx=(0, pad_large * 2), pady=pad_medium)

    # === TOP: Image display ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Scale image to fit upper portion - use less height on smaller screens
            img_ratio = img.height / img.width
            # Allocate less space for image on smaller screens
            img_height_ratio = 0.45 if screen_height < 900 else 0.55 if screen_height < 1200 else 0.65
            target_height = int(screen_height * img_height_ratio)
            target_width = int(target_height / img_ratio)

            # Limit width
            max_img_width = screen_width - pad_large * 4
            if target_width > max_img_width:
                target_width = max_img_width
                target_height = int(target_width * img_ratio)

            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = tk.Label(main_frame, image=photo, bg='#2C3E50')
            image_label.image = photo
            image_label.pack(pady=(0, pad_small))
        except Exception as e:
            print(f"Error loading image: {e}")

    # === TEST RESULT BANNER ===
    result_frame = tk.Frame(main_frame, padx=pad_large, pady=max(8, int(15 * scale_factor)))
    if test_passed:
        result_frame.configure(bg='#27AE60')  # Green
        result_text = f"✓ {slot_name} SLOT - TEST RESULT: PASS"
        result_color = '#27AE60'
    else:
        result_frame.configure(bg='#E74C3C')  # Red
        result_text = f"✗ {slot_name} SLOT - TEST RESULT: FAIL"
        result_color = '#E74C3C'
    result_frame.pack(fill='x', pady=(0, pad_medium))

    result_label = tk.Label(
        result_frame,
        text=result_text,
        font=("Arial", font_size_banner, "bold"),
        fg='white',
        bg=result_color
    )
    result_label.pack()

    # === ID VERIFICATION SECTION ===
    verify_frame = tk.Frame(main_frame, bg='#34495E', padx=pad_large, pady=max(8, int(15 * scale_factor)))
    verify_frame.pack(fill='both', expand=True, pady=(0, pad_medium))

    # Header
    header_label = tk.Label(
        verify_frame,
        text="📋 ID Verification - Scan to Confirm",
        font=("Arial", font_size_header, "bold"),
        fg='white',
        bg='#34495E'
    )
    header_label.pack(pady=(0, pad_medium))

    # Grid for ID verification
    grid_frame = tk.Frame(verify_frame, bg='#34495E')
    grid_frame.pack(fill='x', expand=True)

    # Configure grid columns to expand proportionally
    grid_frame.columnconfigure(0, weight=1)  # Component
    grid_frame.columnconfigure(1, weight=3)  # Original ID
    grid_frame.columnconfigure(2, weight=3)  # Scan/Enter ID
    grid_frame.columnconfigure(3, weight=1)  # Status

    # Column headers
    tk.Label(grid_frame, text="Component", font=("Arial", font_size_medium, "bold"), fg='#BDC3C7', bg='#34495E', width=col_component_width).grid(row=0, column=0, padx=pad_small, pady=pad_small, sticky='ew')
    tk.Label(grid_frame, text="Original ID", font=("Arial", font_size_medium, "bold"), fg='#BDC3C7', bg='#34495E', width=col_id_width).grid(row=0, column=1, padx=pad_small, pady=pad_small, sticky='ew')
    tk.Label(grid_frame, text="Scan/Enter ID", font=("Arial", font_size_medium, "bold"), fg='#BDC3C7', bg='#34495E', width=col_id_width).grid(row=0, column=2, padx=pad_small, pady=pad_small, sticky='ew')
    tk.Label(grid_frame, text="Status", font=("Arial", font_size_medium, "bold"), fg='#BDC3C7', bg='#34495E', width=col_status_width).grid(row=0, column=3, padx=pad_small, pady=pad_small, sticky='ew')

    # ID fields configuration
    id_fields = [
        ('FEMB ID', 'femb_sn', original_ids.get('femb_sn', '')),
        ('CE Box SN', 'ce_box_sn', original_ids.get('ce_box_sn', '')),
        ('Cover (last 4)', 'cover_last4', original_ids.get('cover_last4', '')),
        ('Foam Box QR', 'hwdb_qr', original_ids.get('hwdb_qr', ''))
    ]

    entries = {}
    status_labels = {}

    row_pady = max(4, int(8 * scale_factor))

    for i, (label_text, key, orig_value) in enumerate(id_fields, start=1):
        # Component name
        tk.Label(
            grid_frame,
            text=label_text,
            font=("Arial", font_size_medium),
            fg='white',
            bg='#34495E',
            width=col_component_width,
            anchor='w'
        ).grid(row=i, column=0, padx=pad_small, pady=row_pady, sticky='w')

        # Original ID (left side)
        orig_label = tk.Label(
            grid_frame,
            text=orig_value,
            font=("Arial", font_size_medium, "bold"),
            fg='#2C3E50',
            bg='#f0f0f0',
            width=col_id_width,
            relief='sunken',
            padx=pad_medium
        )
        orig_label.grid(row=i, column=1, padx=pad_small, pady=row_pady, sticky='ew')

        # Scan input (right side)
        entry = tk.Entry(
            grid_frame,
            font=("Arial", font_size_medium),
            width=col_id_width,
            relief='sunken'
        )
        entry.grid(row=i, column=2, padx=pad_small, pady=row_pady, sticky='ew')
        entries[key] = entry

        # Status label
        status_label = tk.Label(
            grid_frame,
            text="⏳",
            font=("Arial", font_size_medium),
            fg='white',
            bg='#34495E',
            width=col_status_width
        )
        status_label.grid(row=i, column=3, padx=pad_small, pady=row_pady, sticky='ew')
        status_labels[key] = status_label

        # Bind entry to check on change
        def make_check_handler(e, ol, ov, k, sl):
            def handler(event=None):
                scanned = e.get().strip()
                validation_results[k]['scanned'] = scanned
                # Normalize '/' to '_' for comparison (handle different scan formats)
                scanned_normalized = scanned.replace('/', '_')
                ov_normalized = ov.replace('/', '_')
                if scanned_normalized == ov_normalized and scanned != '':
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

    # Focus on first entry
    entries['femb_sn'].focus_set()

    root.mainloop()
    return validation_results
