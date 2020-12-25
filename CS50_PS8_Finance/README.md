To not use CS50 sqlite3 library - https://docs.python.org/3/library/sqlite3.html:

import os
import re
import sqlite3

# from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session

# For sqlite3 (not using CS50): https://docs.python.org/3/library/sqlite3.html
# create a connection object that represents the database
conn = sqlite3.connect('information.db')

# create a Cursor object and call its excecute() method
c = conn.cursor()
c.execute('''
                CREATE TABLE information (
	            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            	city VARCHAR(25),
            	company VARCHAR(30),
            	jcategory VARCHAR(25),
            	jsubcategory VARCHAR(25),
            	jdiffer VARCHAR(25),
            	title VARCHAR(25),
            	yoe TINYINT,
            	base_salary UNSIGNED smallint,
            	bonus UNSIGNED smallint,
            	rsu UNSIGNED smallint,
            	transacted TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)
            '''
              )
# Save (commit) the changes
conn.commit()
# Close the connection. 
conn.close()

=====================================================================================================
Harvard's CS50 - Introduction to Computer Science online course.

Problem set 8:
- Implement a web app that enables a user to register, log-in, look up quotes, buy, sell stocks, and look at transaction history.

Created with: Python, HTML, CSS. It also uses IEX API to get stock values in real time and SQLite DB to store and access information.
