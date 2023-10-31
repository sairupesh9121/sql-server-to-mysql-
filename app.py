import pyodbc
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import datetime
import os
import mysql.connector

# Initialize variables
log_text = ""
source_server_entry = None
source_database_entry = None
source_uid_entry = None
source_pwd_entry = None
source_port_entry = None
source_db_type_combobox = None
target_server_entry = None
target_database_entry = None
target_uid_entry = None
target_pwd_entry = None
target_port_entry = None
target_db_type_combobox = None
sync_thread = None

# Function to log messages
def log(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text_widget.config(state=tk.NORMAL)
    log_text_widget.insert(tk.END, f"{current_time} - {message}\n")
    log_text_widget.config(state=tk.DISABLED)
    log_text_widget.see("end")

# Function to log error messages
def log_error(error_message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text_widget.config(state=tk.NORMAL)
    log_text_widget.insert(tk.END, f"{current_time} - ERROR: {error_message}\n", "error")
    log_text_widget.config(state=tk.DISABLED)
    log_text_widget.see("end")

# Function to test a database connection
def test_connection(server, database, uid, pwd, port, db_type):
    try:
        if db_type == "SQL Server":
            conn = pyodbc.connect(
                f'Driver={{SQL Server}};'
                f'Server={server},{port};'
                f'Database={database};'
                f'UID={uid};'
                f'PWD={pwd};'
            )
            conn.close()
            return True, None
        elif db_type == "MySQL":
            conn = mysql.connector.connect(
                host=server,
                user=uid,
                password=pwd,
                database=database,
                port=port
            )
            conn.close()
            return True, None
        else:
            return False, "Unsupported database type"
    except Exception as e:
        return False, str(e)

# Function to get connection details
def get_db_connections(source=True):
    if source:
        server = source_server_entry.get()
        database = source_database_entry.get()
        uid = source_uid_entry.get()
        pwd = source_pwd_entry.get()
        port = source_port_entry.get()
        db_type = source_db_type_combobox.get()
    else:
        server = target_server_entry.get()
        database = target_database_entry.get()
        uid = target_uid_entry.get()
        pwd = target_pwd_entry.get()
        port = target_port_entry.get()
        db_type = target_db_type_combobox.get()
    return server, database, uid, pwd, port, db_type

# Function to show a message box with status
def show_status_message(message, is_error=False):
    msg_title = "Error" if is_error else "Success"
    messagebox.showinfo(msg_title, message)

# Function to validate input fields
def validate_inputs():
    source_server = source_server_entry.get()
    source_database = source_database_entry.get()
    source_uid = source_uid_entry.get()
    source_pwd = source_pwd_entry.get()
    source_port = source_port_entry.get()

    if not source_server or not source_database or not source_uid or not source_pwd or not source_port:
        show_status_message("Please fill in all fields before proceeding.", is_error=True)
        return False

    valid, error = test_connection(source_server, source_database, source_uid, source_pwd, source_port, source_db_type_combobox.get())
    if not valid:
        show_status_message(f"Source DB Connection Error: {error}", is_error=True)
        return False

    return True

# Function to save database connections to a file
def save_connections():
    source_server, source_database, source_uid, source_pwd, source_port, source_db_type = get_db_connections(source=True)
    target_server, target_database, target_uid, target_pwd, target_port, target_db_type = get_db_connections(source=False)

    source_conn_test, source_conn_error = test_connection(source_server, source_database, source_uid, source_pwd, source_port, source_db_type)
    target_conn_test, target_conn_error = test_connection(target_server, target_database, target_uid, target_pwd, target_port, target_db_type)

    if source_conn_test and target_conn_test:
        config = []
        config.append(f"Source_DB_Type={source_db_type}")
        config.append(f"Source_Server={source_server}")
        config.append(f"Source_Database={source_database}")
        config.append(f"Source_UID={source_uid}")
        config.append(f"Source_PWD={source_pwd}")
        config.append(f"Source_Port={source_port}")
        config.append(f"Target_DB_Type={target_db_type}")
        config.append(f"Target_Server={target_server}")
        config.append(f"Target_Database={target_database}")
        config.append(f"Target_UID={target_uid}")
        config.append(f"Target_PWD={target_pwd}")
        config.append(f"Target_Port={target_port}")

        with open("db_config.txt", "w") as config_file:
            config_file.write("\n".join(config))

        show_status_message("Database configuration saved successfully.")
    else:
        show_status_message(f"Source DB Connection Error: {source_conn_error}\nTarget DB Connection Error: {target_conn_error}", is_error=True)

# Function to load database connections from a file
def load_connections():
    if os.path.exists("db_config.txt"):
        with open("db_config.txt", "r") as config_file:
            lines = config_file.read().splitlines()

        config_dict = {}
        for line in lines:
            key, value = line.strip().split("=")
            config_dict[key] = value

        source_db_type_combobox.set(config_dict.get("Source_DB_Type", "SQL Server"))
        source_server_entry.delete(0, tk.END)
        source_server_entry.insert(0, config_dict.get("Source_Server", ""))
        source_database_entry.delete(0, tk.END)
        source_database_entry.insert(0, config_dict.get("Source_Database", ""))
        source_uid_entry.delete(0, tk.END)
        source_uid_entry.insert(0, config_dict.get("Source_UID", ""))
        source_pwd_entry.delete(0, tk.END)
        source_pwd_entry.insert(0, config_dict.get("Source_PWD", ""))
        source_port_entry.delete(0, tk.END)
        source_port_entry.insert(0, config_dict.get("Source_Port", ""))
        target_db_type_combobox.set(config_dict.get("Target_DB_Type", "SQL Server"))
        target_server_entry.delete(0, tk.END)
        target_server_entry.insert(0, config_dict.get("Target_Server", ""))
        target_database_entry.delete(0, tk.END)
        target_database_entry.insert(0, config_dict.get("Target_Database", ""))
        target_uid_entry.delete(0, tk.END)
        target_uid_entry.insert(0, config_dict.get("Target_UID", ""))
        target_pwd_entry.delete(0, tk.END)
        target_pwd_entry.insert(0, config_dict.get("Target_PWD", ""))
        target_port_entry.delete(0, tk.END)
        target_port_entry.insert(0, config_dict.get("Target_Port", ""))
    else:
        show_status_message("No configuration found. Please enter the connection details manually.")

# Function to synchronize data
def start_synchronization():
    global sync_thread

    if sync_thread and sync_thread.is_alive():
        show_status_message("Synchronization is already in progress. Please wait.", is_error=True)
    else:
        if not validate_inputs():
            return

        # Disable the Start Synchronization button while synchronization is in progress
        start_sync_button.config(state=tk.DISABLED)

        source_server, source_database, source_uid, source_pwd, source_port, source_db_type = get_db_connections(source=True)
        target_server, target_database, target_uid, target_pwd, target_port, target_db_type = get_db_connections(source=False)

        source_conn_test, source_conn_error = test_connection(source_server, source_database, source_uid, source_pwd, source_port, source_db_type)
        target_conn_test, target_conn_error = test_connection(target_server, target_database, target_uid, target_pwd, target_port, target_db_type)

        if source_conn_test and target_conn_test:
            log("Source and target connections are successful. Starting data synchronization...")

            def synchronization_task():
                if source_db_type == "SQL Server":
                    conn_a = pyodbc.connect(
                        f'Driver={{SQL Server}};'
                        f'Server={source_server},{source_port};'
                        f'Database={source_database};'
                        f'UID={source_uid};'
                        f'PWD={source_pwd};'
                    )
                elif source_db_type == "MySQL":
                    conn_a = mysql.connector.connect(
                        host=source_server,
                        database=source_database,
                        user=source_uid,
                        password=source_pwd,
                        port=source_port
                    )

                if target_db_type == "SQL Server":
                    conn_b = pyodbc.connect(
                        f'Driver={{SQL Server}};'
                        f'Server={target_server},{target_port};'
                        f'Database={target_database};'
                        f'UID={target_uid};'
                        f'PWD={target_pwd};'
                    )
                elif target_db_type == "MySQL":
                    conn_b = mysql.connector.connect(
                        host=target_server,
                        database=target_database,
                        user=target_uid,
                        password=target_pwd,
                        port=target_port
                    )

                while True:
                    cursor_a = conn_a.cursor()
                    cursor_b = conn_b.cursor()

                    try:
                        if source_db_type == "SQL Server":
                            cursor_a.execute("SELECT emp_code, punch_time FROM iclock_transaction WHERE sync_status = 0")
                        elif source_db_type == "MySQL":
                            cursor_a.execute("SELECT emp_code, punch_time FROM iclock_transaction WHERE sync_status = 0")

                        data_from_a = cursor_a.fetchall()

                        rows_inserted_into_b = 0

                        for row in data_from_a:
                            emp_code, punch_time = row

                            if target_db_type == "SQL Server":
                                sql_insert_b = "INSERT INTO employ_logs (emp_code, punch_time) VALUES (?, ?)"
                                cursor_b.execute(sql_insert_b, (emp_code, punch_time))
                            elif target_db_type == "MySQL":
                                sql_insert_b = "INSERT INTO employ_logs (emp_code, punch_time) VALUES (%s, %s)"
                                cursor_b.execute(sql_insert_b, (emp_code, punch_time))

                            rows_inserted_into_b += 1

                        conn_b.commit()

                        if rows_inserted_into_b > 0:
                            if source_db_type == "SQL Server":
                                sql_update_a = "UPDATE iclock_transaction SET sync_status = 1 WHERE emp_code = ? AND punch_time = ?"
                            elif source_db_type == "MySQL":
                                sql_update_a = "UPDATE iclock_transaction SET sync_status = 1 WHERE emp_code = %s AND punch_time = %s"

                            for row in data_from_a:
                                emp_code, punch_time = row
                                cursor_a.execute(sql_update_a, (emp_code, punch_time))
                            conn_a.commit()

                        log(f"Rows inserted into Database: {rows_inserted_into_b}")

                    except Exception as e:
                        log_error(f"Error during synchronization: {str(e)}")

                    time.sleep(120)

                conn_a.close()
                conn_b.close()

            # Show an animation while data is syncing (you can use a label or an image)
            sync_animation_label = ttk.Label(root, text="Synchronizing...", font=("Helvetica", 8))
            sync_animation_label.grid(row=9, column=0, columnspan=2, pady=10)

            def update_sync_animation():
                while True:
                    sync_animation_label.config(text="Synchronizing.")
                    time.sleep(1)
                    sync_animation_label.config(text="Synchronizing..")
                    time.sleep(1)
                    sync_animation_label.config(text="Synchronizing...")
                    time.sleep(1)

            sync_thread = threading.Thread(target=synchronization_task)
            sync_thread.daemon = True
            sync_thread.start()

            sync_animation_thread = threading.Thread(target=update_sync_animation)
            sync_animation_thread.daemon = True
            sync_animation_thread.start()

            show_status_message("Data synchronization started successfully.")
        else:
            show_status_message(f"Source DB Connection Error: {source_conn_error}\nTarget DB Connection Error: {target_conn_error}", is_error=True)

# Create the main window
root = tk.Tk()
root.title("Database Synchronization")

# Set the application icon (replace 'sync.ico' with your icon file path)
root.iconbitmap("sync.ico")

# Create a frame for source connection settings
source_frame = ttk.LabelFrame(root, text="Source Connection")
source_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

source_db_type_label = ttk.Label(source_frame, text="Database Type:")
source_db_type_label.grid(row=0, column=0, sticky="w")
source_db_types = ["SQL Server", "MySQL"]
source_db_type_combobox = ttk.Combobox(source_frame, values=source_db_types)
source_db_type_combobox.grid(row=0, column=1)
source_db_type_combobox.set("SQL Server")

source_server_label = ttk.Label(source_frame, text="Server:")
source_server_label.grid(row=1, column=0, sticky="w")
source_server_entry = ttk.Entry(source_frame)
source_server_entry.grid(row=1, column=1, padx=5, pady=5)

source_database_label = ttk.Label(source_frame, text="Database:")
source_database_label.grid(row=2, column=0, sticky="w")
source_database_entry = ttk.Entry(source_frame)
source_database_entry.grid(row=2, column=1, padx=5, pady=5)

source_uid_label = ttk.Label(source_frame, text="Username:")
source_uid_label.grid(row=3, column=0, sticky="w")
source_uid_entry = ttk.Entry(source_frame)
source_uid_entry.grid(row=3, column=1, padx=5, pady=5)

source_pwd_label = ttk.Label(source_frame, text="Password:")
source_pwd_label.grid(row=4, column=0, sticky="w")
source_pwd_entry = ttk.Entry(source_frame, show="*")
source_pwd_entry.grid(row=4, column=1, padx=5, pady=5)

source_port_label = ttk.Label(source_frame, text="Port:")
source_port_label.grid(row=5, column=0, sticky="w")
source_port_entry = ttk.Entry(source_frame)
source_port_entry.grid(row=5, column=1, padx=5, pady=5)

# Create a frame for target connection settings
target_frame = ttk.LabelFrame(root, text="Target Connection")
target_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

target_db_type_label = ttk.Label(target_frame, text="Database Type:")
target_db_type_label.grid(row=0, column=0, sticky="w")
target_db_type_combobox = ttk.Combobox(target_frame, values=source_db_types)
target_db_type_combobox.grid(row=0, column=1)
target_db_type_combobox.set("SQL Server")

target_server_label = ttk.Label(target_frame, text="Server:")
target_server_label.grid(row=1, column=0, sticky="w")
target_server_entry = ttk.Entry(target_frame)
target_server_entry.grid(row=1, column=1, padx=5, pady=5)

target_database_label = ttk.Label(target_frame, text="Database:")
target_database_label.grid(row=2, column=0, sticky="w")
target_database_entry = ttk.Entry(target_frame)
target_database_entry.grid(row=2, column=1, padx=5, pady=5)

target_uid_label = ttk.Label(target_frame, text="Username:")
target_uid_label.grid(row=3, column=0, sticky="w")
target_uid_entry = ttk.Entry(target_frame)
target_uid_entry.grid(row=3, column=1, padx=5, pady=5)

target_pwd_label = ttk.Label(target_frame, text="Password:")
target_pwd_label.grid(row=4, column=0, sticky="w")
target_pwd_entry = ttk.Entry(target_frame, show="*")
target_pwd_entry.grid(row=4, column=1, padx=5, pady=5)

target_port_label = ttk.Label(target_frame, text="Port:")
target_port_label.grid(row=5, column=0, sticky="w")
target_port_entry = ttk.Entry(target_frame)
target_port_entry.grid(row=5, column=1, padx=5, pady=5)

# Create buttons
save_button = ttk.Button(root, text="Save Configuration", command=save_connections)
save_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

load_button = ttk.Button(root, text="Load Configuration", command=load_connections)
load_button.grid(row=1, column=1, padx=10, pady=5, sticky="e")

# Create a frame for the logs
log_frame = ttk.LabelFrame(root, text="Logs")
log_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Configure column and row weights for log_frame
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)

log_text_widget = tk.Text(log_frame, wrap=tk.WORD, height=10, width=50, bg="black", fg="white")
log_text_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

scrollbar = ttk.Scrollbar(log_frame, command=log_text_widget.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

# Configure column and row weights for log_frame and log_text_widget
log_frame.columnconfigure(0, weight=1)
log_frame.rowconfigure(0, weight=1)

log_text_widget.config(yscrollcommand=scrollbar.set)
log_text_widget.tag_configure("error", foreground="red")

# Create a button to start synchronization
start_sync_button = ttk.Button(root, text="Start Synchronization", command=start_synchronization)
start_sync_button.grid(row=8, column=0, columnspan=2)

# Handle different screen sizes
root.grid_rowconfigure(2, weight=1)  # Allow the log frame to expand vertically
root.columnconfigure(0, weight=1)  # Allow source frame to expand horizontally
root.columnconfigure(1, weight=1)  # Allow target frame to expand horizontally

# Start the main event loop
root.mainloop()
