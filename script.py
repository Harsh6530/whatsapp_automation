# Program to send bulk messages through WhatsApp web from an excel sheet without saving contact numbers
# Author @inforkgodara

import threading
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas as pd
from selenium.webdriver.chrome.service import Service
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store sessions in memory (for demo, use a dict; in production, use a better store)
sessions = {}

def validate_excel_data(excel_data):
    """Validate the Excel data structure and content."""
    required_columns = ['Phone Number', 'Message']
    optional_columns = ['Name']
    
    # Check if required columns exist
    missing_columns = [col for col in required_columns if col not in excel_data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Validate data types and content
    for idx, row in excel_data.iterrows():
        # Check phone number
        if pd.isna(row['Phone Number']):
            raise ValueError(f"Empty phone number in row {idx + 2}")
        phone = str(row['Phone Number']).strip()
        if not phone or not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError(f"Invalid phone number in row {idx + 2}: {phone}")
        
        # Check message
        if pd.isna(row['Message']):
            raise ValueError(f"Empty message in row {idx + 2}")
        if not str(row['Message']).strip():
            raise ValueError(f"Empty message in row {idx + 2}")
        
        # Check name if present
        if 'Name' in row and pd.notna(row['Name']):
            if not str(row['Name']).strip():
                raise ValueError(f"Empty name in row {idx + 2}")
    
    return True

def start_whatsapp_session(session_id, file_path):
    try:
        # Read Excel file
        excel_data = pd.read_excel(file_path, engine='openpyxl')
        logger.info('Excel data loaded successfully')
        
        # Validate Excel data
        validate_excel_data(excel_data)
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get('https://web.whatsapp.com')
        
        # Store driver and data for this session
        sessions[session_id] = {
            'driver': driver,
            'data': excel_data
        }
        logger.info(f'Session {session_id} started successfully')
        return True
        
    except Exception as e:
        logger.error(f"Error in start_whatsapp_session: {str(e)}")
        if session_id in sessions:
            try:
                sessions[session_id]['driver'].quit()
            except:
                pass
            del sessions[session_id]
        raise

def send_whatsapp_messages(session_id):
    if session_id not in sessions:
        raise ValueError('Session not found or expired')
    
    session = sessions[session_id]
    driver = session['driver']
    excel_data = session['data']
    results = []
    
    try:
        for idx, row in excel_data.iterrows():
            try:
                # Validate and clean phone number
                phone_number = str(row['Phone Number']).strip()
                if not phone_number or not phone_number.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                    results.append({
                        'phone': phone_number,
                        'status': 'failed',
                        'error': 'Invalid phone number format'
                    })
                    continue
                
                # Validate and clean message
                message = str(row['Message']).strip()
                if not message:
                    results.append({
                        'phone': phone_number,
                        'status': 'failed',
                        'error': 'Empty message'
                    })
                    continue
                
                # Process name if present
                name = str(row['Name']).strip() if 'Name' in row and pd.notna(row['Name']) else ''
                message = message.replace('{Name}', name)
                
                logger.info(f'Sending to: {phone_number} | Message: {message}')
                encoded_message = urllib.parse.quote(message)
                
                # Send message
                url = f'https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}'
                driver.get(url)
                
                try:
                    click_btn = WebDriverWait(driver, 35).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']")))
                    sleep(2)
                    click_btn.click()
                    sleep(5)
                    results.append({
                        'phone': phone_number,
                        'status': 'success'
                    })
                except Exception as e:
                    logger.error(f"Error sending message to {phone_number}: {str(e)}")
                    results.append({
                        'phone': phone_number,
                        'status': 'failed',
                        'error': f'Failed to send message: {str(e)}'
                    })
                    
            except Exception as e:
                logger.error(f"Error processing row {idx + 2}: {str(e)}")
                results.append({
                    'phone': str(row.get('Phone Number', 'N/A')),
                    'status': 'failed',
                    'error': f'Processing error: {str(e)}'
                })
                
    except Exception as e:
        logger.error(f"Error in send_whatsapp_messages: {str(e)}")
        raise
    finally:
        try:
            driver.quit()
        except:
            pass
        if session_id in sessions:
            del sessions[session_id]
    
    return results
