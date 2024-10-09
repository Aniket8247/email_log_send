#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import pickle
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import logging

# Set up logging
logging.basicConfig(filename='send_email.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Google Sheets and OAuth 2.0 setup
CLIENT_SECRET_FILE = 'ServiceAccountGS_OauthCredentials.json'  
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1Q6Q-2-V6uaMyyEbsdu2OeGDfKVuk8nhDE3j4jX9y-ZM'

# Email details
SENDER_EMAIL = "aniket.nichat@blackbuck.com"
SENDER_PASSWORD = "itpdntswlapzlxeu"  
RECEIVER_EMAILS = ['vrushabhnichat@gmail.com']  
CC_EMAILS = ["kartikpande12@gmail.com"]
EMAIL_SUBJECT = "District-Wise Trucks Availability"
EMAIL_BODY_HTML_TEMPLATE = """
<html>
<body>
<p>Hi Team,</p>
<p>I've attached to this email the district-wise truck availability report.</p>
<p>Please review the data and let me know if you have any questions or require further information.</p>
<p>Best regards,<br>Aniket Nichat</p>

<!-- Tracking pixel -->
<img src="http://localhost:8501/?email={receiver_email}" width="1" height="1" alt="" />

</body>
</html>
"""
# Authenticate and access Google Sheets API
def authenticate_and_fetch_data():
    creds = None
    # Load existing credentials from token.pickle
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Only for initial authorization

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    try:
        result = sheet.values().get(spreadsheetId=SHEET_ID, range='Available_SP_file').execute()
        values = result.get('values', [])

        if not values:
            logging.warning('No data found in the sheet.')
            print("No data found in the sheet.")
            return None
        else:
            df = pd.DataFrame(values)
            logging.info('Data fetched successfully from Google Sheets.')
            print("Data fetched successfully from Google Sheets.")
            return df
    except Exception as e:
        logging.error(f"Error fetching data from Google Sheets: {e}")
        print(f"Error fetching data from Google Sheets: {e}")
        return None

# Save the DataFrame as a CSV file
def save_data_as_csv(df, file_name):
    try:
        df.to_csv(file_name, index=False, header=False)
        logging.info(f"Data saved as {file_name}")
        print(f"Data saved as {file_name}")
    except Exception as e:
        logging.error(f"Error saving data to CSV: {e}")
        print(f"Error saving data to CSV: {e}")

# Send an email with the CSV file as an attachment
def send_email_with_attachment(sender, receiver_list, cc_list, subject, body, attachment_file):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ', '.join(receiver_list)
        msg['Cc'] = ', '.join(cc_list)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment_file}')
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, SENDER_PASSWORD)
        server.sendmail(sender, receiver_list + cc_list, msg.as_string())
        server.quit()

        logging.info(f"Email sent to {', '.join(receiver_list)} with CC to {', '.join(cc_list)}")
        print(f"Email sent successfully to {', '.join(receiver_list)} with CC to {', '.join(cc_list)}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        logging.error("Error details: ", exc_info=True)
        print(f"Failed to send email: {e}")

# Main function to fetch data and send it via email
if __name__ == '__main__':
    logging.info('Starting the email sending process...')
    print("Starting the email sending process...")
    
    data_df = authenticate_and_fetch_data()

    if data_df is not None:
        csv_file_name = 'Available_SP_data.csv'
        save_data_as_csv(data_df, csv_file_name)
        send_email_with_attachment(SENDER_EMAIL, RECEIVER_EMAILS, CC_EMAILS, EMAIL_SUBJECT, EMAIL_BODY, csv_file_name)
    else:
        logging.warning("No data to send.")
        print("No data to send.")


# In[ ]:




