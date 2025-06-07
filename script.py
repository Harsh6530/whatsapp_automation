# Program to send bulk messages through WhatsApp web from an excel sheet without saving contact numbers
# Author @inforkgodara

import threading
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas
from selenium.webdriver.chrome.service import Service
import urllib.parse

# Store sessions in memory (for demo, use a dict; in production, use a better store)
sessions = {}

def start_whatsapp_session(session_id, file_path):
    excel_data = pandas.read_excel(file_path, engine='openpyxl')
    print('Excel data loaded:')
    print(excel_data)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get('https://web.whatsapp.com')
    # Store driver and data for this session
    sessions[session_id] = {
        'driver': driver,
        'data': excel_data
    }
    # Return immediately; user will scan QR and trigger sending from FE
    return True

def send_whatsapp_messages(session_id):
    session = sessions.get(session_id)
    if not session:
        return {'error': 'Session not found'}
    driver = session['driver']
    excel_data = session['data']
    results = []
    for idx, row in excel_data.iterrows():
        phone_number = str(row['Phone Number'])
        name = str(row['Name']) if 'Name' in row else ''
        message = str(row['Message']).replace('{Name}', name)
        print(f'Sending to: {phone_number} | Message: {message}')
        encoded_message = urllib.parse.quote(message)
        try:
            url = f'https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}'
            driver.get(url)
            try:
                click_btn = WebDriverWait(driver, 35).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']")))
            except Exception as e:
                results.append({'phone': phone_number, 'status': 'failed', 'error': str(e)})
            else:
                sleep(2)
                click_btn.click()
                sleep(5)
                results.append({'phone': phone_number, 'status': 'success'})
        except Exception as e:
            results.append({'phone': phone_number, 'status': 'failed', 'error': str(e)})
    driver.quit()
    # Clean up session
    del sessions[session_id]
    return results
