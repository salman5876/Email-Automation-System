# Email-Automation-System
Email Automation System is a comprehensive email management system built with Python. It fetches unseen emails, parses them to extract relevant data, extract phone number if present, handles attachments, saves data to a database, processes and sends data to an API, and manages email attachments efficiently. The project is designed to run on a scheduled basis using cron jobs.

## Features
- Fetches only unseen emails from the mailbox.
- Parses emails to extract the sender's name, email address, subject, body, and received time.
- Extracts phone numbers from the email body (if present).
- Handles attachments, allowing only specific types and sizes.
- Cleans the email body to remove extra text.
- Saves the parsed data into a database.
- Marks processed emails as seen.
- Fetches data from the database.
- Processes only unprocessed and current date emails stored in database.
- Converts email attachments into base64 format.
- Converts processed data into JSON format.
- Calls an API to pass the processed data.
- Updates the `proccessed` column for emails that have been processed.
- Adds the issue ID returned by the API to the `issue_id` column
- Deletes attachments older than 15 days.
- Runs as a scheduled task using cron.

## Installation

Follow these steps to set up the project:

### 1. Download the Project
- Download the project zip file and extract it to your desired directory.

### 2. Install Required Software
- **VS Code:** Ensure you have Visual Studio Code installed. You can download it from [here](https://code.visualstudio.com/).
- **Python:** Make sure Python is installed on your system. You can download it from [here](https://www.python.org/downloads/).
- **MySQL:** Make sure MySQL is installed and running on your system. You can download it from [here](https://dev.mysql.com/downloads/installer/).

### 3. Install Required Python Libraries
Open your terminal and navigate to the project directory, then run the following command:
- pip install -r requirements.txt


## How to use

To use this project, follow these steps:

### 1. Configure Exchange Server Credentials
- Open `config_exchange_server.py` and add your Exchange Server credentials.

### 2. Set Up the Database
- Open `config_database.py` and add your database credentials.

### 3. Schedule the Script
- Add `execute_file.bat` to Windows Task Scheduler to run at desired intervals.



Feel free to customize the placeholders like `Salman Ahmed`, `mughalsalman616@gmail.com`.


