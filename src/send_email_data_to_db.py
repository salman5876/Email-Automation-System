from exchangelib import Credentials, Account, DELEGATE, FileAttachment, Message, Configuration
import datetime
import mysql.connector
import html2text
import re
from config_database import mysql_config  
from config_exchange_server import mailboxes 



def connect_exchange_mailbox(email, password, server):
    user_credentials = Credentials(email, password)
    config = Configuration(server=server, credentials=user_credentials)
    account = Account(primary_smtp_address=email, credentials=user_credentials, config=config, autodiscover=False)
    return account


# MySQL database 
mysql_conn = mysql.connector.connect(**mysql_config)

# Define the timezone for Pakistan (Asia/Karachi)
timezone = 'Asia/Karachi'

# function to pick number from email message 
def extract_phone_numbers_from_email(body_message):
    phoneRegex = re.compile(r'''
        \b                                  # word boundary
        (?:                                 # start of country code group
            \+?\d{1,3}\s*                   # optional plus sign and one to three-digit country code
            |                               # or
            0                               # zero for local numbers
            |                               # or
            \d{1,3}\s*                      # just the country code
        )?                                  # end of country code group (optional)
        \s*                                 # optional whitespace
        (?:                                 # start of main phone number group
            \d{3}                           # three digits
            (?:[\s-]|\s*\(\d{3}\)\s*|-)?    # optional separator (whitespace, hyphen, or parentheses)
            \d{3}                           # three digits
            (?:[\s-]|\s*\(\d{3}\)\s*|-)?    # optional separator
            \d{4}                           # four digits
        )                                   # end of main phone number group
        \b                                  # word boundary
    ''', re.VERBOSE)
    return phoneRegex.findall(body_message)


# remove extra text from email
def remove_external_message(email):

    start_index = email.find("**_[EXTERNAL MESSAGE]_**")

    if start_index != -1:
        end_index = email.find("****.", start_index) + len("****.**")
        body_message_clean = email[:start_index] + email[end_index:]
    else:
        body_message_clean = email

    body_message_clean = body_message_clean.strip()
    
    return body_message_clean


# Connect to MySQL database
mysql_cursor = mysql_conn.cursor()

# Fetch only unseen emails
def process_emails(account, mysql_conn):
    unseen_emails = account.inbox.filter(is_read=False)

    # Iterate through unseen emails in the inbox
    for item in unseen_emails:
        if isinstance(item, Message):
            subject = item.subject
            sender = str(item.sender)
            sender_name = item.sender.name
            email_address = item.sender.email_address
            sender = f"{sender_name} <{email_address}>"
            
            # Convert HTML body to plain text
            body_html = str(item.body)
            body_message = html2text.html2text(body_html)
            # remove scrap data from email body
            body_message_clean = remove_external_message(body_message)


            received_time = item.datetime_received.isoformat()
            received_time = datetime.datetime.strptime(received_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
            
            # extracting phone number from emial body
            phone_numbers = extract_phone_numbers_from_email(body_message)
            # Convert phone_numbers list to a comma-separated string
            phone_numb = ', '.join(phone_numbers)


            # Define the allowed file types and size limit
            allowed_file_types = {'pdf', 'jpg', 'jpeg', 'png'}
            size_limit = 2 * 1024 * 1024  # 2MB 

            attachments_data = []
            attachments_issues = []

            for attachment in item.attachments:
                if isinstance(attachment, FileAttachment):
                    attachment_size = len(attachment.content)  
                    file_extension = attachment.name.split('.')[-1].lower() 
                    
                    if attachment_size < size_limit and file_extension in allowed_file_types:
                        attachment_data = {
                            'file_name': attachment.name,
                            'content_type': attachment.content_type,
                            'content': attachment.content,
                            'attachment_issue': None
                        }
                        attachments_data.append(attachment_data)
                    else:
                        issue_reason = 'File size exceed to maximum allowed limit' if attachment_size >= size_limit else 'File type not allowed'
                        attachment_issue = {
                            'file_name': attachment.name,
                            'content_type': attachment.content_type,
                            'content': None,
                            'attachment_issue': issue_reason
                        }
                        attachments_issues.append(attachment_issue)

            mysql_cursor.execute(
                "INSERT INTO emails (subject, sender, email_address, body, body_message, received_time, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (subject, sender, email_address, body_html, body_message_clean, received_time, phone_numb)
            )
            email_id = mysql_cursor.lastrowid

            # Insert valid attachments
            for attachment_data in attachments_data:
                mysql_cursor.execute(
                    "INSERT INTO attachments (email_id, file_name, content_type, content, attachment_issue) VALUES (%s, %s, %s, %s, %s)",
                    (email_id, attachment_data['file_name'], attachment_data['content_type'], attachment_data['content'], attachment_data['attachment_issue'])
            )

            # Insert attachments with issues
            for attachment_issue in attachments_issues:
                mysql_cursor.execute(
                    "INSERT INTO attachments (email_id, file_name, content_type, content, attachment_issue) VALUES (%s, %s, %s, %s, %s)",
                    (email_id, attachment_issue['file_name'], attachment_issue['content_type'], attachment_issue['content'], attachment_issue['attachment_issue'])
            )

            # Mark the email as read
            item.is_read = True
            item.save()

            mysql_conn.commit()

for mailbox_info in mailboxes:
    email = mailbox_info['email']
    password = mailbox_info['password']
    server = mailbox_info['server']
    account = connect_exchange_mailbox(email, password, server)
    process_emails(account, mysql_conn)



# Close MySQL database connection
mysql_cursor.close()
mysql_conn.close()

