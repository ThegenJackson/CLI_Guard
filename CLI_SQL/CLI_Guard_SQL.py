# Import SQLite library
import sqlite3

# Import OS library
import os

# DateTime used for Logging
from datetime import datetime

todays_time = datetime.now().strftime('%Y-%m-%d %H:%M')



# Write to Debugging Log file
def logging(message):
    with open(".\\Logs.txt", "a") as f:
        f.write(f"[{todays_time}] DATABASE {message}\n")



# Connet to the CLI Guard Database
sqlConnection = sqlite3.connect('.\\CLI_SQL\\CLI_Guard_DB.db')
# Create a cursor - read more docs on this
sqlCursor = sqlConnection.cursor()



# Query the passwords table and insert all into list_passwords ordered by account name or userID
# ? Placeholders in SQL Queries prevent SQL Injection as per the SQLite3 documentation
# https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
def queryData(table, category=None, text=None, sort_by=None) -> list:
    try:
        if text is not None:
            sql_query = f"""
                SELECT * 
                FROM vw_{table}
                WHERE {category} LIKE ?;
            """
            sqlCursor.execute(sql_query, (f"%{text}%",))
        elif sort_by is not None:
            sqlCursor.execute(f"""
                SELECT * 
                FROM vw_{table}
                ORDER BY {category} {sort_by};
            """)
        else:
            sqlCursor.execute(f"""
                SELECT * 
                FROM vw_{table};
            """)

        list_passwords = sqlCursor.fetchall()
        return list_passwords

    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: Failed to query data from {table} - {str(sql_error)}")
        return []
    except Exception as e:
        logging(message=f"ERROR: {str(e)}")
        return []


# INSERT new user into users SQLite table
def insertMaster(user, password, session_key, today) -> None:
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
        sqlCursor.execute(sql_query, (user))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Created master user {user}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to insert master user {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# UPDATE records in the passwords SQLite table
def lockMaster(user, today, tomorrow) -> None:
    try:
        sql_query = (f"""
            UPDATE users 
            SET last_locked = '{today}' 
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Locked master user {user} until {tomorrow}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to lock master user {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# INSERT new records into passwords SQLite table
def insertData(user, category, account, username, password, session_key, today) -> None:
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
        sqlCursor.execute(sql_query, (user, category, account, username))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Inserted password for user {user} account {account}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to insert password for user {user} account {account} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# UPDATE records in the passwords SQLite table
def updateMasterPassword(user, password, session_key, today) -> None:
    try:
        sql_query = (f"""
            UPDATE users 
            SET master_pw = '{password}', 
                master_key = '{session_key}',
                master_last_modified = '{today}'
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Updated master password for user {user}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to update master password for user {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


# UPDATE records in the passwords SQLite table
def updateData(password, account, username, old_password, session_key, today) -> None:
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
        sqlCursor.execute(sql_query,(account,username))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Updated password for user {username} account {account}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to update password for user {username} account {account} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")


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
        sqlCursor.execute(sql_query, (user, account, username))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Deleted password for user {user} account {account}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to delete password for user {user} account {account} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: {str(e)}")