import tkinter as tk
from tkinter import ttk
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import numpy as np

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="stocks",
    port=3306
)
cursor = db.cursor()

# Create the main window
root = tk.Tk()
root.title("Stock Data Viewer")


def calculate_growth():
    stock_name1 = stock_dropdown1.get()
    stock_name2 = stock_dropdown2.get()
    start_date_str = start_date_entry.get()  # Get the start date string
    end_date_str = end_date_entry.get()      # Get the end date string

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                start_date = datetime.strptime(start_date_str, '%Y')  # Try parsing as YYYY
    else:
        # If start date is empty, set it to the oldest date available in the database
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

    # Parse end date string
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                end_date = datetime.strptime(end_date_str, '%Y')  # Try parsing as YYYY
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

    if start_date and end_date:
        start_year, start_month, start_day = start_date.year, start_date.month, start_date.day
        end_year, end_month, end_day = end_date.year, end_date.month, end_date.day

        if start_year < 1999 or end_year > 2022:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, "Year range should be between 1999 and 2022.")
            return

        if stock_name1 and not stock_name2:
            calculate_single_growth(stock_name1, start_year, end_year)
        elif stock_name1 and stock_name2:
            result_text.insert(tk.END, f"Comparing growth between {stock_name1} and {stock_name2} during {start_year}-{end_year}:\n")
            calculate_double_growth(stock_name1, stock_name2, start_year, end_year)
        else:
            result_text.insert(tk.END, "Please select at least one stock.\n")

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

def parse_date(date_str):
    if date_str is None:
        return None

    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str, '%Y-%m')
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str, '%Y')
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY, YYYY-MM, YYYY-MM-DD, or YYYY-MM-DD HH:MM:SS.")


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
                start_date = datetime.strptime(start_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                start_date = datetime.strptime(start_date_str, '%Y')  # Try parsing as YYYY

    # Parse end date string
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                end_date = datetime.strptime(end_date_str, '%Y')  # Try parsing as YYYY
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


# Function to execute the SQL query
def execute_query():
    if not validate_date_entries():
        return

    stock_names = [stock_dropdown1.get(), stock_dropdown2.get()]
    selected_columns = [columns[i] for i in column_vars if column_vars[i].get()]

    for stock_name in stock_names:
        if not selected_columns:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, "Please select at least one column.")
            return

        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, "Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'.")
            return

        if start_date < datetime(1999, 1, 22, 0, 0, 0) or end_date > datetime(2022, 12, 12, 0, 0, 0):
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, "Date range should be between '1999-01-22 00:00:00' and '2022-12-12 00:00:00'.")
            return

        query = f"SELECT {', '.join(selected_columns)} FROM stocks.`{stock_name}` WHERE Date BETWEEN '{start_date}' AND '{end_date}';"
        cursor.execute(query)
        rows = cursor.fetchall()

        result_text.delete('1.0', tk.END)
        if rows:
            for row in rows:
                result_text.insert(tk.END, str(row) + "\n")
        else:
            result_text.insert(tk.END, f"No data found for {stock_name}.\n")

def calculate_single_growth(stock_name, start_year, end_year):
    # Define the start and end dates
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)

    # Query to fetch the start price
    query_start = f"SELECT Close FROM stocks.`{stock_name}` WHERE Date >= '{start_date}' ORDER BY Date ASC LIMIT 1;"
    cursor.execute(query_start)
    start_price_row = cursor.fetchone()
    start_price = start_price_row[0] if start_price_row else None

    # Query to fetch the end price
    query_end = f"SELECT Close FROM stocks.`{stock_name}` WHERE Date <= '{end_date}' ORDER BY Date DESC LIMIT 1;"
    cursor.execute(query_end)
    end_price_row = cursor.fetchone()
    end_price = end_price_row[0] if end_price_row else None

    # Calculate growth rate if both start and end prices are available
    if start_price is not None and end_price is not None:
        growth = ((end_price - start_price) / start_price) * 100
        result_text.insert(tk.END, f"Growth rate for {stock_name} from {start_year} to {end_year}: {growth:.2f}%\n")
        return growth  # Return the growth rate value
    else:
        result_text.insert(tk.END, f"No data found for {stock_name} within the specified year range.\n")
        return None  # Return None if growth rate cannot be calculated


def calculate_double_growth(stock_name1, stock_name2, start_year, end_year):
    result_text.delete('1.0', tk.END)
    
    # Calculate growth rates for both stocks
    growth_rate1 = calculate_single_growth(stock_name1, start_year, end_year)
    growth_rate2 = calculate_single_growth(stock_name2, start_year, end_year)
    
    # Compare growth rates and display the result
    if growth_rate1 is not None and growth_rate2 is not None:
        # Calculate the difference in growth rates
        growth_difference = growth_rate1 - growth_rate2
        
        if growth_difference > 0:
            result_text.insert(tk.END, f"{stock_name1} has a higher growth rate compared to {stock_name2} by {abs(growth_difference):.2f}%.\n")
        elif growth_difference < 0:
            result_text.insert(tk.END, f"{stock_name2} has a higher growth rate compared to {stock_name1} by {abs(growth_difference):.2f}%.\n")
        else:
            result_text.insert(tk.END, "Both stocks have the same growth rate.\n")
    else:
        result_text.insert(tk.END, "Error: Unable to calculate growth rates for one or both of the selected stocks.\n")

    stock_name1 = stock_dropdown1.get()
    stock_name2 = stock_dropdown2.get()
    start_date_str = start_date_entry.get()  # Get the start date string
    end_date_str = end_date_entry.get()      # Get the end date string

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                start_date = datetime.strptime(start_date_str, '%Y')  # Try parsing as YYYY
    else:
        # If start date is empty, set it to the oldest date available in the database
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

    # Parse end date string
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                end_date = datetime.strptime(end_date_str, '%Y')  # Try parsing as YYYY
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

    if start_date and end_date:
        start_year, start_month, start_day = start_date.year, start_date.month, start_date.day
        end_year, end_month, end_day = end_date.year, end_date.month, end_date.day

        if start_year < 1999 or end_year > 2022:
            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, "Year range should be between 1999 and 2022.")
            return

        if stock_name1 and not stock_name2:
            calculate_single_growth(stock_name1, start_year, end_year)
        elif stock_name1 and stock_name2:
            result_text.insert(tk.END, f"Comparing growth between {stock_name1} and {stock_name2} during {start_year}-{end_year}:\n")
            calculate_double_growth(stock_name1, stock_name2, start_year, end_year)
        else:
            result_text.insert(tk.END, "Please select at least one stock.\n")

   
def visualize_growth():
    # Get the selected stock names
    stock_name1 = stock_dropdown1.get()
    stock_name2 = stock_dropdown2.get()
    start_date_str = start_date_entry.get()  # Get the start date string
    end_date_str = end_date_entry.get()      # Get the end date string

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

            # Displaying the graph
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

            # Displaying the graph
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



def calculate_and_display_volatility(*stock_names):
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()

    # Parse start date string
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')  # Try parsing as YYYY-MM-DD
        except ValueError:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                start_date = datetime.strptime(start_date_str, '%Y')  # Try parsing as YYYY
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
                end_date = datetime.strptime(end_date_str, '%Y-%m')  # Try parsing as YYYY-MM
            except ValueError:
                end_date = datetime.strptime(end_date_str, '%Y')  # Try parsing as YYYY
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

def calculate_price_volatility(stock_name, start_date, end_date):
    start_date = f"'{start_date.strftime('%Y-%m-%d')}'"
    end_date = f"'{end_date.strftime('%Y-%m-%d')}'"

    query = f"SELECT Close FROM stocks.`{stock_name}` WHERE Date BETWEEN {start_date} AND {end_date} ORDER BY Date;"
    cursor.execute(query)
    closing_prices = [row[0] for row in cursor.fetchall()]

    if len(closing_prices) < 2:
        return None  # Insufficient data for calculation

    price_volatility = np.std(closing_prices)
    return price_volatility

frame1 = ttk.Frame(root)
frame1.pack(fill='both', expand=True)

stocks = ["amazon", "apple", "credit acceptance corp.", "ebay", "encore wire corp", "hasbro", "intel", "kforce", "nvidia", "texas instruments inc"]

stock_label1 = tk.Label(frame1, text="Stock Name 1:")
stock_label1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

stock_dropdown1 = ttk.Combobox(frame1, values=stocks)
stock_dropdown1.grid(row=0, column=1, padx=5, pady=5)

# Adding second stock dropdown
stock_label2 = tk.Label(frame1, text="Stock Name 2:")
stock_label2.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

stock_dropdown2 = ttk.Combobox(frame1, values=stocks)
stock_dropdown2.grid(row=1, column=1, padx=5, pady=5)

start_date_label = tk.Label(frame1, text="Start Date (YYYY-MM-DD HH:MM:SS):")
start_date_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
start_date_entry = tk.Entry(frame1)
start_date_entry.grid(row=2, column=1, padx=5, pady=5)

end_date_label = tk.Label(frame1, text="End Date (YYYY-MM-DD HH:MM:SS):")
end_date_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
end_date_entry = tk.Entry(frame1)
end_date_entry.grid(row=3, column=1, padx=5, pady=5)

columns = ["Date", "Low", "Open", "Volume", "High", "Close", "Adjusted Close"]
column_vars = {col: tk.BooleanVar() for col in columns}

column_frame = tk.Frame(frame1)
column_frame.grid(row=4, column=0, columnspan=2)

result_text = tk.Text(frame1, height=10, width=100)
result_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# Visualize Growth button
visualize_growth_button = tk.Button(frame1, text="Visualize Growth", command=visualize_growth)
visualize_growth_button.grid(row=1, column=11, padx=5, pady=5)

# Calculate Growth button
calculate_growth_button = tk.Button(frame1, text="Calculate Growth", command=calculate_growth)
calculate_growth_button.grid(row=2, column=10, columnspan=2, padx=5, pady=5)

clear_button = tk.Button(frame1, text="Clear", command=clear_inputs_and_visualization)
clear_button.grid(row=1, column=12, columnspan=2, padx=5, pady=5)

calculate_volatility_button = tk.Button(frame1, text="Calculate Price Volatility", command=lambda: calculate_and_display_volatility(stock_dropdown1.get(), stock_dropdown2.get()))
calculate_volatility_button.grid(row=2, column=13, columnspan=2, padx=5, pady=5)

root.mainloop()