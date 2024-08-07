import tkinter as tk
from tkinter import ttk
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import re

# Connect to MySQL database
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    port=int(os.getenv('DB_PORT', 3306))
)
cursor = db.cursor()

# Create the main window
root = tk.Tk()
root.title("Stock Data Viewer")

# Add into database name and dates
def add_to_favorite_list():
    stock_name = stock_dropdown1.get()
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()

    if stock_name:
        # Check if the stock is already in the favorites table
        check_query = "SELECT COUNT(*) FROM favorites WHERE stockname = %s"
        cursor.execute(check_query, (stock_name,))
        count = cursor.fetchone()[0]

        if count == 0:
            # Parse start and end dates
            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None

            # Insert the stock into the favorites table
            insert_query = "INSERT INTO favorites (stockname, start_date, end_date) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (stock_name, start_date, end_date))
            db.commit()
            result_text.insert(tk.END, f"{stock_name} added to favorite list.\n")
            update_dropdown_menu()  # Update the dropdown menu after adding a new stock
        else:
            result_text.insert(tk.END, f"{stock_name} is already in the favorite list.\n")
    else:
        result_text.insert(tk.END, "Please select a stock.\n")
# This function validates the format of a date string using regular expressions.
# It checks if the date string matches any of the predefined patterns.     
def validate_date_format(date):
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}-\d{2}$',         # YYYY-MM
        r'^\d{4}$'                # YYYY
    ]
    for pattern in patterns:
        if re.match(pattern, date):
            return True
    return False
# This function parses a date string into a Python datetime.date object.
# It tries multiple date formats until it successfully parses the string.
# If none of the formats match, it raises a ValueError.
def parse_date(date_str):
    formats_to_try = ['%Y-%m-%d', '%Y-%m', '%Y']
    for format_str in formats_to_try:
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            pass
    raise ValueError("Invalid date format. Please use YYYY-MM-DD, YYYY-MM, or YYYY.")

# This function calculates the growth rate of a single stock within a specified date range.
def calculate_single_growth(stock_name, start_date, end_date, display_result=True):
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Query to fetch the start price
    query_start = f"SELECT Close FROM stocks.`{stock_name}` WHERE Date >= '{start_date_str}' ORDER BY Date ASC LIMIT 1;"
    cursor.execute(query_start)
    
    start_price_row = cursor.fetchone()
    start_price = start_price_row[0] if start_price_row else None
    
    # Query to fetch the end price
    query_end = f"SELECT Close FROM stocks.`{stock_name}` WHERE Date <= '{end_date_str}' ORDER BY Date DESC LIMIT 1;"
    cursor.execute(query_end)
    
    end_price_row = cursor.fetchone()
    end_price = end_price_row[0] if end_price_row else None
    
    # Calculate growth rate if both start and end prices are available
    if start_price is not None and end_price is not None:
        growth = ((end_price - start_price) / start_price) * 100
        if display_result:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, f"Growth rate for {stock_name} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}: {growth:.2f}%\n")
        return growth
    else:
        if display_result:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, f"No valid data found for {stock_name} within the specified date range.\n")
        return None
    
# Calculate growths for two stocks and compare them
def calculate_double_growth(stock_name1, stock_name2, start_date, end_date):
    result_text.delete('1.0', tk.END)
    # Calculate growth rates for both stocks without displaying individual results
    growth_rate1 = calculate_single_growth(stock_name1, start_date, end_date, display_result=False)
    growth_rate2 = calculate_single_growth(stock_name2, start_date, end_date, display_result=False)
    # Compare growth rates and display the result
    if growth_rate1 is not None and growth_rate2 is not None:
        growth_difference = growth_rate1 - growth_rate2
        if growth_difference > 0:
            result_text.insert(tk.END, f"{stock_name1} has a higher growth rate compared to {stock_name2} by {abs(growth_difference):.2f}%.\n")
        elif growth_difference < 0:
            result_text.insert(tk.END, f"{stock_name2} has a higher growth rate compared to {stock_name1} by {abs(growth_difference):.2f}%.\n")
        else:
            result_text.insert(tk.END, "Both stocks have the same growth rate.\n")
    else:
        if growth_rate1 is None:
            result_text.insert(tk.END, f"Error: Unable to calculate growth rate for {stock_name1}.\n")
        if growth_rate2 is None:
            result_text.insert(tk.END, f"Error: Unable to calculate growth rate for {stock_name2}.\n")
        if growth_rate1 is None and growth_rate2 is None:
            result_text.insert(tk.END, "Error: Unable to calculate growth rates for both selected stocks.\n")

# This function calculates the growth rate of one or two stocks within a specified date range.
# It retrieves the necessary inputs from the GUI elements and calls the appropriate
# calculation functions based on the user's selection.
def calculate_growth():
    stock_name1 = stock_dropdown1.get()
    stock_name2 = stock_dropdown2.get()
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()
    try:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
    except ValueError as e:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, str(e))
        return

    if stock_name1 and stock_name2:
        calculate_double_growth(stock_name1, stock_name2, start_date, end_date)
    elif stock_name1:
        calculate_single_growth(stock_name1, start_date, end_date)
    elif stock_name2:
        calculate_single_growth(stock_name2, start_date, end_date)
    else:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Please select at least one stock.")

# Visualize growth of selected stock
def visualize_growth():
    # Get the selected stock names
    stock_name1 = stock_dropdown1.get()
    stock_name2 = stock_dropdown2.get()
    start_date_str = start_date_entry.get()  
    end_date_str = end_date_entry.get()

    # Validate date format and entries
    if not validate_date_format(start_date_str) or not validate_date_format(end_date_str):
        # Handle invalid date format
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Invalid date format. Please use YYYY, YYYY-MM, YYYY-MM-DD, or YYYY-MM-DD HH:MM:SS.")
        return

    start_date, end_date = validate_date_entries(start_date_entry, end_date_entry, result_text, stock_name1, stock_name2, cursor)
    if start_date is None or end_date is None:
        # Handle invalid date entries
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Invalid date entries.")
        return

    # Plotting for one stock
    if stock_name1 and not stock_name2:
        query = f"SELECT Date, Close FROM stocks.`{stock_name1}` WHERE Date BETWEEN '{start_date}' AND '{end_date}' ORDER BY Date;"
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            dates = [row[0] for row in rows]
            closes = [row[1] for row in rows]

            # Plotting the graph
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates, closes, label=stock_name1)
            ax.set_title(f"{stock_name1} Stock Growth Fluctuation")
            ax.set_xlabel("Date")
            ax.set_ylabel("Close Price in Dollars")
            plt.xticks(rotation=90)
            ax.legend()

            # The graph
            canvas = FigureCanvasTkAgg(fig, master=frame1)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

            # Resize the canvas when the window is resized
            frame1.grid_rowconfigure(6, weight=1)
            frame1.grid_columnconfigure(0, weight=1)
            frame1.grid_columnconfigure(1, weight=1)
        else:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, "No data found.")

    # Plotting for two stocks
    elif stock_name1 and stock_name2:
        query1 = f"SELECT Date, Close FROM stocks.`{stock_name1}` WHERE Date BETWEEN '{start_date}' AND '{end_date}' ORDER BY Date;"
        cursor.execute(query1)
        rows1 = cursor.fetchall()

        query2 = f"SELECT Date, Close FROM stocks.`{stock_name2}` WHERE Date BETWEEN '{start_date}' AND '{end_date}' ORDER BY Date;"
        cursor.execute(query2)
        rows2 = cursor.fetchall()

        if rows1 and rows2:
            dates1 = [row[0] for row in rows1]
            closes1 = [row[1] for row in rows1]
            dates2 = [row[0] for row in rows2]
            closes2 = [row[1] for row in rows2]

            # Plotting the graph for both stocks
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates1, closes1, label=stock_name1)
            ax.plot(dates2, closes2, label=stock_name2)
            ax.set_title("Stock Growth Fluctuation")
            ax.set_xlabel("Date")
            ax.set_ylabel("Close Price")
            plt.xticks(rotation=90)
            ax.legend()

            # The graph
            canvas = FigureCanvasTkAgg(fig, master=frame1)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

            # Resize the canvas when the window is resized
            frame1.grid_rowconfigure(6, weight=1)
            frame1.grid_columnconfigure(0, weight=1)
            frame1.grid_columnconfigure(1, weight=1)
        else:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, f"No data found for {stock_name1} or {stock_name2}.")
    else:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, "Please select at least one stock.")

# Clear the input fields and output fields
def clear_inputs_and_visualization():
    # Clear input fields
    start_date_entry.delete(0, tk.END)
    end_date_entry.delete(0, tk.END)
    stock_dropdown1.set('')
    stock_dropdown2.set('')

    # Clear visualization
    for widget in frame1.winfo_children():
        if isinstance(widget, tk.Canvas):
            widget.destroy()
    result_text.delete('1.0', tk.END)
    update_dropdown_menu()
  
# Validation of date entries if not entered sets the MIN and MAX  
def validate_date_entries(start_date_entry, end_date_entry, result_text, stock_name1, stock_name2, cursor):
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()

    # If start date is empty, set it to the oldest date available in the database
    if not start_date_str:
        if stock_name1 or stock_name2:
            if stock_name1:
                cursor.execute(f"SELECT MIN(Date) FROM stocks.`{stock_name1}`")
                min_date_result = cursor.fetchone()[0]
            elif stock_name2:
                cursor.execute(f"SELECT MIN(Date) FROM stocks.`{stock_name2}`")
                min_date_result = cursor.fetchone()[0]
            min_date = min_date_result.strftime('%Y-%m-%d') if min_date_result else None
            start_date = datetime.strptime(min_date, '%Y-%m-%d') if min_date else None
        else:
            start_date = None
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m')
            except ValueError:
                start_date = datetime.strptime(start_date_str, '%Y')

    # Parse end date string
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m')
            except ValueError:
                end_date = datetime.strptime(end_date_str, '%Y')
    else:
        # If end date is empty, set it to the newest date available in the database
        if stock_name1 or stock_name2:
            if stock_name1:
                cursor.execute(f"SELECT MAX(Date) FROM stocks.`{stock_name1}`")
                max_date_result = cursor.fetchone()[0]
            elif stock_name2:
                cursor.execute(f"SELECT MAX(Date) FROM stocks.`{stock_name2}`")
                max_date_result = cursor.fetchone()[0]
            max_date = max_date_result.strftime('%Y-%m-%d') if max_date_result else None
            end_date = datetime.strptime(max_date, '%Y-%m-%d') if max_date else None
        else:
            end_date = None

    # Perform additional validation or processing with start_date and end_date
    return start_date, end_date

# This chekcs the dates, and displays the volatility by calling calculate_price_volatility function
def calculate_and_display_volatility(*stock_names):
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()
    # Parse start date string
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m') 
            except ValueError:
                start_date = datetime.strptime(start_date_str, '%Y') 
    else:
        # If start date is empty, set it to the oldest date available in the database
        if stock_names:
            for stock_name in stock_names:
                cursor.execute(f"SELECT MIN(Date) FROM stocks.`{stock_name}`")
                min_date_result = cursor.fetchone()[0]
                if min_date_result:
                    min_date = min_date_result.strftime('%Y-%m-%d')
                    start_date = datetime.strptime(min_date, '%Y-%m-%d')
                    break
        else:
            start_date = None

    # Parse end date string
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m')
            except ValueError:
                end_date = datetime.strptime(end_date_str, '%Y')
    else:
        # If end date is empty, set it to the newest date available in the database
        if stock_names:
            for stock_name in stock_names:
                cursor.execute(f"SELECT MAX(Date) FROM stocks.`{stock_name}`")
                max_date_result = cursor.fetchone()[0]
                if max_date_result:
                    max_date = max_date_result.strftime('%Y-%m-%d')
                    end_date = datetime.strptime(max_date, '%Y-%m-%d')
                    break
        else:
            end_date = None

    if start_date and end_date:
        result_text.delete('1.0', tk.END)
        for stock_name in stock_names:
            volatility = calculate_price_volatility(stock_name, start_date, end_date)
            if volatility is not None:
                result_text.insert(tk.END, f"Price volatility for {stock_name} between {start_date} and {end_date}: {volatility:.2f}%\n")
            else:
                result_text.insert(tk.END, f"Not enough data to calculate price volatility for {stock_name} within the specified time frame.\n")
                
# This function calculates the price volatility of a stock within a given date range.
def calculate_price_volatility(stock_name, start_date, end_date):
    if not stock_name:
        return None

    start_date = f"'{start_date.strftime('%Y-%m-%d')}'"
    end_date = f"'{end_date.strftime('%Y-%m-%d')}'"

    query = f"SELECT Close FROM stocks.`{stock_name}` WHERE Date BETWEEN {start_date} AND {end_date} ORDER BY Date;"
    cursor.execute(query)
    closing_prices = [row[0] for row in cursor.fetchall()]

    if len(closing_prices) < 2:
        return None  # Insufficient data for calculation

    # Calculate the standard deviation of closing prices
    price_volatility = np.std(closing_prices)
    return price_volatility

# Delete stock from favorites
def delete_stock():
    global selected_stock
    # Get the selected stock name from the dropdown
    selected_stock_value = selected_stock.get()
    if selected_stock_value:
        # Execute a delete query to remove the selected stock from the favorites table
        delete_query = "DELETE FROM favorites WHERE stockname = %s"
        cursor.execute(delete_query, (selected_stock_value,))
        db.commit()
        result_text.insert(tk.END, f"{selected_stock_value} deleted from favorites.\n")
        # Update the dropdown menu after deletion
        update_dropdown_menu()
    else:
        result_text.insert(tk.END, "Please select a stock to delete.\n")

# Call favorites table to see our favorite stocks
def update_dropdown_menu():
    # Clear the current dropdown menu
    stock_dropdown['menu'].delete(0, tk.END)

    # Add "None" option at the beginning
    stock_dropdown['menu'].add_command(label="None", command=lambda: selected_stock.set(""))

    # Query the database for favorite stocks
    select_query = "SELECT stockname FROM favorites"
    cursor.execute(select_query)
    favorites = cursor.fetchall()

    if favorites:
        for favorite in favorites:
            stock_name = favorite[0]

            # Add the favorite stock to the menu
            stock_dropdown['menu'].add_command(label=stock_name, command=lambda name=stock_name: selected_stock.set(name))

# Insert Values from Database to the input fields
def insert_values_from_database(*args):
    stock_name = selected_stock.get()
    start_date_str = ""
    end_date_str = ""
    stock_name = selected_stock.get()
    stock_dropdown1.set(stock_name)
    if stock_name:
        cursor.execute("SELECT start_date, end_date FROM favorites WHERE stockname = %s", (stock_name,))
        result = cursor.fetchone()
        if result:
            start_date_str, end_date_str = result
            start_date_entry.delete(0, tk.END)
            start_date_entry.insert(0, start_date_str)
            end_date_entry.delete(0, tk.END)
            end_date_entry.insert(0, end_date_str)

# Attach a trace to selected_stock to trigger insert_values_from_database whenever its value changes
selected_stock = tk.StringVar()
selected_stock.trace_add("write", insert_values_from_database)

# Refresh dropdown in schedule
def refresh_dropdown():
    update_dropdown_menu()
    # Schedule the next refresh after 5 seconds
    root.after(5000, refresh_dropdown)


# THE GUI
frame1 = ttk.Frame(root)
frame1.pack(fill='both', expand=True)

stocks = ["amazon", "apple", "credit acceptance corp.", "ebay", "encore wire corp", "hasbro", "intel", "kforce", "nvidia", "texas instruments inc"]

# Adding main stock dropdown
stock_label1 = tk.Label(frame1, text="Main Stock:")
stock_label1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
stock_dropdown1 = ttk.Combobox(frame1, values=stocks)
stock_dropdown1.grid(row=0, column=1, padx=5, pady=5)

# Adding second stock dropdown
stock_label2 = tk.Label(frame1, text="Comparison Stock:")
stock_label2.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
stock_dropdown2 = ttk.Combobox(frame1, values=stocks)
stock_dropdown2.grid(row=1, column=1, padx=5, pady=5)

# Select Date
start_date_label = tk.Label(frame1, text="Start Date (YYYY-MM-DD): From 1999-01-22 to 2022-12-12") 
start_date_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
start_date_entry = tk.Entry(frame1)
start_date_entry.grid(row=2, column=1, padx=5, pady=5)

# Select Date
end_date_label = tk.Label(frame1, text="End Date (YYYY-MM-DD): From 1999-01-22 to 2022-12-12")
end_date_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
end_date_entry = tk.Entry(frame1)
end_date_entry.grid(row=3, column=1, padx=5, pady=5)

column_frame = tk.Frame(frame1)
column_frame.grid(row=4, column=0, columnspan=2)

# Result Text display
result_text = tk.Text(frame1, height=10, width=150)
result_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# Visualize Growth button
visualize_growth_button = tk.Button(frame1, text="Visualize Growth", command=visualize_growth)
visualize_growth_button.grid(row=1, column=11, padx=5, pady=5)

# Calculate Growth button
calculate_growth_button = tk.Button(frame1, text="Calculate Growth", command=calculate_growth)
calculate_growth_button.grid(row=2, column=10, columnspan=2, padx=5, pady=5)

# Clears
clear_button = tk.Button(frame1, text="Clear", command=clear_inputs_and_visualization)
clear_button.grid(row=3, column=11, columnspan=2, padx=5, pady=5)

# Volatility
calculate_volatility_button = tk.Button(frame1, text="Calculate Price Volatility", command=lambda: calculate_and_display_volatility(*[stock for stock in [stock_dropdown1.get(), stock_dropdown2.get()] if stock]))
calculate_volatility_button.grid(row=2, column=13, columnspan=2, padx=5, pady=5)

# Add Favorites
add_to_favorites_button = tk.Button(frame1, text="Add to Favorites", command=add_to_favorite_list)
add_to_favorites_button.grid(row=1, column=12, columnspan=2, padx=5, pady=5)

# Create a notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

tab_favorites = ttk.Frame(notebook)
notebook.add(tab_favorites, text="Favorites")

# Labels and dropdown for stock selection
stock_dropdown_label = tk.Label(tab_favorites, text="Favorite Stocks:")
stock_dropdown_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
selected_stock = tk.StringVar()
stock_dropdown = tk.OptionMenu(tab_favorites, selected_stock, "")
stock_dropdown.grid(row=0, column=1, padx=5, pady=5)

# Button to insert values from database into input fields
insert_button = tk.Button(tab_favorites, text="Insert Values", command=insert_values_from_database)
insert_button.grid(row=0, column=3, padx=5, pady=5)

# Delete Fav Stocks
delete_button = tk.Button(tab_favorites, text="Delete Stock", command=delete_stock)
delete_button.grid(row=0, column=2, padx=5, pady=5)

refresh_dropdown()

root.mainloop()
