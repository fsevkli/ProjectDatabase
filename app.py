import tkinter as tk
from tkinter import ttk
import mysql.connector

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="world",
    port=3306
)
cursor = db.cursor()

# Create GUI
root = tk.Tk()
root.title("Database Application")
root.geometry("900x600")

style = ttk.Style()
style.theme_use("clam")

# Function to execute SQL query
def execute_query(query):
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    display_result(result)

# Main frame
main_frame = ttk.Frame(root)
main_frame.pack(pady=10, expand=True, fill="both")

# SQL query entry
query_label = ttk.Label(main_frame, text="Enter SQL query:", font=("Helvetica", 12))
query_label.pack(pady=10)

query_entry = ttk.Entry(main_frame, font=("Helvetica", 12))
query_entry.pack()

execute_button = ttk.Button(main_frame, text="Execute", command=lambda: execute_query(query_entry.get()), style="Accent.TButton")
execute_button.pack(pady=10)

# Predefined SQL query buttons
query1_button = ttk.Button(main_frame, text="Show Countries", style="Accent.TButton", command=lambda: execute_query("SELECT * FROM country"))
query1_button.pack(pady=5)

query2_button = ttk.Button(main_frame, text="Show Cities", style="Accent.TButton", command=lambda: execute_query("SELECT * FROM city"))
query2_button.pack(pady=5)

query3_button = ttk.Button(main_frame, text="Show Languages", style="Accent.TButton", command=lambda: execute_query("SELECT * FROM countrylanguage"))
query3_button.pack(pady=5)

# Result display
result_frame = ttk.Frame(main_frame)
result_frame.pack(pady=10, fill="both", expand=True)

result_canvas = tk.Canvas(result_frame)
result_canvas.pack(side="left", fill="both", expand=True)

result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_canvas.yview)
result_scrollbar.pack(side="right", fill="y")

result_canvas.configure(yscrollcommand=result_scrollbar.set)
result_canvas.bind("<Configure>", lambda e: result_canvas.configure(scrollregion=result_canvas.bbox("all")))

result_interior = tk.Frame(result_canvas)
result_canvas.create_window((0, 0), window=result_interior, anchor="nw")

result_data = []

def display_result(data):
    global result_data

    for widget in result_interior.winfo_children():
        widget.destroy()

    result_data = data
    num_rows = len(result_data)

    if num_rows > 0:
        cursor_description = cursor.description
        if cursor_description:
            column_names = [desc[0] for desc in cursor_description]

            for row_index in range(num_rows):
                row_frame = tk.Frame(result_interior, relief="raised", borderwidth=2, padx=10, pady=10)
                row_frame.pack(fill="x", padx=10, pady=5)

                main_label = tk.Label(row_frame, text=result_data[row_index][0], font=("Helvetica", 14, "bold"))
                main_label.pack(pady=5)

                for col_index, value in enumerate(result_data[row_index]):
                    if col_index > 0:
                        attribute_label = tk.Label(row_frame, text=f"{column_names[col_index]}: {value}")
                        attribute_label.pack(fill="x", padx=5)

# Better page design
root.configure(bg="#F0F0F0")  # Set a light background color

root.mainloop()