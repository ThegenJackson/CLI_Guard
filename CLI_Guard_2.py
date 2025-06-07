# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

from typing import Any



def getUsers() -> list[list[str]]:

    # Create empty list to insert data into
    users_list: list[list[str]] = []

    # Query Users table
    data: list[list[Any]] = sqlite.queryData(user=None, table="users")
    
    # Loop through query data and insert relevant data to users_list
    for i, user_record in enumerate(data):
        users_list.append([user_record[0]])

    return users_list



def authUser(user: str, attempted_password_hash: bytes) -> bool:

    # Query Users table for User Password Hash
    user_data: str = sqlite.queryData(user, table="users")

    # Compare attempted_password hash against User Password Hash
    if attempted_password_hash == user_data[1]:
        return True
    else:
        return False