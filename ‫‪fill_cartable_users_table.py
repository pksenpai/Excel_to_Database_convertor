from decouple import config
from time import sleep
import logging
import psycopg2
import xlrd
import xlrd2


""" SETTINGS """
# logging:
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s(%(asctime)s): %(name)s --> %(message)s")

# excel:
EXCEL_PATH = "./"
EXCEL_FILE = "users_list.xlsx"

# database:
DB_NAME = config('DB_NAME', cast=str)
DB_USER = config('DB_USER', cast=str)
DB_PASS = config('DB_PASS', cast=str)
DB_HOST = config('DB_HOST', cast=str)
DB_PORT = config('DB_PORT', cast=str)


""" Database Connector """
class Database:
    def __init__(self, db_name, db_user, db_pass, db_host, db_port):
        """ connect to database """
        self.__conn = None
        self._cur = None
        while self.__conn is None:
            try:
                self.__conn = psycopg2.connect(
                                database=db_name,
                                user=db_user,
                                password=db_pass,
                                host=db_host,
                                port=db_port
                            )

                logging.info("Database connected successfully!!!")
            except:
                logging.error("Database NOT connected successfully!!!")
                sleep(1)
                
    def __enter__(self) -> object:
        """ create & return cursor """
        self._cur = self.__conn.cursor()
        return self
    
    def is_empty(self, table):
        self._cur.execute(
            f"""
            SELECT EXISTS (SELECT * FROM {table})
            """
        )
        exists = self._cur.fetchone()[0]
        logging.debug(f"{table} is_empty({not exists})")
        
        return not exists # if exists so not is_empty!
    
    def get_index(self, table : str, col : str = None) -> dict or list:
        """ find values id """
        self._cur.execute(f"SELECT id FROM {table}")
        values_id: list[tuple] = self._cur.fetchall()
        values_id_normalized = self.normalize_database_returns(values_id)
        if col:
            self._cur.execute(f"SELECT {col} FROM {table}")
            values: list[tuple] = self._cur.fetchall()
            values_normalized = self.normalize_database_returns(values)
            
            return dict(zip(values_normalized, values_id_normalized)) # {key="value": value="id"}
        return values_id_normalized

    def is_row_exists(self, table : str, cond: str) -> int:
        """ check a row exists if True returns id """
        self._cur.execute(
            f"""
            SELECT id FROM {table} WHERE {cond}
            """
        )
        id = self._cur.fetchone()
        logging.debug(f"{id} exists!" if id else "row not found!!!")
        
        return None if id is None else id[0]
    
    def select_rows(self, table : str, cond : str) -> list:
        """ check rows exists if True return rows_id """
        self._cur.execute(
            f"""
            SELECT id
            FROM {table}
            WHERE {cond};
            """
        )
        rows_id = self._cur.fetchall()
        return rows_id
    
    def select_columns(self, table : str, cols : str) -> list:
        """ Show Stored Data from a table columns """            
        self._cur.execute(f"SELECT {cols} FROM {table}")
        rows = self._cur.fetchall()
        return rows

    def insert_new_values(self, table : str, cols : str, vals : str) -> object:
        """ add new values """
        self._cur.execute(
            f"""
            INSERT INTO {table}({cols})
            VALUES {vals}
            returning id;
            """
        )
        values_id = self.normalize_database_returns(self._cur.fetchall())
        logging.debug("values added!" if values_id else "values Not added!!!")
        
        return values_id

    def update_rows(self, table : str, cols : tuple, new_values : tuple, ids : tuple):
        """ update values """
        if len(cols) == len(new_values) and len(ids) == len(new_values):
            self._cur.execute(
                f"""
                UPDATE {table}
                SET {', '.join([ f"{col}={repr(val)}" for col, val in zip(cols, new_values)])}
                WHERE id in {ids}
                """
            )
        else:
            logging.error("cols, new_values & ids must be the same length!")
            raise ValueError('ERROR: cols, new_values & ids must be the same length!')
    
    def delete_all_table_values(self, table : str):
        """ remove all values of a table """
        self._cur.execute(
            f"""
            TRUNCATE {table} CASCADE;
            """
        )

    def delete_table_value(self, table : str, cond : str):
        """ remove specific value of a table """
        self._cur.execute(
            f"""
            DELETE FROM {table}
            WHERE {cond};
            """
        )
        logging.debug("value deleted!!!")
        
    @staticmethod
    def normalize_insert_values(values : list or set or tuple) -> str:
        """ Normalize multiple values to use for inserting data at once! """
        return ', '.join(map(lambda e: f'({repr(e)})', values)) #... VALUES ('a'), ('b'), ('c'), ...;
    
    @staticmethod
    def normalize_database_returns(data : list or set or tuple) -> str:
        """ normalize multiple columns to use for inserting data at once! """
        return list(map(lambda e: e[0], data)) # List[Tuple] to List[str|int]

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ commit query & disconnect from database """
        self.__conn.commit()
        self.__conn.close()
        # check committing successfully:
        logging.error(exc_val) if exc_val else logging.info("Done!")


def read_excel_col(file_path : str, file_name : str, page_index : int = 0, col_index : int = 0, start_rowx : int = 1) -> list:
    """ extract data from excel """
    # wb = xlrd.open_workbook(file_path + file_name) # xlrd not supported XLSX files, it used for XLS files
    wb = xlrd2.open_workbook(file_path + file_name) # xlrd version 2 supported XLSX files too
    sheet = wb.sheet_by_index(page_index)
    
    col_values: list = sheet.col_values(col_index, start_rowx=start_rowx) # start from row x...
    return col_values


if __name__ == "__main__":

    DATABASE = Database(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT)

    # Extract Data:
    senders_usernames: list = read_excel_col(EXCEL_PATH, EXCEL_FILE, page_index=1)
    recipients_usernames: list = read_excel_col(EXCEL_PATH, EXCEL_FILE, page_index=1, col_index=1)
    
    # Extract all from Extracted data:
    all_usernames = tuple(set(senders_usernames + recipients_usernames)) # now we have unique usernames! :3
    
    """ Connect to the Database """
    with DATABASE as db:
        
        # Delete All Table Values: 
        # db.delete_all_table_values(table="users")
        # db.delete_all_table_values(table="reports")
        
        # Normalization: 
        all_usernames_normalized: str = db.normalize_insert_values(all_usernames)
        reports_cols = 'sender_id, recipient_id'

        # get username & ids:
        users: dict = db.get_index("users", "username")
        reports_id: list = db.get_index("reports")
        correct_data_id_list = []
        
        # add new values:
        if db.is_empty("reports"):
            # Insert Users Data:
            if not users:
                users_id = db.insert_new_values('users', 'username', all_usernames_normalized)
                users = dict(zip(all_usernames, users_id)) # {key="username": value="id"}
            # Insert Reports Data:
            for sender, recipient in zip(senders_usernames, recipients_usernames):
                vals = f"({users[sender]}, {users[recipient]})" # (sender_id, recipient_id)
                db.insert_new_values(table='reports', cols=reports_cols, vals=vals)
        else:
            for sender, recipient in zip(senders_usernames, recipients_usernames):
                cond = f"sender_id = {users[sender]} AND recipient_id = {users[recipient]}"
                if id := db.is_row_exists("reports", cond):
                    pass # this row already exists!
                else:
                    vals = f"({users[sender]}, {users[recipient]})" # (sender_id, recipient_id)
                    id = db.insert_new_values("reports", reports_cols, vals)[0]

                correct_data_id_list.append(id)
        
        # remove incorrect old values:
        for id in reports_id:
            if id in correct_data_id_list:
                continue
            cond = f"id = {id}"
            db.delete_table_value("reports", cond)
        
        # # Show Data: 
        # users_data = db.select_columns('users', '*')
        # reports_data = db.select_columns('reports', '*')

        # print("users data:", users_data)
        # print("reports data:", reports_data)

    
