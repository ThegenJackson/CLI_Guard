# Import SQLite library
import sqlite3

# Import OS library
import os

# DateTime used for Logging
from datetime import datetime

todaysTime = datetime.now().strftime('%Y-%m-%d %H:%M')



# Write to Debugging Log file
def logging(message):
    with open(".\\Logs.txt", "a") as f:
        f.write(f"[{todaysTime}] DATABASE {message}\n")



# Connet to the CLI Guard Database
sql_connection = sqlite3.connect('.\\SQL_DB\\CLI_Guard_DB.db')
# Create a cursor - read more docs on this
sql_cursor = sql_connection.cursor()



# Query the passwords table and insert all into list_pw ordered by account name or userID
def query_data(table) -> list:
    try:
        sql_cursor.execute(f"""
                        SELECT * 
                        FROM vw_{table};
                        """)
        list_pw = sql_cursor.fetchall()
        return list_pw
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to query data from {table} - {str(sql_error)}")
        return []
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")
        return []


# INSERT new user into users SQLite table
def insert_master(user, pw, session_key, today) -> None:
    try:
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
        logging(message = f"SUCCESS: Inserted master user {user}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to insert master user {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# UPDATE records in the passwords SQLite table
def lock_master(user, today) -> None:
    try:
        sql_cursor.execute(f"""
            UPDATE users 
            SET last_locked = '{today}' 
            WHERE user = '{user}';
            """)
        sql_connection.commit()
        logging(message = f"SUCCESS: Locked user {user} until {today}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to lock user {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# INSERT new records into passwords SQLite table
def insert_data(user, category, acct, username, pw, session_key, today) -> None:
    try:
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
        logging(message = f"SUCCESS: Inserted password for user {user} account {acct}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to insert password for user {user} account {acct} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# UPDATE records in the passwords SQLite table
def update_master_pw(user, pw, session_key, today) -> None:
    try:
        sql_cursor.execute(f"""
            UPDATE users 
            SET master_pw = '{pw}', 
                master_key = '{session_key}',
                master_last_modified = '{today}'
            WHERE user = '{user}';
            """)
        sql_connection.commit()
        logging(message = f"SUCCESS: Updated master password for user {user}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to update master password for user {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# UPDATE records in the passwords SQLite table
def update_data(pw, acct, usr, old_pw, session_key, today) -> None:
    try:
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
        logging(message = f"SUCCESS: Updated password for user {usr} account {acct}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to update password for user {usr} account {acct} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# DELETE records from the passwords SQLite table
def delete_data(user, acct, usr, pw) -> None:
    try:
        sql_cursor.execute(f"""
            DELETE FROM passwords 
            WHERE user = '{user}'
            AND account = '{acct}' 
            AND username = '{usr}'
            AND password = '{pw}';
            """)
        sql_connection.commit()
        logging(message = f"SUCCESS: Deleted password for user {user} account {acct}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to delete password for user {user} account {acct} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")