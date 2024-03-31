# Import SQLite library
import sqlite3

# Connet to database file included in Simple Program Manager
sql_connection = sqlite3.connect('SPMdb.db')
# Create a cursor - read more docs on this
sql_cursor = sql_connection.cursor()



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
def insert_data(user, acct, username, pw, session_key, today) -> None:
    sql_cursor.execute(f"""
                    INSERT INTO passwords 
                    VALUES(
                        '{user}',
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