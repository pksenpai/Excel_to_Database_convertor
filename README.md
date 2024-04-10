# Excel to Database Convertor

## steps before running the program:

1- virtual environment(venv) & libraries:
create a virtual environment, activate it then install libraries with commands blow:
```
>>> python -m venv <venv-name>
>>> .\venv\Scripts\activate
>>> pip install -r requirements.txt
```

2- Check mini_ERD.png:
for know better the database structure...

3- Create .env file:
this file keeps important data such as database and root user data separatly from the program for more security!
After creating .env file, copy the following lines into it:
```
DB_NAME = 
DB_USER = 
DB_PASS = 
DB_HOST = 
DB_PORT = 
```
then fill them with your data...

4- Run db_create.sql script:
Run it to create database & tables with command blow in terminal:
```
>>> psql -U <user> -a -f db_create.sql
```
or use pg_admin...

5- open & set ‫‪excel_conf.txt:
include file_path, file_name & page_index(page number)
it lets you change app conf without open the app source!

6- open or run ‫‪fill_cartable_users_table.py:
open it to see source & set more settings...
OR
run the code in shell with command blow:
```
>>> python ‫‪fill_cartable_users_table.py
```

-now we have a mini ORM :D
_________________________________________________________________

## my preferences:
- I preferred to write it mudolar for clean code if task didn't want the single file...(database.py, excel.py & main.py)
- I trying to run long runtime processes on the database (sql) side
Because SQL is faster than Python and helps to have a more efficient program
- I would be very grateful if you let me know the bugs and tips of my code even if I get rejected so that I can know my weaknesses.

--- Thank you so much ---
