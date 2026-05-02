import os
import sys
import csv
import json
import threading
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pystray
from PIL import Image
from core import AutoMailerCore
import tkinter.ttk as ttk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Local AppData Settings File
if sys.platform == "win32":
    appdata = os.getenv('APPDATA') or os.path.expanduser("~")
    CONFIG_FILE = os.path.join(appdata, "automailer_config.json")
else:
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".automailer_config.json")

class AutoMailerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoMailer - Extended GUI")
        self.geometry("850x650")

        self.core = AutoMailerCore()

        self.csv_path = None
        self.template_path = None
        self.attachment_paths = []
        self.total_rows = 0
        self.sent_count_session = 0

        self.protocol('WM_DELETE_WINDOW', self.hide_window)

        # Top Frame for Theme Toggle & Status
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=10, pady=5)
        
        self.theme_switch = ctk.CTkSwitch(self.top_frame, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.select()
        self.theme_switch.pack(side="right")

        # Main Layout
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=5)

        self.tab_credentials = self.tabview.add("Credentials")
        self.tab_compose = self.tabview.add("Compose")
        self.tab_send = self.tabview.add("Send")

        self.build_credentials_tab()
        self.build_compose_tab()
        self.build_send_tab()
        
        self.load_settings()

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.entry_email.insert(0, data.get("email", ""))
                    self.entry_display_name.insert(0, data.get("display_name", ""))
                    self.entry_subject.insert(0, data.get("subject", ""))
                    self.format_var.set(data.get("format", "Plain Text"))
                    self.dropdown_format.set(self.format_var.get())
            except Exception as e:
                print(f"Could not load settings: {e}")

    def save_settings(self):
        data = {
            "email": self.entry_email.get(),
            "display_name": self.entry_display_name.get(),
            "subject": self.entry_subject.get(),
            "format": self.format_var.get()
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def build_credentials_tab(self):
        label_title = ctk.CTkLabel(self.tab_credentials, text="Gmail App Passwords Setup", font=("Arial", 20, "bold"))
        label_title.pack(pady=10)

        instructions = (
            "1. Go to your Google Account.\n"
            "2. Turn on 2-Step Verification.\n"
            "3. Go to the link below.\n"
            "4. Create a new App Password and paste it below."
        )
        label_instructions = ctk.CTkLabel(self.tab_credentials, text=instructions, justify="left")
        label_instructions.pack(pady=10)

        # Clickable Link
        self.link_label = ctk.CTkLabel(self.tab_credentials, text="https://myaccount.google.com/apppasswords", text_color="#1E90FF", cursor="hand2")
        self.link_label.pack(pady=5)
        self.link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://myaccount.google.com/apppasswords"))

        self.entry_email = ctk.CTkEntry(self.tab_credentials, placeholder_text="Gmail Address", width=300)
        self.entry_email.pack(pady=10)

        self.entry_password = ctk.CTkEntry(self.tab_credentials, placeholder_text="App Password", show="*", width=300)
        self.entry_password.pack(pady=10)

        self.entry_display_name = ctk.CTkEntry(self.tab_credentials, placeholder_text="Display Name (e.g. John Doe)", width=300)
        self.entry_display_name.pack(pady=10)

        self.btn_verify = ctk.CTkButton(self.tab_credentials, text="Verify & Save Credentials", command=self.verify_credentials)
        self.btn_verify.pack(pady=20)

        self.label_verify_status = ctk.CTkLabel(self.tab_credentials, text="", text_color="green")
        self.label_verify_status.pack(pady=5)

    def verify_credentials(self):
        self.save_settings()
        email = self.entry_email.get()
        password = self.entry_password.get()

        if not email or not password:
            self.label_verify_status.configure(text="Please enter both email and password.", text_color="red")
            return

        self.label_verify_status.configure(text="Verifying...", text_color="yellow")
        self.update_idletasks()

        success, error = self.core.verify_credentials(email, password)
        if success:
            self.label_verify_status.configure(text="Verified Successfully!", text_color="green")
        else:
            self.label_verify_status.configure(text=f"Failed: {error}", text_color="red")

    def build_compose_tab(self):
        # File imports
        frame_files = ctk.CTkFrame(self.tab_compose)
        self.btn_import_csv = ctk.CTkButton(frame_files, text="Import CSV", command=self.import_csv)
        self.btn_import_csv.pack(side="left", padx=5)
        
        self.btn_view_csv = ctk.CTkButton(frame_files, text="View CSV", command=self.view_csv, state="disabled", fg_color="gray")
        self.btn_view_csv.pack(side="left", padx=5)

        self.btn_import_template = ctk.CTkButton(frame_files, text="Import Template", command=self.import_template)
        self.btn_import_template.pack(side="left", padx=5)

        self.btn_import_attach = ctk.CTkButton(frame_files, text="Add Attachment", command=self.import_attachment)
        self.btn_import_attach.pack(side="left", padx=5)
        
        self.btn_clear_attach = ctk.CTkButton(frame_files, text="Clear Attachments", command=self.clear_attachments, fg_color="darkred", hover_color="#8B0000")
        self.btn_clear_attach.pack(side="left", padx=5)

        frame_files.pack(pady=10)

        self.label_files = ctk.CTkLabel(self.tab_compose, text="CSV: None | Template: None | Attachments: 0")
        self.label_files.pack(pady=5)

        # Subject
        self.entry_subject = ctk.CTkEntry(self.tab_compose, placeholder_text="Subject Template (Optional)", width=400)
        self.entry_subject.pack(pady=10)

        # Type Selection
        self.format_var = ctk.StringVar(value="Plain Text")
        self.dropdown_format = ctk.CTkOptionMenu(self.tab_compose, variable=self.format_var, values=["Plain Text", "HTML"], command=self.update_preview)
        self.dropdown_format.pack(pady=10)

        # Preview Area
        label_preview = ctk.CTkLabel(self.tab_compose, text="Preview (This is just an example of your template variables):")
        label_preview.pack(pady=5)

        self.text_preview = ctk.CTkTextbox(self.tab_compose, width=600, height=250)
        self.text_preview.pack(pady=10)

    def tutorial_csv(self):
        msg = (
            "CSV Import Tutorial:\n\n"
            "1. Your CSV file MUST have a column named 'EMAIL' (case-sensitive) for the recipient addresses.\n"
            "2. Any other column header (e.g. 'NAME') can be used in your template as '$NAME' to personalize the email.\n"
            "3. Make sure the file is saved as a comma-separated values (.csv) file."
        )
        messagebox.showinfo("CSV Tutorial", msg)

    def import_csv(self):
        self.tutorial_csv()
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            # Validate CSV
            try:
                with open(path, "r", encoding="utf-8") as f:
                    headers = [h.strip() for h in f.readline().split(",")]
                    if "EMAIL" not in headers:
                        messagebox.showerror("Validation Error", "The CSV file must contain a column exactly named 'EMAIL'.")
                        return
                    
                    data = list(csv.DictReader(f, fieldnames=headers))
                    self.total_rows = len(data) - 1 # Subtract 1 for headers if present in data, but DictReader skips header? Actually DictReader uses the fieldnames so it reads all data.
                    
                # Fix for exact row count
                with open(path, "r", encoding="utf-8") as f:
                    data = list(csv.DictReader(f))
                    self.total_rows = len(data)

                self.csv_path = path
                self.btn_view_csv.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
                self.update_file_labels()
                self.update_preview()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {e}")

    def view_csv(self):
        if not self.csv_path:
            return
        viewer = ctk.CTkToplevel(self)
        viewer.title("CSV Viewer")
        viewer.geometry("600x400")
        viewer.attributes("-topmost", True)
        
        tree_frame = ttk.Frame(viewer)
        tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)
                tree["columns"] = headers
                for h in headers:
                    tree.heading(h, text=h)
                    tree.column(h, width=120)
                for row in reader:
                    tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load CSV for viewing: {e}")

    def import_template(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("HTML Files", "*.html *.htm")])
        if path:
            self.template_path = path
            if path.lower().endswith(('.html', '.htm')):
                self.format_var.set("HTML")
            else:
                self.format_var.set("Plain Text")
            self.dropdown_format.set(self.format_var.get())
            self.update_file_labels()
            self.update_preview()

    def import_attachment(self):
        path = filedialog.askopenfilename()
        if path:
            self.attachment_paths.append(path)
            self.update_file_labels()
            
    def clear_attachments(self):
        self.attachment_paths = []
        self.update_file_labels()

    def update_file_labels(self):
        csv_name = os.path.basename(self.csv_path) if self.csv_path else "None"
        tpl_name = os.path.basename(self.template_path) if self.template_path else "None"
        row_count = f" ({self.total_rows} rows)" if self.total_rows > 0 else ""
        self.label_files.configure(text=f"CSV: {csv_name}{row_count} | Template: {tpl_name} | Attachments: {len(self.attachment_paths)}")

    def update_preview(self, *args):
        self.save_settings()
        self.text_preview.delete("1.0", "end")
        if not self.template_path:
            self.text_preview.insert("1.0", "Please import a template to see preview.")
            return

        with open(self.template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        if self.csv_path:
            try:
                with open(self.csv_path, "r", encoding="utf-8") as f:
                    headers = [h.strip() for h in f.readline().split(",")]
                example_text = template_content
                for header in headers:
                    example_text = example_text.replace(f"${header}", f"[Example {header}]")

                self.text_preview.insert("1.0", example_text)
            except Exception as e:
                self.text_preview.insert("1.0", f"Error reading CSV for preview: {e}")
        else:
            self.text_preview.insert("1.0", template_content)

    def build_send_tab(self):
        # Interval
        frame_interval = ctk.CTkFrame(self.tab_send)
        ctk.CTkLabel(frame_interval, text="Send Interval:").pack(side="left", padx=5)
        self.interval_var = ctk.StringVar(value="Instant")
        self.dropdown_interval = ctk.CTkOptionMenu(frame_interval, variable=self.interval_var, values=["Instant", "10 seconds", "30 seconds", "1 minute"])
        self.dropdown_interval.pack(side="left", padx=5)
        
        self.btn_clear_log = ctk.CTkButton(frame_interval, text="Clear Log", command=lambda: self.text_log.delete("1.0", "end"), fg_color="gray", hover_color="#555555")
        self.btn_clear_log.pack(side="left", padx=15)
        
        frame_interval.pack(pady=10)

        # Limits & Progress
        self.label_limits = ctk.CTkLabel(self.tab_send, text=f"Daily Limit: {self.core.sent_today}/{self.core.max_per_day} sent today")
        self.label_limits.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.tab_send, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.btn_send = ctk.CTkButton(self.tab_send, text="Start Sending", command=self.confirm_and_send)
        self.btn_send.pack(pady=10)

        self.text_log = ctk.CTkTextbox(self.tab_send, width=600, height=250)
        self.text_log.pack(pady=10)
        self.text_log.insert("1.0", "Waiting to start...\n")
        
    def log(self, message):
        def _log():
            self.text_log.insert("end", message + "\n")
            self.text_log.see("end")
            self.label_limits.configure(text=f"Daily Limit: {self.core.sent_today}/{self.core.max_per_day} sent today")
            
            if message.startswith("SUCCESS:"):
                self.sent_count_session += 1
                if self.total_rows > 0:
                    progress = min(1.0, self.sent_count_session / self.total_rows)
                    self.progress_bar.set(progress)

        self.after(0, _log)

    def confirm_and_send(self):
        if not self.csv_path or not self.template_path:
            messagebox.showerror("Error", "Please import both a CSV file and a Template file before sending.")
            return
            
        confirm = messagebox.askyesno("Confirm Send", f"You are about to send up to {self.total_rows} emails.\nAre you sure you want to proceed?")
        if confirm:
            self.start_sending_thread()

    def start_sending_thread(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        display_name = self.entry_display_name.get()

        if not email or not password:
            messagebox.showerror("Error", "Please fill in your Gmail credentials in the Credentials tab.")
            return

        self.btn_send.configure(state="disabled", text="Sending...")
        self.sent_count_session = 0
        self.progress_bar.set(0)
        self.save_settings()

        threading.Thread(target=self.send_process, daemon=True).start()

    def send_process(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        display_name = self.entry_display_name.get()
        subject = self.entry_subject.get()
        is_html = self.format_var.get() == "HTML"

        with open(self.template_path, "r", encoding="utf-8") as f:
            template = f.read()

        interval_map = {"Instant": 0, "10 seconds": 10, "30 seconds": 30, "1 minute": 60}
        interval = interval_map[self.interval_var.get()]

        # Prepare attachments
        attachments_data = None
        if self.attachment_paths:
            names = []
            contents = []
            for path in self.attachment_paths:
                names.append(os.path.basename(path))
                with open(path, "rb") as f:
                    contents.append(f.read())
            attachments_data = {"names": names, "contents": contents}

        self.core.send_emails(
            sender_email=email,
            password=password,
            display_name=display_name,
            csv_file_path=self.csv_path,
            template=template,
            subject=subject,
            is_html=is_html,
            attachments_data=attachments_data,
            interval=interval,
            log_callback=self.log
        )

        def reset_btn():
            self.btn_send.configure(state="normal", text="Start Sending")
        self.after(0, reset_btn)


    # System Tray Integration
    def hide_window(self):
        self.withdraw()
        # Create an image for the tray icon
        image = Image.new('RGB', (64, 64), color = (0, 0, 128))
        menu = pystray.Menu(pystray.MenuItem('Show', self.show_window), pystray.MenuItem('Quit', self.quit_window))
        self.tray_icon = pystray.Icon("name", image, "AutoMailer", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon, item):
        icon.stop()
        self.after(0, self.deiconify)

    def quit_window(self, icon, item):
        icon.stop()
        self.quit()

if __name__ == "__main__":
    app = AutoMailerGUI()
    app.mainloop()