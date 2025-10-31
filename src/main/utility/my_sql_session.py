import sys
import os
# Add project root (mart_project) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from resources import config
import pandas as pd
import mysql.connector   
from mysql.connector import Error


def get_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host=config.destination_host,
            user=config.destination_username,
            password=config.destination_password,
            database=config.destination_database_name,
        )

        if connection.is_connected():
            print("✅ Connected to MySQL database")
            return connection

    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        sys.exit(1)

# get_mysql_connection()
#     cursor = connection.cursor()

# # Execute a SQL query
# query = "SELECT * FROM product_staging_table"
# cursor.execute(query)

# # Fetch and print the results
# for row in cursor.fetchall():
#     print(row)

# # Close the cursor
# cursor.close()

# connection.close()
