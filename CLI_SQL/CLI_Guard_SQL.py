# Import SQLite library
import sqlite3

# Import OS library
import os

# Import Traceback for logging
import traceback

# DateTime used for Logging
from datetime import date, datetime, timedelta

today = date.today()
todays_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
tomorrow = date.today() + timedelta(1)



# Write to Debugging Log file
def logging(message=None):
    with open(os.path.join(".", "Logs.txt"), "a") as file:
        #  Handles Traceback since no message argument is passed
        if message is None:
            # traceback.format_exc() function works without explicitly passing an error
            # because it captures the most recent exception from the current context
            file.write(f"[{todays_time}] {traceback.format_exc()}\n")
        else:
            # Handles Logging when a message argument is passed
            file.write(f"[{todays_time}] DATABASE {message}\n")


# Check if database exists
if os.path.exists(os.path.join(os.getcwd(), "CLI_SQL", "CLI_Guard_DB.db")):
    # Connect to the CLI Guard Database
    sqlConnection = sqlite3.connect(os.path.join(os.getcwd(), "CLI_SQL", "CLI_Guard_DB.db"))
    # Create a cursor - read more docs on this
    sqlCursor = sqlConnection.cursor()
else:
    logging(message="ERROR: Could not connect to CLI Guard Database - Default database does not exist or cannot be found")



# Query the passwords table and insert all into list_table ordered by account name or userID
# ? Placeholders in SQL Queries prevent SQL Injection as per the SQLite3 documentation
# The trailing comma when passing Placeholder Bindings avoids the "Incorrect number of bindings supplied" error
# by ensuring the argument is treated as a tuple, which is what execute() expects
# https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
def queryData(user, table, category=None, text=None, sort_by=None) -> list:
    try:
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
            # Convert sort_by fromm Ascending to ASC or Descending to DESC using .upper()[:-6]
            # Convert Category to category using .lower()
            elif sort_by is not None:
                sql_query = (f"""
                    SELECT * 
                    FROM vw_{table}
                    WHERE user = ?
                    ORDER BY {category.lower()} {sort_by.upper()[:-6]};
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
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to query data from {table} - {str(sql_error)}")
    except Exception:
        logging()


# INSERT new user into users SQLite table
def insertMaster(user, password, session_key) -> None:
    try:
        sql_query = (f"""
            INSERT INTO users
            (user, master_pw, master_key, master_last_modified) 
            VALUES(
                ?,
                '{password}',
                '{session_key}',
                '{today}');
            """)
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Created master {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to insert Master User {user} - {str(sql_error)}")
    except Exception:
        logging()


# UPDATE records in the passwords SQLite table
def updateMasterPassword(user, password, session_key) -> None:
    try:
        sql_query = (f"""
            UPDATE users 
            SET master_pw = '{password}', 
                master_key = '{session_key}',
                master_last_modified = '{today}'
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Updated master password for {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to update Master User {user} - {str(sql_error)}")
    except Exception:
        logging()


# DELETE records from the users SQLite table as well as their passwords
def deleteMaster(user) -> None:
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
        logging(message=f"SUCCESS: Deleted master user {user}")
        logging(message=f"SUCCESS: Deleted all passwords for master user {user}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to delete Master User {user} - {str(sql_error)}")
    except Exception:
        logging()


# UPDATE records in the passwords SQLite table
def lockMaster(user) -> None:
    try:
        sql_query = (f"""
            UPDATE users 
            SET last_locked = '{today}' 
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Locked {user} until {tomorrow}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to failed to lock Master User {user} - {str(sql_error)}")
    except Exception:
        logging()


# INSERT new records into passwords SQLite table
def insertData(user, category, account, username, password, session_key) -> None:
    try:
        sql_query = (f"""
            INSERT INTO passwords 
            VALUES(
                ?,
                ?,
                ?,
                ?,
                '{password}',
                '{session_key}',
                '{today}');
            """)
        sqlCursor.execute(sql_query, (user, category, account, username,))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Inserted password for {username}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to insert password for {username} - {str(sql_error)}")
    except Exception:
        logging()


# UPDATE records in the passwords SQLite table
def updateData(password, account, username, old_password, session_key) -> None:
    try:
        sql_query = (f"""
            UPDATE passwords 
            SET password = '{password}', 
                pw_key = '{session_key}',
                last_modified = '{today}' 
            WHERE account = ? 
            AND username = ?
            AND password = '{old_password}';
            """)
        sqlCursor.execute(sql_query,(account,username,))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Updated password for {username}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to update password for {username} - {str(sql_error)}")
    except Exception:
        logging()


# DELETE records from the passwords SQLite table
def deleteData(user, account, username, password) -> None:
    try:
        sql_query = (f"""
            DELETE FROM passwords 
            WHERE user = ?
            AND account = ? 
            AND username = ?
            AND password = '{password}';
            """)
        sqlCursor.execute(sql_query, (user, account, username,))
        sqlConnection.commit()
        logging(message=f"SUCCESS: Deleted password for {username}")
    except sqlite3.IntegrityError as integrity_error:
        logging(message=f"ERROR: SQLite3 data integrity issue - {str(integrity_error)}")
    except sqlite3.OperationalError as op_error:
        logging(message=f"ERROR: SQLite3 operational failure - {str(op_error)}")
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: SQLite3 failed to delete password for {username} - {str(sql_error)}")
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