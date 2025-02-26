import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import re
import mysql.connector
from tkcalendar import Calendar
from datetime import datetime

class SocietyManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Society Management System")
        self.root.geometry("600x400")  # Main window size
        self.root.configure(bg="#f0f0f0")
        
        # Standard size for secondary windows
        self.standard_width = 800
        self.standard_height = 600
        
        # Initialize database
        self.db = Database()
        self.db.create_tables()
        
        self.show_main_menu()
    
    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.root,
            text="Society Management System",
            font=("Helvetica", 24, "bold"),
            bg="#f0f0f0"
        ).pack(pady=50)
        
        # Buttons Frame
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(expand=True)
        
        tk.Button(
            btn_frame,
            text="Admin Login",
            command=self.show_admin_login,
            font=("Helvetica", 14),
            width=20
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Flat Owner Login",
            command=self.show_member_login,
            font=("Helvetica", 14),
            width=20
        ).pack(pady=10)
    
    def show_admin_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Admin Login")
        login_window.geometry("300x200")
        
        tk.Label(login_window, text="Admin ID:").pack(pady=5)
        admin_id = tk.Entry(login_window)
        admin_id.pack(pady=5)
        
        tk.Label(login_window, text="Password:").pack(pady=5)
        password = tk.Entry(login_window, show="*")
        password.pack(pady=5)
        
        def login():
            if self.db.authenticate_admin(admin_id.get(), password.get()):
                login_window.destroy()
                self.show_admin_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        
        tk.Button(login_window, text="Login", command=login).pack(pady=20)
    
    def show_member_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Flat Owner Login")
        login_window.geometry("400x300")
        login_window.configure(bg="#f0f0f0")
        
        # Make window modal
        login_window.transient(self.root)
        login_window.grab_set()
        
        # Center the window
        self.center_window(login_window)
        
        # Title
        tk.Label(
            login_window,
            text="Flat Owner Login",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=20)
        
        # Login frame
        login_frame = tk.Frame(login_window, bg="#f0f0f0")
        login_frame.pack(pady=20)
        
        # Flat Number
        tk.Label(login_frame, text="Flat Number:", bg="#f0f0f0").pack()
        flat_number = tk.Entry(login_frame, width=20)
        flat_number.pack(pady=5)
        
        # PIN
        tk.Label(login_frame, text="PIN (4 digits):", bg="#f0f0f0").pack()
        pin = tk.Entry(login_frame, show="*", width=20)
        pin.pack(pady=5)
        
        def login():
            # Store values before destroying window
            flat_num = flat_number.get()
            pin_num = pin.get()
            
            result = self.db.authenticate_member(flat_num, pin_num)
            if result:
                login_window.destroy()  # Close login window
                self.root.withdraw()    # Hide main window
                self.show_member_dashboard(flat_num)  # Show dashboard
            else:
                messagebox.showerror("Error", "Invalid credentials")
        
        # Login button
        tk.Button(
            login_frame,
            text="Login",
            command=login,
            width=15,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 10, "bold")
        ).pack(pady=20)
        
        # Back button
        tk.Button(
            login_window,
            text="Back to Main Menu",
            command=lambda: self.go_back(login_window),
            width=15
        ).pack(pady=10)
        
        # Override window close button
        login_window.protocol("WM_DELETE_WINDOW", lambda: self.go_back(login_window))
        
        # Keep window on top
        login_window.lift()
        login_window.focus_force()

    def go_back(self, current_window):
        current_window.destroy()
        self.root.deiconify()  # Show main window

    def center_window(self, window):
        """Center any window on the screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def create_standard_window(self, title, parent=None):
        """Create a standard-sized window with common settings"""
        window = tk.Toplevel(parent or self.root)
        window.title(title)
        window.geometry(f"{self.standard_width}x{self.standard_height}")
        window.configure(bg="#f0f0f0")
        self.center_window(window)
        return window

    def show_admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill='both', expand=True)
        
        # Header with logout button
        header_frame = tk.Frame(main_frame, bg="#f0f0f0")
        header_frame.pack(fill='x', pady=20)
        
        tk.Label(
            header_frame,
            text="Admin Dashboard",
            font=("Helvetica", 20, "bold"),
            bg="#f0f0f0"
        ).pack(side='left', padx=20)
        
        tk.Button(
            header_frame,
            text="Logout",
            command=self.show_main_menu,
            font=("Helvetica", 10)
        ).pack(side='right', padx=20)
        
        # Buttons Frame
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(expand=True)
        
        options = [
            ("Add Member", self.show_add_member),
            ("View Members", self.show_members_list),
            ("View Complaints", self.show_complaints),
            ("Manage Maintenance", self.show_maintenance)
        ]
        
        for text, command in options:
            tk.Button(
                btn_frame,
                text=text,
                command=command,
                width=20,
                font=("Helvetica", 12)
            ).pack(pady=5)

    def show_member_dashboard(self, flat_number):
        dashboard = self.create_standard_window(f"Dashboard - Flat {flat_number}")
        dashboard.protocol("WM_DELETE_WINDOW", lambda: self.logout(dashboard))
        
        # Header frame with member name
        header_frame = tk.Frame(dashboard, bg="#f0f0f0")
        header_frame.pack(fill='x', pady=20)
        
        member_name = self.db.get_member_name(flat_number) or "Member"
        tk.Label(
            header_frame,
            text=f"Welcome {member_name} - Flat {flat_number}",
            font=("Helvetica", 20, "bold"),
            bg="#f0f0f0"
        ).pack(side='left', padx=20)
        
        tk.Button(
            header_frame,
            text="Logout",
            command=lambda: self.logout(dashboard),
            font=("Helvetica", 10)
        ).pack(side='right', padx=20)
        
        # Content frame
        content_frame = tk.Frame(dashboard, bg="#f0f0f0")
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Menu options
        options = [
            ("View My Details", lambda: self.show_member_details(flat_number, dashboard)),
            ("Submit Complaint", lambda: self.show_submit_complaint(flat_number, dashboard)),
            ("View My Complaints", lambda: self.show_my_complaints(flat_number, dashboard)),
            ("View Maintenance", lambda: self.show_my_maintenance(flat_number, dashboard))
        ]
        
        for text, command in options:
            tk.Button(
                content_frame,
                text=text,
                command=command,
                width=20,
                font=("Helvetica", 12),
                bg="#3498db",
                fg="white"
            ).pack(pady=10)

    def logout(self, current_window):
        current_window.destroy()
        self.root.deiconify()
        self.show_main_menu()

    def show_member_details(self, flat_number, parent_window):
        parent_window.withdraw()
        
        window = tk.Toplevel(self.root)
        window.title(f"My Details - Flat {flat_number}")
        window.geometry("400x300")
        window.configure(bg="#f0f0f0")
        
        # Back button
        back_btn = tk.Button(
            window,
            text="← Back",
            command=lambda: self.go_back_to_parent(window, parent_window),
            font=("Helvetica", 10)
        )
        back_btn.pack(anchor='nw', padx=10, pady=5)
        
        # Get member details from database
        member = self.db.get_member_by_flat(flat_number)
        if member:
            details_frame = tk.LabelFrame(window, text="Member Details", bg="#f0f0f0")
            details_frame.pack(padx=20, pady=20, fill='both', expand=True)
            
            labels = [
                ("Name:", member[1]),
                ("Flat Number:", member[2]),
                ("Contact:", member[3])
            ]
            
            for label, value in labels:
                tk.Label(
                    details_frame,
                    text=f"{label} {value}",
                    bg="#f0f0f0",
                    font=("Helvetica", 12)
                ).pack(pady=10)
        
        window.protocol("WM_DELETE_WINDOW", lambda: self.go_back_to_parent(window, parent_window))

    def go_back_to_parent(self, current_window, parent_window):
        current_window.destroy()
        parent_window.deiconify()

    def show_add_member(self):
        window = self.create_standard_window("Add Member")
        
        # Back button
        back_btn = tk.Button(
            window,
            text="← Back",
            command=lambda: self.go_back(window),
            font=("Helvetica", 10)
        )
        back_btn.pack(anchor='nw', padx=10, pady=5)
        
        # Title
        tk.Label(
            window,
            text="Add New Member",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(window, bg="#f0f0f0")
        form_frame.pack(pady=20)
        
        # Field requirements
        requirements = {
            "Name:": "Letters and spaces only (2-50 characters)",
            "Flat Number:": "Letters, numbers and hyphen only (e.g., A-101)",
            "Contact:": "10 digits only",
            "PIN (4 digits):": "4 digits only"
        }
        
        entries = {}
        fields = [
            ("Name:", None, r"^[A-Za-z\s]{2,50}$"),
            ("Flat Number:", None, r"^[A-Z0-9-]{1,10}$"),
            ("Contact:", None, r"^\d{10}$"),
            ("PIN (4 digits):", "*", r"^\d{4}$")
        ]
        
        for text, show, pattern in fields:
            # Label frame for each field
            field_frame = tk.LabelFrame(form_frame, text=text, bg="#f0f0f0")
            field_frame.pack(fill='x', padx=20, pady=5)
            
            # Entry
            entry = tk.Entry(field_frame, show=show if show else "")
            entry.pack(fill='x', padx=5, pady=5)
            entries[text] = (entry, pattern)
            
            # Requirement hint
            tk.Label(
                field_frame,
                text=requirements[text],
                font=("Helvetica", 8),
                fg="gray",
                bg="#f0f0f0"
            ).pack(padx=5)
        
        # Buttons frame
        btn_frame = tk.Frame(window, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        
        def validate_and_save():
            for (text, (entry, pattern)) in entries.items():
                value = entry.get()
                if not value or not re.match(pattern, value):
                    messagebox.showerror("Error", f"Invalid {text.replace(':', '')}\n{requirements[text]}")
                    entry.focus()
                    return
                    
            try:
                self.db.add_member(
                    entries["Name:"][0].get(),
                    entries["Flat Number:"][0].get().upper(),
                    entries["Contact:"][0].get(),
                    entries["PIN (4 digits):"][0].get()
                )
                messagebox.showinfo("Success", "Member added successfully")
                self.go_back(window)
            except mysql.connector.Error as err:
                if err.errno == 1062:  # Duplicate entry error
                    messagebox.showerror("Error", "Flat number already exists!")
                else:
                    messagebox.showerror("Error", f"Database error: {err}")
        
        # Clear and Add buttons
        tk.Button(
            btn_frame,
            text="Clear Form",
            command=lambda: [e[0].delete(0, tk.END) for e in entries.values()],
            width=15,
            bg="#e74c3c",
            fg="white"
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="Add Member",
            command=validate_and_save,
            width=15,
            bg="#2ecc71",
            fg="white"
        ).pack(side='left', padx=5)
        
        window.protocol("WM_DELETE_WINDOW", lambda: self.go_back(window))

    def show_members_list(self):
        window = self.create_standard_window("Members List")
        
        # Back button
        back_btn = tk.Button(
            window,
            text="← Back",
            command=lambda: self.go_back(window),
            font=("Helvetica", 10)
        )
        back_btn.pack(anchor='nw', padx=10, pady=5)
        
        # Title
        tk.Label(
            window,
            text="Society Members",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        # Create tree view with scrollbar
        tree_frame = tk.Frame(window)
        tree_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        columns = ('Name', 'Flat Number', 'Contact')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Add scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        # Define headings and column widths
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor='center')
        
        # Get and insert data
        members = self.db.get_members()
        for member in members:
            tree.insert('', 'end', values=member)
        
        tree.pack(fill='both', expand=True)
        
        # Buttons frame
        btn_frame = tk.Frame(window, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Delete Selected",
            command=lambda: self.delete_member(tree, window),
            width=15
        ).pack(side='left', padx=5)
        
        window.protocol("WM_DELETE_WINDOW", lambda: self.go_back(window))

    def delete_member(self, tree, window):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a member to delete")
            return
            
        member_data = tree.item(selected_item)['values']
        flat_number = str(member_data[1])  # Convert to string since flat number could be numeric
        
        if flat_number.upper() == 'ADMIN':
            messagebox.showerror("Error", "Cannot delete admin account")
            return
            
        # Confirm deletion
        confirm_msg = f"Are you sure you want to delete member with flat number {flat_number}?\n\n"
        confirm_msg += "This will also delete all associated maintenance records and complaints."
        if messagebox.askyesno("Confirm Delete", confirm_msg):
            if self.db.delete_member(flat_number):
                tree.delete(selected_item)
                messagebox.showinfo("Success", "Member deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete member")

    def show_complaints(self):
        window = tk.Toplevel(self.root)
        window.title("Complaints List")
        window.geometry("800x400")
        
        # Create tree view
        columns = ('ID', 'Flat Number', 'Title', 'Description', 'Status', 'Date')
        tree = ttk.Treeview(window, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
        
        # Get and insert data
        complaints = self.db.get_complaints()
        for complaint in complaints:
            tree.insert('', 'end', values=complaint)
        
        tree.pack(pady=20, padx=20, fill='both', expand=True)
        
        tk.Button(
            window,
            text="Close",
            command=window.destroy
        ).pack(pady=10)

    def show_maintenance(self):
        self.root.withdraw()
        window = self.create_standard_window("Maintenance Records")
        
        # Back button
        back_btn = tk.Button(
            window,
            text="← Back",
            command=lambda: self.go_back(window),
            font=("Helvetica", 10)
        )
        back_btn.pack(anchor='nw', padx=10, pady=5)
        
        # Add Maintenance Button that opens a new window
        def open_add_maintenance():
            add_window = tk.Toplevel(window)
            add_window.title("Add Maintenance Record")
            add_window.geometry("500x400")
            add_window.configure(bg="#f0f0f0")
            self.center_window(add_window)
            
            # Make it modal
            add_window.transient(window)
            add_window.grab_set()
            
            # Form frame
            form_frame = tk.LabelFrame(add_window, text="Add New Maintenance", bg="#f0f0f0", padx=20, pady=10)
            form_frame.pack(fill='x', padx=20, pady=20)
            
            # Flat Number Dropdown
            tk.Label(form_frame, text="Flat Number:", bg="#f0f0f0").pack()
            flat_numbers = self.db.get_all_flat_numbers()
            if not flat_numbers:
                messagebox.showerror("Error", "No flat owners found in the system")
                add_window.destroy()
                return
                
            flat_var = tk.StringVar(value=flat_numbers[0] if flat_numbers else "")
            flat_combo = ttk.Combobox(form_frame, textvariable=flat_var, values=flat_numbers, state="readonly", width=17)
            flat_combo.pack(pady=5)
            
            # Amount
            tk.Label(form_frame, text="Amount:", bg="#f0f0f0").pack()
            amount_entry = tk.Entry(form_frame, width=20)
            amount_entry.pack(pady=5)
            
            # Month Dropdown
            tk.Label(form_frame, text="Month:", bg="#f0f0f0").pack()
            months = ["January", "February", "March", "April", "May", "June", 
                     "July", "August", "September", "October", "November", "December"]
            month_var = tk.StringVar(value=months[datetime.now().month - 1])
            month_combo = ttk.Combobox(form_frame, textvariable=month_var, values=months, state="readonly", width=17)
            month_combo.pack(pady=5)
            
            # Year Dropdown
            tk.Label(form_frame, text="Year:", bg="#f0f0f0").pack()
            current_year = datetime.now().year
            years = list(range(current_year - 2, current_year + 3))
            year_var = tk.StringVar(value=str(current_year))
            year_combo = ttk.Combobox(form_frame, textvariable=year_var, values=years, state="readonly", width=17)
            year_combo.pack(pady=5)
            
            def save_maintenance():
                try:
                    flat_num = flat_var.get()
                    if not flat_num:
                        raise ValueError("Please select a flat number")
                        
                    amount = amount_entry.get().strip()
                    if not amount:
                        raise ValueError("Please enter an amount")
                    amount = float(amount)
                    if amount <= 0:
                        raise ValueError("Amount must be greater than 0")
                    
                    month = month_var.get()
                    year = int(year_var.get())
                    
                    # Check if maintenance record already exists
                    if self.db.maintenance_exists(flat_num, month, year):
                        raise ValueError(f"Maintenance record already exists for {flat_num} for {month} {year}")
                    
                    self.db.add_maintenance(flat_num, amount, month, year)
                    messagebox.showinfo("Success", "Maintenance record added successfully")
                    add_window.destroy()
                    load_records()  # Refresh the main window's records
                    
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add record: {str(e)}")
            
            # Buttons frame
            btn_frame = tk.Frame(add_window, bg="#f0f0f0")
            btn_frame.pack(pady=20)
            
            tk.Button(
                btn_frame,
                text="Cancel",
                command=add_window.destroy,
                width=15,
                bg="#e74c3c",
                fg="white"
            ).pack(side='left', padx=5)
            
            tk.Button(
                btn_frame,
                text="Save Record",
                command=save_maintenance,
                width=15,
                bg="#2ecc71",
                fg="white"
            ).pack(side='left', padx=5)
        
        # Add Record button in main window
        tk.Button(
            window,
            text="Add New Maintenance Record",
            command=open_add_maintenance,
            width=25,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10, "bold")
        ).pack(pady=10)
        
        # Filter Frame
        filter_frame = tk.LabelFrame(window, text="Filter Records", padx=10, pady=5)
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(filter_frame, text="Month:").pack(side='left', padx=5)
        month_var = tk.StringVar(value="All")
        month_combo = ttk.Combobox(filter_frame, textvariable=month_var, 
                                 values=["All"] + ["January", "February", "March", "April", "May", "June", 
                                                 "July", "August", "September", "October", "November", "December"])
        month_combo.pack(side='left', padx=5)
        
        tk.Label(filter_frame, text="Year:").pack(side='left', padx=5)
        year_var = tk.StringVar(value="All")
        year_entry = tk.Entry(filter_frame, textvariable=year_var)
        year_entry.pack(side='left', padx=5)
        
        # Records Display
        records_frame = tk.LabelFrame(window, text="Maintenance Records")
        records_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Flat Number', 'Amount', 'Month', 'Year', 'Status')
        tree = ttk.Treeview(records_frame, columns=columns, show='headings')
        
        # Add scrollbar
        vsb = ttk.Scrollbar(records_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')
        
        def load_records():
            for item in tree.get_children():
                tree.delete(item)
                
            month = month_var.get()
            year = year_var.get()
            
            records = self.db.get_maintenance_filtered(
                month if month != "All" else None,
                int(year) if year.isdigit() else None
            )
            
            for record in records:
                tree.insert('', 'end', values=record)
        
        tk.Button(filter_frame, text="Apply Filter", command=load_records).pack(side='left', padx=20)
        
        tree.pack(pady=10, padx=10, fill='both', expand=True)
        
        def update_status():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a record")
                return
            
            record = tree.item(selected[0])['values']
            new_status = 'paid' if record[5] == 'unpaid' else 'unpaid'
            
            if self.db.update_maintenance_status(record[0], new_status):
                load_records()
                messagebox.showinfo("Success", f"Status updated to {new_status}")
            else:
                messagebox.showerror("Error", "Failed to update status")
        
        tk.Button(window, text="Toggle Payment Status", command=update_status).pack(pady=10)
        
        load_records()  # Initial load
        window.protocol("WM_DELETE_WINDOW", lambda: self.go_back(window))

    def go_back(self, current_window):
        self.root.deiconify()  # Show main window
        current_window.destroy()

    def show_submit_complaint(self, flat_number, parent_window):
        parent_window.withdraw()
        window = self.create_standard_window("Submit Complaint")
        
        # Back button
        back_btn = tk.Button(
            window,
            text="← Back",
            command=lambda: self.go_back_to_parent(window, parent_window),
            font=("Helvetica", 10)
        )
        back_btn.pack(anchor='nw', padx=10, pady=5)
        
        # Form frame
        form_frame = tk.LabelFrame(window, text="Submit New Complaint", bg="#f0f0f0")
        form_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Title
        tk.Label(form_frame, text="Title:", bg="#f0f0f0").pack(pady=5)
        title_entry = tk.Entry(form_frame, width=50)
        title_entry.pack(pady=5)
        
        # Description
        tk.Label(form_frame, text="Description:", bg="#f0f0f0").pack(pady=5)
        desc_text = tk.Text(form_frame, height=10, width=50)
        desc_text.pack(pady=5)
        
        def submit():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            
            if not title or not description:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if self.db.submit_complaint(flat_number, title, description):
                messagebox.showinfo("Success", "Complaint submitted successfully")
                self.go_back_to_parent(window, parent_window)
            else:
                messagebox.showerror("Error", "Failed to submit complaint")
        
        tk.Button(
            form_frame,
            text="Submit Complaint",
            command=submit,
            width=20,
            bg="#2ecc71",
            fg="white"
        ).pack(pady=20)
        
        window.protocol("WM_DELETE_WINDOW", lambda: self.go_back_to_parent(window, parent_window))

    def show_my_complaints(self, flat_number, parent_window):
        parent_window.withdraw()
        window = self.create_standard_window("My Complaints")
        
        # Back button
        back_btn = tk.Button(
            window,
            text="← Back",
            command=lambda: self.go_back_to_parent(window, parent_window),
            font=("Helvetica", 10)
        )
        back_btn.pack(anchor='nw', padx=10, pady=5)
        
        # Title
        tk.Label(
            window,
            text="My Complaints History",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        # Create tree view
        columns = ('ID', 'Title', 'Description', 'Status', 'Date')
        tree = ttk.Treeview(window, columns=columns, show='headings')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Get and insert data
        complaints = self.db.get_complaints_by_flat(flat_number)
        for complaint in complaints:
            tree.insert('', 'end', values=complaint)
        
        tree.pack(pady=20, padx=20, fill='both', expand=True)
        
        window.protocol("WM_DELETE_WINDOW", lambda: self.go_back_to_parent(window, parent_window))

    def show_my_maintenance(self, flat_number, parent_window):
        parent_window.withdraw()
        window = self.create_standard_window("My Maintenance")
        
        # Back button
        back_btn = tk.Button(
            window,
            text="← Back",
            command=lambda: self.go_back_to_parent(window, parent_window),
            font=("Helvetica", 10)
        )
        back_btn.pack(anchor='nw', padx=10, pady=5)
        
        # Title
        tk.Label(
            window,
            text="Maintenance Records",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        # Create tree view with correct columns
        columns = ('ID', 'Flat Number', 'Amount', 'Month', 'Year', 'Status')
        tree = ttk.Treeview(window, columns=columns, show='headings')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Define headings with appropriate widths
        column_widths = {
            'ID': 50,
            'Flat Number': 100,
            'Amount': 100,
            'Month': 100,
            'Year': 100,
            'Status': 100
        }
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths[col], anchor='center')
        
        def load_maintenance():
            for item in tree.get_children():
                tree.delete(item)
            
            records = self.db.get_maintenance(flat_number)
            for record in records:
                tree.insert('', 'end', values=record)
        
        def pay_maintenance():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a record to pay")
                return
            
            record = tree.item(selected[0])['values']
            if record[4] == 'paid':  # Status is at index 4
                messagebox.showinfo("Info", "This maintenance is already paid")
                return
            
            if messagebox.askyesno("Confirm", "Do you want to pay this maintenance?"):
                if self.db.pay_maintenance(record[0]):  # ID is at index 0
                    messagebox.showinfo("Success", "Payment successful")
                    load_maintenance()
                else:
                    messagebox.showerror("Error", "Payment failed")
        
        tree.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Payment button
        tk.Button(
            window,
            text="Pay Selected",
            command=pay_maintenance,
            width=20,
            bg="#2ecc71",
            fg="white"
        ).pack(pady=10)
        
        # Load initial data
        load_maintenance()
        
        window.protocol("WM_DELETE_WINDOW", lambda: self.go_back_to_parent(window, parent_window))

if __name__ == "__main__":
    root = tk.Tk()
    app = SocietyManagementSystem(root)
    root.mainloop()
