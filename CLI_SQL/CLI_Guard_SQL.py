# Import SQLite library
import sqlite3

# Import OS library
import os

# Import Traceback for logging
import traceback

# DateTime used for Logging
from datetime import date, datetime, timedelta


def get_today() -> date:
    """Get current date (calculated dynamically)"""
    return date.today()


def get_now_timestamp() -> str:
    """Get current timestamp as formatted string (calculated dynamically)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_tomorrow() -> date:
    """Get tomorrow's date (calculated dynamically)"""
    return date.today() + timedelta(1)

# Whitelist of allowed column names for SQL queries (prevents SQL injection)
ALLOWED_COLUMNS = {'category', 'account', 'username', 'last_modified'}
ALLOWED_SORT_ORDERS = {'ascending', 'descending'}



# Write to Debugging Log file
def logging(message=None):
    with open(os.path.join(".", "Logs.txt"), "a") as file:
        #  Handles Traceback since no message argument is passed
        if message is None:
            # traceback.format_exc() function works without explicitly passing an error
            # because it captures the most recent exception from the current context
            file.write(f"[{get_now_timestamp()}] {traceback.format_exc()}\n")
        else:
            # Handles Logging when a message argument is passed
            file.write(f"[{get_now_timestamp()}] DATABASE {message}\n")


# Database path constant
DB_PATH = os.path.join(os.getcwd(), "CLI_SQL", "CLI_Guard_DB.db")


def get_db_connection() -> sqlite3.Connection:
    """
    Get a database connection with proper error handling

    Returns:
        sqlite3.Connection: Active database connection

    Raises:
        FileNotFoundError: If database file doesn't exist
        sqlite3.Error: If connection fails
    """
    if not os.path.exists(DB_PATH):
        error_msg = "ERROR: Could not connect to CLI Guard Database - Default database does not exist or cannot be found"
        logging(message=error_msg)
        raise FileNotFoundError(error_msg)

    try:
        connection = sqlite3.connect(DB_PATH)
        # Enable foreign keys (SQLite doesn't enable them by default)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    except sqlite3.Error as e:
        logging(message=f"ERROR: Failed to connect to database - {str(e)}")
        raise


# Legacy global connection for backward compatibility (will be phased out)
# TODO: Remove these globals once all functions use get_db_connection()
try:
    sqlConnection = get_db_connection()
    sqlCursor = sqlConnection.cursor()
except (FileNotFoundError, sqlite3.Error):
    sqlConnection = None
    sqlCursor = None


def close_db_connection() -> None:
    """
    Properly close the database connection

    This should be called when the application exits.
    In the future, this will be managed by context managers.
    """
    global sqlConnection, sqlCursor
    try:
        if sqlCursor:
            sqlCursor.close()
        if sqlConnection:
            sqlConnection.commit()  # Commit any pending transactions
            sqlConnection.close()
            logging(message="Database connection closed successfully")
    except sqlite3.Error as e:
        logging(message=f"ERROR: Failed to close database connection - {str(e)}")


def ensure_connection() -> bool:
    """
    Ensure database connection is active, reconnect if needed

    Returns:
        bool: True if connection is active, False otherwise
    """
    global sqlConnection, sqlCursor

    # Check if connection exists and is valid
    if sqlConnection is None or sqlCursor is None:
        try:
            sqlConnection = get_db_connection()
            sqlCursor = sqlConnection.cursor()
            return True
        except (FileNotFoundError, sqlite3.Error):
            return False

    # Test if connection is still alive
    try:
        sqlConnection.execute("SELECT 1")
        return True
    except sqlite3.Error:
        # Connection is dead, try to reconnect
        try:
            sqlConnection = get_db_connection()
            sqlCursor = sqlConnection.cursor()
            return True
        except (FileNotFoundError, sqlite3.Error):
            return False



# Query the passwords table and insert all into list_table ordered by account name or userID
# ? Placeholders in SQL Queries prevent SQL Injection as per the SQLite3 documentation
# The trailing comma when passing Placeholder Bindings avoids the "Incorrect number of bindings supplied" error
# by ensuring the argument is treated as a tuple, which is what execute() expects
# https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
def queryData(user, table, category=None, text=None, sort_by=None) -> list:
    try:
        # Ensure database connection is active
        if not ensure_connection():
            logging(message="ERROR: No database connection available")
            return []

        # Validate column name against whitelist to prevent SQL injection
        if category is not None and category.lower() not in ALLOWED_COLUMNS:
            logging(message=f"ERROR: Invalid column name attempted: {category}")
            raise ValueError(f"Invalid column name: {category}")

        # Validate sort order against whitelist
        if sort_by is not None and sort_by.lower() not in ALLOWED_SORT_ORDERS:
            logging(message=f"ERROR: Invalid sort order attempted: {sort_by}")
            raise ValueError(f"Invalid sort order: {sort_by}")

        if user is not None:
            # Convert Category to category using .lower()
            if text is not None:
                sql_query = f"""
                    SELECT * 
                    FROM vw_{table}
                    WHERE user = ?
                    AND {category.lower()} LIKE ?;
                """
                sqlCursor.execute(sql_query, (user, f"%{text}%",))
            # Convert sort_by from "ascending" to "ASC" or "descending" to "DESC"
            # Convert Category to category using .lower()
            elif sort_by is not None:
                # Map validated sort order to SQL keywords
                sort_sql = "ASC" if sort_by.lower() == "ascending" else "DESC"
                sql_query = (f"""
                    SELECT *
                    FROM vw_{table}
                    WHERE user = ?
                    ORDER BY {category.lower()} {sort_sql};
                """)
                sqlCursor.execute(sql_query, (user,))
            else:
                sql_query = (f"""
                    SELECT * 
                    FROM vw_{table}
                    WHERE user = ?;
                """)
                sqlCursor.execute(sql_query, (user,))
            # Insert query data to a list
            list_table = sqlCursor.fetchall()
            # Return the list of values
            return list_table
        else:
            sqlCursor.execute(f"""
                SELECT * 
                FROM vw_{table};
            """)
            # Insert query data to a list
            list_table = sqlCursor.fetchall()
            # Return the list of values
            return list_table
    except ValueError:
        # Return empty list for validation errors (already logged above)
        return []
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to query data from {table} - {str(sql_error)}")
    except Exception:
        logging()


# INSERT new user into users SQLite table
def insertUser(user, password) -> None:
    try:
        # Ensure database connection is active
        if not ensure_connection():
            logging(message="ERROR: Cannot insert user - no database connection")
            return

        # Handle password as bytes (bcrypt hash) or string
        # SQLite stores bytes as BLOB type
        sql_query = ("""
            INSERT INTO users
            (user, user_pw, user_last_modified)
            VALUES(?, ?, ?);
            """)
        sqlCursor.execute(sql_query, (user, password, get_today()))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Created User {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to insert User {user} - {str(sql_error)}")
    except Exception:
        logging()


# UPDATE records in the passwords SQLite table
def updateUserPassword(user, password) -> None:
    try:
        # Handle password as bytes (bcrypt hash) or string
        sql_query = ("""
            UPDATE users
            SET user_pw = ?,
                user_last_modified = ?
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (password, get_today(), user))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Updated password for {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to update User {user} - {str(sql_error)}")
    except Exception:
        logging()


# DELETE records from the users SQLite table as well as their passwords
def deleteUser(user) -> None:
    try:
        sql_query = (f"""
            DELETE FROM users 
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()
        
        sql_query = (f"""
            DELETE FROM passwords 
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()       
        logging(message=f"SUCCESS: Deleted User {user}")
        logging(message=f"SUCCESS: Deleted all passwords for User {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to delete User {user} - {str(sql_error)}")
    except Exception:
        logging()


# UPDATE records in the users SQLite table to lock account
def lockUser(user) -> None:
    try:
        sql_query = ("""
            UPDATE users
            SET last_locked = ?
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (get_today(), user))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Locked User {user} until {get_tomorrow()}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to lock User {user} - {str(sql_error)}")
    except Exception:
        logging()


# CHECK if user account is locked
def isUserLocked(user) -> bool:
    try:
        sql_query = ("""
            SELECT last_locked
            FROM users
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user,))
        result = sqlCursor.fetchone()

        if result and result[0]:
            # Check if last_locked is today (still locked)
            if str(result[0]) == str(get_today()):
                return True

        return False
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to check lock status for User {user} - {str(sql_error)}")
        return False
    except Exception:
        logging()
        return False


# INSERT new records into passwords SQLite table
def insertData(user, category, account, username, password) -> None:
    try:
        # Ensure database connection is active
        if not ensure_connection():
            logging(message="ERROR: Cannot insert password - no database connection")
            return

        sql_query = ("""
            INSERT INTO passwords
            VALUES(?, ?, ?, ?, ?, ?);
            """)
        sqlCursor.execute(sql_query, (user, category, account, username, password, get_today()))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Inserted password for {account} in User account {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to insert password for {account} in User account {user} - {str(sql_error)}")
    except Exception:
        logging()


# UPDATE records in the passwords SQLite table
def updateData(user, password, account, username, old_password) -> None:
    try:
        sql_query = ("""
            UPDATE passwords
            SET password = ?,
                last_modified = ?
            WHERE account = ?
            AND username = ?
            AND password = ?;
            """)
        sqlCursor.execute(sql_query, (password, get_today(), account, username, old_password))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Updated password for {account} in User account {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to update password for {account} in User account {user} - {str(sql_error)}")
    except Exception:
        logging()


# DELETE records from the passwords SQLite table
def deleteData(user, account, username, password) -> None:
    try:
        sql_query = ("""
            DELETE FROM passwords
            WHERE user = ?
            AND account = ?
            AND username = ?
            AND password = ?;
            """)
        sqlCursor.execute(sql_query, (user, account, username, password))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Deleted password for {account} in User account {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to delete password for {account} in User account {user} - {str(sql_error)}")
    except Exception:
        logging()


# Export Database using SQLite.backup function
def exportDatabase(export_path) -> bool:
    try:
        # Create a new connection for the export file
        with sqlite3.connect(export_path) as target_conn:
            # Use the backup method to copy data from the active connection
            sqlConnection.backup(target_conn)

        logging(message=f"Database successfully exported as {export_path}")
        # Return True to signify operation was successfuls
        return True
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to export database - {str(sql_error)}")
    except Exception:
        logging()


# Query Imported Database and return contents of Users or Passwords table
def importDatabase(import_path, table) -> list:
    try:
        # Connect to the Imported Database
        importConnection = sqlite3.connect(import_path)
        # Create a cursor - read more docs on this
        importCursor = importConnection.cursor()

        importCursor.execute(f"""
            SELECT * 
            FROM vw_{table};
        """)
        # Insert query data to a list
        list_table = importCursor.fetchall()

        # Close the connection to the Imported Database after use
        importConnection.close()

        # Return the list of values
        return list_table
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to query data from {table} - {str(sql_error)}")
    except Exception:
        logging()