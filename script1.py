import mysql.connector
import customtkinter as ctk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",  # Replace with your MySQL username
    "password": "root",  # Replace with your MySQL password
    "database": "sacco_db"  # Replace with your database name
}

# Connect to MySQL
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        id_number VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        balance DECIMAL(10, 2) DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        id INT AUTO_INCREMENT PRIMARY KEY,
        member_id INT NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        interest_rate DECIMAL(5, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'Pending',
        FOREIGN KEY (member_id) REFERENCES members (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        role VARCHAR(255) NOT NULL
    )
    ''')

    conn.commit()
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Error: {err}")
    exit()

# CustomTkinter App
class SaccoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SACCO Management System")
        self.geometry("1200x800")
        self.configure_appearance()

        # Left-side panel with key functions
        self.left_panel = ctk.CTkFrame(self, width=200)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Add buttons for key functions
        self.add_left_panel_buttons()

        # Main content area
        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Initialize dashboard as the default page
        self.show_dashboard()

    def configure_appearance(self):
        ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

    def add_left_panel_buttons(self):
        functions = [
            "Dashboard", "Clients", "Loans", "Savings", "Institution",
            "Accounting", "Reports", "Admin", "Settings"
        ]
        for func in functions:
            button = ctk.CTkButton(self.left_panel, text=func, command=lambda f=func: self.show_page(f))
            button.pack(pady=5, fill="x")

    def show_page(self, page_name):
        # Clear the main content area
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Show the selected page
        if page_name == "Dashboard":
            self.show_dashboard()
        elif page_name == "Clients":
            self.show_clients()
        elif page_name == "Loans":
            self.show_loans()
        elif page_name == "Savings":
            self.show_savings()
        elif page_name == "Institution":
            self.show_institution()
        elif page_name == "Accounting":
            self.show_accounting()
        elif page_name == "Reports":
            self.show_reports()
        elif page_name == "Admin":
            self.show_admin()
        elif page_name == "Settings":
            self.show_settings()

    def show_dashboard(self):
        # Fetch data for summaries
        cursor.execute("SELECT COUNT(*) FROM members")
        total_clients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*), SUM(amount) FROM loans")
        loan_data = cursor.fetchone()
        total_loans = loan_data[0] if loan_data[0] else 0
        total_loan_amount = loan_data[1] if loan_data[1] else 0

        cursor.execute("SELECT SUM(balance) FROM members")
        total_savings = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM loans WHERE status = 'Disbursed'")
        total_cash_in_circulation = cursor.fetchone()[0] or 0

        # Display summaries
        summary_frame = ctk.CTkFrame(self.main_content)
        summary_frame.pack(pady=10)

        ctk.CTkLabel(summary_frame, text=f"Total Clients: {total_clients}").pack()
        ctk.CTkLabel(summary_frame, text=f"Total Loans: {total_loans} (Amount: {total_loan_amount})").pack()
        ctk.CTkLabel(summary_frame, text=f"Total Savings: {total_savings}").pack()
        ctk.CTkLabel(summary_frame, text=f"Total Cash in Circulation: {total_cash_in_circulation}").pack()

        # Pie chart for loans (disbursed vs collected)
        loan_data = {
            "Disbursed": total_loan_amount,
            "Collected": total_cash_in_circulation
        }

        # Ensure values are valid for the pie chart
        if loan_data["Disbursed"] == 0 and loan_data["Collected"] == 0:
            ctk.CTkLabel(self.main_content, text="No loan data available for visualization.").pack()
        else:
            fig, ax = plt.subplots()
            ax.pie(loan_data.values(), labels=loan_data.keys(), autopct="%1.1f%%")
            ax.set_title("Loans: Disbursed vs Collected")

            canvas = FigureCanvasTkAgg(fig, master=self.main_content)
            canvas.draw()
            canvas.get_tk_widget().pack()

    def show_clients(self):
        tab_view = ctk.CTkTabview(self.main_content)
        tab_view.pack(fill="both", expand=True)

        tab_view.add("Create Client")
        tab_view.add("View Clients")

        # Create Client Tab
        create_tab = tab_view.tab("Create Client")
        self.name_entry = ctk.CTkEntry(create_tab, placeholder_text="Full Name")
        self.name_entry.pack(pady=10)
        self.id_entry = ctk.CTkEntry(create_tab, placeholder_text="ID Number")
        self.id_entry.pack(pady=10)
        self.phone_entry = ctk.CTkEntry(create_tab, placeholder_text="Phone Number")
        self.phone_entry.pack(pady=10)
        self.email_entry = ctk.CTkEntry(create_tab, placeholder_text="Email Address")
        self.email_entry.pack(pady=10)

        create_button = ctk.CTkButton(create_tab, text="Create Client", command=self.register_member)
        create_button.pack(pady=20)

        # View Clients Tab
        view_tab = tab_view.tab("View Clients")
        self.clients_tree = ttk.Treeview(view_tab, columns=("ID", "Name", "ID Number", "Phone", "Email", "Balance"), show="headings")
        self.clients_tree.heading("ID", text="ID")
        self.clients_tree.heading("Name", text="Name")
        self.clients_tree.heading("ID Number", text="ID Number")
        self.clients_tree.heading("Phone", text="Phone")
        self.clients_tree.heading("Email", text="Email")
        self.clients_tree.heading("Balance", text="Balance")
        self.clients_tree.pack(fill="both", expand=True, padx=10, pady=10)

        refresh_button = ctk.CTkButton(view_tab, text="Refresh List", command=self.refresh_clients_list)
        refresh_button.pack(pady=10)

    def show_loans(self):
        tab_view = ctk.CTkTabview(self.main_content)
        tab_view.pack(fill="both", expand=True)

        tab_view.add("Apply for Loan")
        tab_view.add("View Loans")

        # Apply for Loan Tab
        apply_tab = tab_view.tab("Apply for Loan")
        self.member_id_loan = ctk.CTkEntry(apply_tab, placeholder_text="Member ID")
        self.member_id_loan.pack(pady=10)
        self.amount_loan = ctk.CTkEntry(apply_tab, placeholder_text="Loan Amount")
        self.amount_loan.pack(pady=10)
        self.interest_rate_loan = ctk.CTkEntry(apply_tab, placeholder_text="Interest Rate (%)")
        self.interest_rate_loan.pack(pady=10)

        apply_button = ctk.CTkButton(apply_tab, text="Apply for Loan", command=self.apply_loan)
        apply_button.pack(pady=20)

        # View Loans Tab
        view_tab = tab_view.tab("View Loans")
        self.loans_tree = ttk.Treeview(view_tab, columns=("ID", "Member ID", "Amount", "Interest Rate", "Status"), show="headings")
        self.loans_tree.heading("ID", text="ID")
        self.loans_tree.heading("Member ID", text="Member ID")
        self.loans_tree.heading("Amount", text="Amount")
        self.loans_tree.heading("Interest Rate", text="Interest Rate")
        self.loans_tree.heading("Status", text="Status")
        self.loans_tree.pack(fill="both", expand=True, padx=10, pady=10)

        refresh_button = ctk.CTkButton(view_tab, text="Refresh List", command=self.refresh_loans_list)
        refresh_button.pack(pady=10)

    def show_savings(self):
        pass  # Implement savings functionality

    def show_institution(self):
        pass  # Implement institution functionality

    def show_accounting(self):
        pass  # Implement accounting functionality

    def show_reports(self):
        pass  # Implement reports functionality

    def show_admin(self):
        pass  # Implement admin functionality

    def show_settings(self):
        pass  # Implement settings functionality

    def register_member(self):
        name = self.name_entry.get()
        id_number = self.id_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        if not name or not id_number or not phone:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            cursor.execute('''
            INSERT INTO members (name, id_number, phone, email)
            VALUES (%s, %s, %s, %s)
            ''', (name, id_number, phone, email))
            conn.commit()
            messagebox.showinfo("Success", "Member registered successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")

    def refresh_clients_list(self):
        for row in self.clients_tree.get_children():
            self.clients_tree.delete(row)

        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
        for member in members:
            self.clients_tree.insert("", "end", values=member)

    def apply_loan(self):
        member_id = self.member_id_loan.get()
        amount = self.amount_loan.get()
        interest_rate = self.interest_rate_loan.get()

        if not member_id or not amount or not interest_rate:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            amount = float(amount)
            interest_rate = float(interest_rate)
            cursor.execute('''
            INSERT INTO loans (member_id, amount, interest_rate)
            VALUES (%s, %s, %s)
            ''', (member_id, amount, interest_rate))
            conn.commit()
            messagebox.showinfo("Success", "Loan application submitted.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")

    def refresh_loans_list(self):
        for row in self.loans_tree.get_children():
            self.loans_tree.delete(row)

        cursor.execute("SELECT * FROM loans")
        loans = cursor.fetchall()
        for loan in loans:
            self.loans_tree.insert("", "end", values=loan)

# Run the app
if __name__ == "__main__":
    app = SaccoApp()
    app.mainloop()

# Close the database connection when the app is closed
conn.close()