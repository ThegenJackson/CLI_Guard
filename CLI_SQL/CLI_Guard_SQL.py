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



# Query the passwords table and insert all into list_table ordered by account name or userID
# ? Placeholders in SQL Queries prevent SQL Injection as per the SQLite3 documentation
# The trailing comma when passing Placeholder Bindings avoids the "Incorrect number of bindings supplied" error
# by ensuring the argument is treated as a tuple, which is what execute() expects
# https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
def queryData(user, table, category=None, text=None, sort_by=None) -> list:
    try:
        if user is not None:
            if text is not None:
                sql_query = f"""
                    SELECT * 
                    FROM vw_{table}
                    WHERE user = ?
                    AND {category} LIKE ?;
                """
                sqlCursor.execute(sql_query, (user, f"%{text}%",))
            elif sort_by is not None:
                sql_query = (f"""
                    SELECT * 
                    FROM vw_{table}
                    WHERE user = ?
                    ORDER BY {category} {sort_by};
                """)
                sqlCursor.execute(sql_query, (user,))
            else:
                sql_query = (f"""
                    SELECT * 
                    FROM vw_{table}
                    WHERE user = ?;
                """)
                sqlCursor.execute(sql_query, (user,))

            list_table = sqlCursor.fetchall()
            return list_table
        else:
            sqlCursor.execute(f"""
                SELECT * 
                FROM vw_{table};
            """)

            list_table = sqlCursor.fetchall()
            return list_table
    except sqlite3.Error as sql_error:
        logging(message=f"ERROR: Failed to query data from {table} - {str(sql_error)}")
        return []
    except Exception as e:
        logging(message=f"ERROR: queryData Function - {str(e)}")
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
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Created master {user}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to insert master {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: insertMaster Function - {str(e)}")


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
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Updated master password for {user}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to update master password for {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: updateMasterPassword - {str(e)}")


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
        logging(message = f"SUCCESS: Deleted master user {user}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to delete master user {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: deleteMaster - {str(e)}")


# UPDATE records in the passwords SQLite table
def lockMaster(user, today, tomorrow) -> None:
    try:
        sql_query = (f"""
            UPDATE users 
            SET last_locked = '{today}' 
            WHERE user = ?;
            """)
        sqlCursor.execute(sql_query, (user,))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Locked {user} until {tomorrow}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to lock master {user} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: lockMaster Function - {str(e)}")


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
        sqlCursor.execute(sql_query, (user, category, account, username,))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Inserted password for {username}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to insert password for {username} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: insertData Function - {str(e)}")


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
        sqlCursor.execute(sql_query,(account,username,))
        sqlConnection.commit()
        logging(message = f"SUCCESS: Updated password for {username}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to update password for {username} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: updateDataFunction - {str(e)}")


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
        logging(message = f"SUCCESS: Deleted password for {username}")
    except sqlite3.Error as sql_error:
        logging(message = f"ERROR: Failed to delete password for {username} - {str(sql_error)}")
    except Exception as e:
        logging(message = f"ERROR: deleteData - {str(e)}")