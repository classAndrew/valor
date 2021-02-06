# Connecting to SQL DB for handling server configurations
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
import logging
import time

# in case it hasn't already been done yet
load_dotenv()

class ValorSQL:
    _info = {"host": os.environ["DBHOST"],
        "user": os.environ["DBUSER"],
        "password": os.environ["DBPASS"],
        "database":os.environ["DBNAME"]}
    last_connected = time.time()
    connection_live = 120 # 2 minute(s) per connection
    conn = mysql.connector.connect(**_info)
    @classmethod
    def insert_new_server(cls, *args):
        # get columns N before string indicates unicode
        cls._execute("SHOW columns FROM server_options")
        cols = tuple(c[0] for c in cls._fetchall())
        if len(args) != len(cols):
            raise Exception("DB QUERY: Column Mismatch")
        cls._execute(
            f"INSERT INTO server_options ({', '.join(map(str, cols))}) VALUES ({', '.join(map(str, args))})")
    
    # should probably use a decorator for the ones with _add_new_user
    @classmethod
    def set_user_wynnbuilder(cls, userid: int, pref: str, r: bool):
        cls._add_new_user(userid)
        cls._execute(f"UPDATE user_config SET {pref} = {r} WHERE user_id = {userid}")

    @classmethod
    def get_user_config(cls, userid: int):
        cls._add_new_user(userid)
        res = cls._execute("SHOW columns FROM user_config")
        cols = tuple(c[0] for c in res)
        res = cls._execute(f"SELECT * FROM user_config WHERE user_id = {userid}")
        res = res[0]
        return {cols[i]: res[i] for i in range(len(cols))}

    @classmethod
    def _add_new_user(cls, userid: int):
        res = cls._execute(f"SELECT * FROM user_config WHERE user_id = {userid}")
        if len(res): # if user exists
            return
        res = cls._execute("SHOW columns FROM user_config")
        cols = tuple(c[0] for c in res)
        cls._execute(f"INSERT INTO user_config (user_id) VALUES ({userid})")

    @classmethod
    def _execute(cls, query: str):
        if time.time() - cls.last_connected > cls.connection_live:
            cls.conn.close()
            cls.conn = mysql.connector.connect(**cls._info)
        while not cls.conn.is_connected():
            logging.info("DB disconnected. Now reconnecting")
            cls.conn = mysql.connector.connect(**cls._info)
            cls.last_connected = time.time()
        cursor = cls.conn.cursor()
        cursor.execute(query)
        res = list(cursor.fetchall())
        cls.conn.commit()
        cursor.close()
        return res

    # @classmethod
    # def _reconnect(cls):
    #     print("ValorSQL: Reconnecting to db")
    #     cls.cursor.close()
    #     cls.db.close()
    #     cls.db = mysql.connector.connect(
    #         **cls._info
    #     )

if __name__ == "__main__":
    # ValorSQL.insert_new_server(1, 1)
    ValorSQL._add_new_user(1651)
    cursor = ValorSQL.db.cursor()
    cursor.execute("SELECT * FROM user_config")
    print(cursor.fetchall())