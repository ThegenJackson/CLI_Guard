# Simple Password Manager Functions

# Import SQLite library
import sqlite3

# Import Python Cryptography library and Fernet module according to documentation
import cryptography
from cryptography.fernet import Fernet

# DateTime used when editing passwords or adding new passwords
from datetime import date


today = date.today()


# Generate the Fernet Encryption Key
# Required for encryption and decryption with Fernet as per documentation
# Since the Encryption Key is generated upon each session, the session's
# Key is converted into a STRING from BITS then the string is written to
# the SQLite database for each password created or added
# We can then later use the Encryption key saved with that record to 
# Decrypt and decode the password
key = Fernet.generate_key()
fernet = Fernet(key)
session_pw_key = key

# Connet to database file included in Simple Program Manager
sql_connection = sqlite3.connect('SPMdb.db')
# Create a cursor - read more docs on this
sql_cursor = sql_connection.cursor()

# Create empty list of encrypted passwords
list_pw = []



# Encrypt
def encrypt_pw(pw):
    # Password is encoded then saved to a new variable per documentation
    encrypted_pw = fernet.encrypt(pw.encode())
    # The variable needs var.decode() when adding to the encrypted passwords table
    # This converts the values datatype from BITS to STRING
    # Otherwise it saves to the list as b'var' instead of 'var'
    # Decode is different to Decrypt, remember to read the docs more
    # The encoded pw is BITS datatype once encrypted and needs it's own variable
    return encrypted_pw.decode()


# Decrypt
def decrypt_pw(key, pw):
    # Decrypted password needs to be saved to its own variable
    # We use Fernet(pw_key) here instead of fernet variable to
    # Decrypt with the relevant records Encryption Key
    decrypted_pw = Fernet(key).decrypt(pw)
    # Remember to DECODE the new variable to convert from BITS datatype to STRING
    # This removes the leading b value changing b'variable' to 'variable'
    return decrypted_pw.decode()


# Query the passwords table and insert all into list_pw ordered by account name
def query_data():
    sql_cursor.execute("""
                        SELECT * 
                        FROM passwords 
                        ORDER BY account ASC;
                        """)
    list_pw = sql_cursor.fetchall()
    return list_pw


# INSERT new records into passwords SQLite table
def insert_data(acct, username, pw):
    sql_cursor.execute(f"""
                    INSERT INTO passwords 
                    VALUES(
                        '{acct}',
                        '{username}',
                        '{pw}',
                        '{session_pw_key.decode()}',
                        '{today}');
                    """)
    sql_connection.commit()


# UPDATE records in the passwords SQLite table
def update_data(pw, acct, usr, old_pw):
    sql_cursor.execute(f"""
                    UPDATE passwords 
                    SET password = '{pw}', 
                    pw_key = '{session_pw_key}',
                    last_modified = '{today}' 
                    WHERE account = '{acct}' 
                    AND username = '{usr}'
                    AND password = '{old_pw}';
                    """)
    sql_connection.commit()


# DELETE records from the passwords SQLite table
def delete_data(acct, usr, pw):
    sql_cursor.execute(f"""
                    DELETE FROM passwords 
                    WHERE account = '{acct}' 
                    AND username = '{usr}'
                    AND password = '{pw}';
                    """)
    sql_connection.commit()