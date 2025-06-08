# WhatsApp Automation API

This is a WhatsApp automation API that allows you to send bulk messages through WhatsApp Web. The API is designed to be deployed on Vercel.

## Prerequisites

* Python 3.8 or higher
* Chrome browser
* A Vercel account

## Dependencies

The following Python packages are required:
* FastAPI
* Selenium
* Pandas
* Webdriver Manager
* Openpyxl
* Uvicorn
* Python-multipart

## Local Development

1. Install the dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The server will start at `http://localhost:8000`

## Deployment to Vercel

1. Fork or clone this repository
2. Install the Vercel CLI: `npm i -g vercel`
3. Login to Vercel: `vercel login`
4. Deploy the project: `vercel`

## API Usage

### Endpoints

1. `GET /`: Health check endpoint
2. `POST /send-messages`: Send bulk WhatsApp messages

### Sending Messages

To send messages, you need to:

1. Prepare an Excel file with two columns:
   - `Contact`: Phone numbers (with country code, no '+' or spaces)
   - `Message`: The message to send

2. Send a POST request to `/send-messages` with the Excel file as form data.

Example using curl:
```bash
curl -X POST -F "file=@path/to/your/excel/file.xlsx" https://your-vercel-deployment.vercel.app/send-messages
```

## Important Notes

* The API uses headless Chrome for automation
* WhatsApp Web QR code scanning is required for authentication
* The API is rate-limited by WhatsApp's policies
* This is an unofficial implementation and should be used responsibly

## Legal Disclaimer

This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by WhatsApp or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk. Commercial use of this code/repo is strictly prohibited.
