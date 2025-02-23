# Import SQLite library
import sqlite3

# Import OS library
import os

# DateTime used for Logging
from datetime import datetime

todaysTime = datetime.now().strftime('%Y-%m-%d %H:%M')



# Write to Debugging Log file
def debug_logging(error_message):
    with open(".\\Logs\\Logs_Debugging.txt", "a") as f:
        f.write(f"[{todaysTime}] DATABASE {error_message}\n")

# Define the correct path for the database
db_path = os.path.join(os.getcwd(), r'SQL_DB', 'CLI_Guard_DB.db')

# Create the directory if it doesn't exist
if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))

# Function to create the database schema and views
def create_database():
    debug_logging("MSG: Creating database CLI_Guard_DB.db")

    try:
        # Connect to the database
        sql_connection = sqlite3.connect(db_path)
        sql_cursor = sql_connection.cursor()

        # Create the users table if it doesn't exist
        sql_cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user TEXT NOT NULL UNIQUE PRIMARY KEY,
            master_pw TEXT NOT NULL,
            master_key TEXT NOT NULL,
            master_last_modified TEXT NOT NULL,
            last_locked TEXT
        )
        ''')

        # Create the passwords table if it doesn't exist
        sql_cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            user TEXT NOT NULL,
            category TEXT NOT NULL,
            account TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            pw_key TEXT NOT NULL,
            last_modified TEXT NOT NULL,
            FOREIGN KEY (user) REFERENCES users(user) ON DELETE NO ACTION ON UPDATE NO ACTION
        )
        ''')

        # Create the vw_users view if it doesn't exist
        sql_cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_users AS
        SELECT * FROM users;
        ''')

        # Create the vw_passwords view if it doesn't exist
        sql_cursor.execute('''
        CREATE VIEW IF NOT EXISTS vw_passwords AS
        SELECT * FROM passwords;
        ''')

        # Commit changes
        sql_connection.commit()
        # Write to Debug Logs that the database was successfully created and connected 
        debug_logging("SUCCESS: Database created")
        debug_logging("SUCCESS: Connected to database CLI_Guard_DB.db")
        
        return sql_connection, sql_cursor
        
    except sqlite3.Error as sql_error:
        debug_logging(f"ERROR: Failed to create or connect to database CLI_Guard_DB.db - {str(sql_error)}")
        return None, None

# Connect to the existing database
def connect_to_database():
    try:
        # Connect to the database if it exists
        sql_connection = sqlite3.connect(db_path)
        sql_cursor = sql_connection.cursor()
        debug_logging("SUCCESS: Connected to database CLI_Guard_DB.db")
        return sql_connection, sql_cursor
    except sqlite3.Error as sql_error:
        debug_logging(f"ERROR: Failed to connect to database CLI_Guard_DB.db - {str(sql_error)}")
        return None, None

# Check if the database exists and log accordingly
if os.path.exists(db_path):
    try:
        # Connect to the database if exists
        sql_connection = sqlite3.connect(db_path)
        sql_cursor = sql_connection.cursor()
        debug_logging("SUCCESS: Connected to database CLI_Guard_DB.db")
    except sqlite3.Error as sql_error:
        debug_logging(f"ERROR: Failed to connect to database CLI_Guard_DB.db - {str(sql_error)}")
        sql_connection = None
        sql_cursor = None
else:
    # Create the database if it doesn't exist
    debug_logging("MSG: Checking if database exists")
    sql_connection, sql_cursor = create_database()



# Query the passwords table and insert all into list_pw ordered by account name or userID
def query_data(table) -> list:
    sql_cursor.execute(f"""
                        SELECT * 
                        FROM vw_{table};
                        """)
    list_pw = sql_cursor.fetchall()
    return list_pw


# INSERT new user into users SQLite table
def insert_master(user, pw, session_key, today) -> None:
    sql_cursor.execute(f"""
                    INSERT INTO users
                    (user, master_pw, master_key, master_last_modified) 
                    VALUES(
                        '{user}',
                        '{pw}',
                        '{session_key}',
                        '{today}');
                    """)
    sql_connection.commit()


# UPDATE records in the passwords SQLite table
def lock_master(user, today) -> None:
    sql_cursor.execute(f"""
                    UPDATE users 
                    SET last_locked = '{today}' 
                    WHERE user = '{user}';
                    """)
    sql_connection.commit()
    
    
# INSERT new records into passwords SQLite table
def insert_data(user, category, acct, username, pw, session_key, today) -> None:
    sql_cursor.execute(f"""
                    INSERT INTO passwords 
                    VALUES(
                        '{user}',
                        '{category}',
                        '{acct}',
                        '{username}',
                        '{pw}',
                        '{session_key}',
                        '{today}');
                    """)
    sql_connection.commit()


# UPDATE records in the passwords SQLite table
def update_master_pw(user, pw, session_key, today) -> None:
    sql_cursor.execute(f"""
                    UPDATE users 
                    SET master_pw = '{pw}', 
                    master_key = '{session_key}',
                    master_last_modified = '{today}'
                    WHERE user = '{user}';
                    """)
    sql_connection.commit()


# UPDATE records in the passwords SQLite table
def update_data(pw, acct, usr, old_pw, session_key, today) -> None:
    sql_cursor.execute(f"""
                    UPDATE passwords 
                    SET password = '{pw}', 
                    pw_key = '{session_key}',
                    last_modified = '{today}' 
                    WHERE account = '{acct}' 
                    AND username = '{usr}'
                    AND password = '{old_pw}';
                    """)
    sql_connection.commit()


# DELETE records from the passwords SQLite table
def delete_data(user, acct, usr, pw) -> None:
    sql_cursor.execute(f"""
                    DELETE FROM passwords 
                    WHERE user = '{user}'
                    AND account = '{acct}' 
                    AND username = '{usr}'
                    AND password = '{pw}';
                    """)
    sql_connection.commit()