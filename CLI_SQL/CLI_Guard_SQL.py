# Import SQLite library
import sqlite3

# Import OS library
import os

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
# This wraps the shared logger (logger.py) for backward compatibility.
# All existing calls to logging(message="...") continue to work unchanged.
# New code should use: from logger import log; log("DATABASE", "message")
def logging(message=None):
    from logger import log as shared_log
    if message is None:
        shared_log("DATABASE", "Unhandled exception", exc_info=True)
    else:
        shared_log("DATABASE", message)


# Database path constant
# Uses __file__ (not getcwd) so the path is correct regardless of where the CLI is invoked from
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CLI_Guard_DB.db")


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
def queryData(user, table, category=None, text=None, sort_by=None, sort_column=None) -> list:
    try:
        # Ensure database connection is active
        if not ensure_connection():
            logging(message="ERROR: No database connection available")
            return []

        # Validate search column name against whitelist to prevent SQL injection
        if category is not None and category.lower() not in ALLOWED_COLUMNS:
            logging(message=f"ERROR: Invalid column name attempted: {category}")
            raise ValueError(f"Invalid column name: {category}")

        # Validate sort column name against whitelist to prevent SQL injection
        if sort_column is not None and sort_column.lower() not in ALLOWED_COLUMNS:
            logging(message=f"ERROR: Invalid sort column attempted: {sort_column}")
            raise ValueError(f"Invalid sort column: {sort_column}")

        # Validate sort order against whitelist
        if sort_by is not None and sort_by.lower() not in ALLOWED_SORT_ORDERS:
            logging(message=f"ERROR: Invalid sort order attempted: {sort_by}")
            raise ValueError(f"Invalid sort order: {sort_by}")

        if user is not None:
            # Build query incrementally — search and sort can combine
            sql_query = f"SELECT * FROM vw_{table} WHERE user = ?"
            params: list = [user]

            # Apply search filter (WHERE ... LIKE)
            if text is not None and category is not None:
                sql_query += f" AND {category.lower()} LIKE ?"
                params.append(f"%{text}%")

            # Apply sort order (ORDER BY)
            # sort_column is the column to sort by; sort_by is the direction
            # For backward compatibility: if sort_column is None, fall back to category
            effective_sort_col = sort_column if sort_column is not None else category
            if sort_by is not None and effective_sort_col is not None:
                sort_sql = "ASC" if sort_by.lower() == "ascending" else "DESC"
                sql_query += f" ORDER BY {effective_sort_col.lower()} {sort_sql}"

            sqlCursor.execute(sql_query, tuple(params))
            return sqlCursor.fetchall()
        else:
            sqlCursor.execute(f"SELECT * FROM vw_{table}")
            return sqlCursor.fetchall()
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


# ---------------------------------------------------------------------------
# Service Token functions (for token-based CLI authentication)
# ---------------------------------------------------------------------------

def createServiceTokensTable() -> None:
    """Create the service_tokens table and view if they don't exist (migration)"""
    try:
        if not ensure_connection():
            logging(message="ERROR: Cannot create service_tokens table - no database connection")
            return

        sqlCursor.execute("""
            CREATE TABLE IF NOT EXISTS service_tokens (
                token_id        TEXT PRIMARY KEY,
                user            TEXT NOT NULL,
                name            TEXT NOT NULL,
                token_hash      BLOB NOT NULL,
                wrapped_key     TEXT NOT NULL,
                created_at      TEXT NOT NULL,
                expires_at      TEXT,
                last_used       TEXT,
                revoked         INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user) REFERENCES users(user)
            );
        """)
        sqlCursor.execute("""
            CREATE VIEW IF NOT EXISTS vw_service_tokens AS SELECT * FROM service_tokens;
        """)
        sqlConnection.commit()
        logging(message="SUCCESS: service_tokens table ready")
    except sqlite3.OperationalError as op_error:
        # Table may already exist — that's fine
        if "already exists" not in str(op_error):
            logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to create service_tokens table - {str(sql_error)}")
    except Exception:
        logging()


# Run migration on module load (creates table if it doesn't exist)
if sqlConnection is not None:
    try:
        createServiceTokensTable()
    except Exception:
        pass  # Logged internally; don't crash on import


def insertServiceToken(token_id, user, name, token_hash, wrapped_key,
                        created_at, expires_at=None) -> None:
    """Insert a new service token row"""
    try:
        if not ensure_connection():
            logging(message="ERROR: Cannot insert service token - no database connection")
            return

        sql_query = """
            INSERT INTO service_tokens
            (token_id, user, name, token_hash, wrapped_key, created_at, expires_at)
            VALUES(?, ?, ?, ?, ?, ?, ?);
        """
        sqlCursor.execute(sql_query, (token_id, user, name, token_hash,
                                       wrapped_key, created_at, expires_at))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Created service token '{name}' for user '{user}'")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to insert service token - {str(sql_error)}")
    except Exception:
        logging()


def queryServiceToken(token_id) -> tuple | None:
    """Query a single service token by token_id"""
    try:
        if not ensure_connection():
            logging(message="ERROR: No database connection available")
            return None

        sql_query = "SELECT * FROM vw_service_tokens WHERE token_id = ?"
        sqlCursor.execute(sql_query, (token_id,))
        return sqlCursor.fetchone()
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to query service token - {str(sql_error)}")
        return None
    except Exception:
        logging()
        return None


def queryServiceTokensByUser(user) -> list:
    """Query all service tokens for a user (for listing)"""
    try:
        if not ensure_connection():
            logging(message="ERROR: No database connection available")
            return []

        sql_query = "SELECT * FROM vw_service_tokens WHERE user = ?"
        sqlCursor.execute(sql_query, (user,))
        return sqlCursor.fetchall()
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to query service tokens for user '{user}' - {str(sql_error)}")
        return []
    except Exception:
        logging()
        return []


def revokeServiceToken(token_id) -> None:
    """Mark a service token as revoked"""
    try:
        if not ensure_connection():
            logging(message="ERROR: Cannot revoke service token - no database connection")
            return

        sql_query = "UPDATE service_tokens SET revoked = 1 WHERE token_id = ?"
        sqlCursor.execute(sql_query, (token_id,))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Revoked service token '{token_id}'")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to revoke service token - {str(sql_error)}")
    except Exception:
        logging()


def updateServiceTokenLastUsed(token_id, timestamp) -> None:
    """Update the last_used timestamp for a service token"""
    try:
        if not ensure_connection():
            return

        sql_query = "UPDATE service_tokens SET last_used = ? WHERE token_id = ?"
        sqlCursor.execute(sql_query, (timestamp, token_id))
        sqlConnection.commit()
    except sqlite3.Error:
        pass  # Non-critical — don't fail the operation if we can't update last_used
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Database Import/Export
# ---------------------------------------------------------------------------

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