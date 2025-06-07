from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
from script import start_whatsapp_session, send_whatsapp_messages

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session_id = str(uuid.uuid4())
        try:
            start_whatsapp_session(session_id, filepath)
            os.remove(filepath)
            return jsonify({'message': 'WhatsApp Web opened. Please scan QR and click Start Sending.', 'session_id': session_id})
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/start-sending', methods=['POST'])
def start_sending():
    data = request.get_json()
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session_id provided'}), 400
    try:
        print(f"[INFO] Starting to send messages for session: {session_id}")
        results = send_whatsapp_messages(session_id)
        print(f"[INFO] Finished sending messages for session: {session_id}")
        return jsonify({'message': 'Messages sent', 'results': results})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 