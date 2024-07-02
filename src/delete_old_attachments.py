import mysql.connector
from config_database import mysql_config


mysql_conn = mysql.connector.connect(**mysql_config)
mysql_cursor = mysql_conn.cursor()

# SQL query to delete rows from the attachments table where received_time is more than 15 days old and processed = 1
delete_query = """
    DELETE a FROM attachments a
    INNER JOIN emails e ON a.email_id = e.id
    WHERE e.received_time < NOW() - INTERVAL 15 DAY AND e.proccessed = 1
"""

mysql_cursor.execute(delete_query)

mysql_conn.commit()

# Print the number of rows deleted
print(f"Number of rows deleted: {mysql_cursor.rowcount}")

# Close MySQL cursor and connection
mysql_cursor.close()
mysql_conn.close()
