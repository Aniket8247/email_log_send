import streamlit as st
from datetime import datetime
import pandas as pd
import os
from PIL import Image
import io

# To log email opens
log_file = 'email_tracking_log.csv'

# Check if the log file exists; if not, create it
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write("Email,Timestamp\n")  # Write headers for the CSV file

# Function to log email open events
def log_email_open(email):
    with open(log_file, 'a') as f:
        f.write(f"{email},{datetime.now()}\n")

# Function to create a 1x1 transparent pixel
def create_transparent_pixel():
    pixel = Image.new("RGBA", (1, 1), (0, 0, 0, 0))  # Create a 1x1 transparent image
    return pixel

# Streamlit app
def main():
    st.title("Email Tracking App")

    # Get the email from the query parameter
    query_params = st.query_params
    email = query_params.get("email", ["unknown"])[0]

    # Log the email open
    if email != "unknown":
        log_email_open(email)
        st.write(f"Tracked email open for: {email}")

    # Create a transparent pixel image and display it
    pixel_image = create_transparent_pixel()
    buf = io.BytesIO()
    pixel_image.save(buf, format='PNG')
    byte_im = buf.getvalue()
    st.image(byte_im, width=1)

    # Optionally display the tracking log if you want to view it in the app
    if st.checkbox("Show Tracking Log"):
        log_df = pd.read_csv(log_file, names=["Email", "Timestamp"])
        st.write(log_df)

if __name__ == "__main__":
    main()
