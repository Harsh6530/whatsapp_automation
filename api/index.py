from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import tempfile

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "WhatsApp Automation API is running"}

@app.post("/send-messages")
async def send_messages(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Read the Excel file
        excel_data = pd.read_excel(temp_file_path)
        
        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the driver
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get('https://web.whatsapp.com')
        
        # Wait for QR code scan (in production, you might want to implement a different approach)
        time.sleep(15)  # Give time for manual QR code scan
        
        results = []
        count = 0
        
        for contact in excel_data['Contact'].tolist():
            try:
                url = f'https://web.whatsapp.com/send?phone={contact}&text={excel_data["Message"][0]}'
                driver.get(url)
                
                try:
                    click_btn = WebDriverWait(driver, 35).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, '_3XKXx')))
                    time.sleep(2)
                    click_btn.click()
                    time.sleep(5)
                    results.append({
                        "contact": contact,
                        "status": "success",
                        "message": "Message sent successfully"
                    })
                except Exception as e:
                    results.append({
                        "contact": contact,
                        "status": "error",
                        "message": f"Failed to send message: {str(e)}"
                    })
                
                count += 1
                
            except Exception as e:
                results.append({
                    "contact": contact,
                    "status": "error",
                    "message": f"Failed to process contact: {str(e)}"
                })
        
        driver.quit()
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return {
            "status": "completed",
            "total_processed": count,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 