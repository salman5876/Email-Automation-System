
import base64
import mysql.connector
import requests
from config_database import mysql_config  


def send_email_data(data):
    api_url = "your-api-url"
    authorization_key = "your-api-key"

    headers = {
        "Authorization": authorization_key
    }
 
    response = requests.post(api_url, json=data, headers=headers)

    if response.status_code == 201:
        # Extract the ID from the response JSON
        response_json = response.json()
        issue_id = response_json.get("issue", {}).get("id")
        return issue_id
    else:
        print("Failed to send email data to the API.")
        print("Response:", response.text)
        return None


# MySQL database 
mysql_conn = mysql.connector.connect(**mysql_config)
# Connect to MySQL database
mysql_cursor = mysql_conn.cursor()

# fetch data from db by using join of users and attachment table
mysql_cursor.execute("""
    SELECT e.id, e.subject, e.sender, e.email_address, e.body_message, e.received_time, e.phone_number, e.proccessed, 
           a.file_name, a.content_type, a.content
    FROM emails e 
    LEFT JOIN attachments a ON e.id = a.email_id
    WHERE e.proccessed = 0
      AND DATE(e.received_time) = CURDATE()
""")


results = mysql_cursor.fetchall()

# we need to process only un_proccessed email
processed_emails = set()  

for row in results:
    email_id, subject, sender, email_address, body, received_time, phone_number,  file_name, content_type, proccessed,  content = row
    received_date = received_time.date()
    received_date_formatted = received_date.strftime('%Y-%m-%d')
    # received_date_json = json.dumps(received_date_formatted)
    if phone_number is None or not phone_number.strip():
        phone_number = "0000000000"

    # Check if the email has already been processed
    if email_id in processed_emails:
        continue  # Skip if email already processed
    

    # Initialize data for API ## modify it according to your data 
    data = {
        "summary": subject,
        "description": body,
        "email": email_address,
        "recived_date": received_date_formatted,
        "phone no": phone_number,
       
        "files": []
    }
    
    # Fetch all attachments associated with the current email ID
    attachments = []
    for attachment_row in results:
        attachment_email_id, attachment_file_name, attachment_content_type, attachment_content = attachment_row[0], attachment_row[8], attachment_row[9], attachment_row[10]
        if attachment_email_id == email_id and attachment_file_name and attachment_content_type and attachment_content:
            # Ensure attachment_content is bytes-like
            if isinstance(attachment_content, str):
                attachment_content = attachment_content.encode('utf-8')
                
            # Extract file extension
            file_extension = attachment_file_name.split('.')[-1]
            
            # Combine file content with file extension
            content_with_extension = f"{base64.b64encode(attachment_content).decode('utf-8')}.{file_extension}"
            
            attachment = {
                "name": attachment_file_name,
                "content": content_with_extension  # Content includes both base64 encoded content and file extension
            }
            attachments.append(attachment)


    # Append all attachments to the data
    data["files"] = attachments

    # Update the processed = 1 in the 'emails' table
    mysql_cursor.execute("UPDATE emails SET proccessed = 1 WHERE id = %s", (email_id,))
    mysql_conn.commit()

    # Print the data before sending
    # print(json.dumps(data, indent=4))

    # Add the email ID to the processed set
    processed_emails.add(email_id)

    # Call the function to send data to API 
    # send_email_data(data)


    # API Responce 
        
    # Call the function to send data and capture the issue ID
    issue_id = send_email_data(data)

    # Update the 'issue_id' column in the 'emails' table with the issue ID
    if issue_id:
        mysql_cursor.execute("UPDATE emails SET issue_id = %s WHERE id = %s", (issue_id, email_id))
        mysql_conn.commit()
        print("Email data sent successfully to the API.")
        print("Issue ID:", issue_id, "updated in the database for email ID:", email_id)





# Close MySQL cursor and connection
mysql_cursor.close()
mysql_conn.close()
