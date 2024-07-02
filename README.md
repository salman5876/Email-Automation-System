# Email-Automation-System
Email Automation System is a comprehensive email management system built with Python. It fetches unseen emails, parses them to extract relevant data, extract phone number if present, handles attachments, saves data to a database, processes and sends data to an API, and manages email attachments efficiently. The project is designed to run on a scheduled basis using cron jobs.

## Features
• Fetches only unseen emails from the mailbox.
• Parses emails to extract the sender's name, email address, subject, body, and received time.
• Extracts phone numbers from the email body (if present).
• Handles attachments, allowing only specific types and sizes.
• Cleans the email body to remove extra text.
• Saves the parsed data into a database.
• Marks processed emails as seen.
• Fetches data from the database.
• Processes only unprocessed and current date emails stored in database.
• Converts email attachments into base64 format.
• Converts processed data into JSON format.
• Calls an API to pass the processed data.
• Updates the `proccessed` column for emails that have been processed.
• Adds the issue ID returned by the API to the `issue_id` column
