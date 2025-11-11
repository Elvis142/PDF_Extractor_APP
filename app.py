import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from io import BytesIO
import tempfile

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

# Store processed files in memory during session
processed_files = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_pdf(pdf_path):
    """
    Process Alcoa packing list PDFs and extract structured data
    Extracts: pkg_bundle, lot/job number, quantity, UOM, weight (LB/KG)
    """
    try:
        import pdfplumber
        import re
        
        rows = []
        # Pattern matches: BUNDLE LOT/JOB QTY PC WEIGHT_LB LB/WEIGHT_KG KG
        pattern = re.compile(r"(\S+)\s+(\S+)\s+(\d+\.\d{2})\s+PC\s+(\d+)\s+LB/(\d+)\s+KG")
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                    
                for line in text.split('\n'):
                    match = pattern.search(line)
                    if match:
                        pkg_bundle = match.group(1)
                        lot_job = match.group(2)
                        qty = float(match.group(3))
                        weight_lb = int(match.group(4))
                        weight_kg = int(match.group(5))
                        
                        # Parse pkg_bundle: extract second part after dot
                        if isinstance(pkg_bundle, str) and '.' in pkg_bundle:
                            pkg_bundle = pkg_bundle.split('.')[1]
                        
                        # Parse lot_job: extract second part after slash
                        if isinstance(lot_job, str) and '/' in lot_job:
                            lot_job = lot_job.split('/')[1]
                        
                        rows.append({
                            'pkg_bundle': pkg_bundle,
                            'Lot/Job Num': lot_job,
                            'Qty Ship': qty,
                            'UOM': 'PC',
                            'Net Weight (LB)': weight_lb,
                            'Net Weight (KG)': weight_kg
                        })
        
        return rows if rows else None
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the PDF
        processed_data = process_pdf(filepath)
        
        if processed_data is None:
            os.remove(filepath)
            return jsonify({'error': 'Failed to process PDF'}), 400
        
        # Store the result
        file_id = filename.replace('.pdf', '').replace(' ', '_')
        processed_files[file_id] = {
            'filename': filename,
            'filepath': filepath,
            'data': processed_data
        }
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {filename}',
            'file_id': file_id,
            'data': processed_data
        })
    
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    if file_id not in processed_files:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        file_info = processed_files[file_id]
        df = pd.DataFrame(file_info['data'])
        
        # Create CSV in memory
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        csv_filename = file_id + '.csv'
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=csv_filename
        )
    
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/list-files', methods=['GET'])
def list_files():
    files_list = [
        {'file_id': fid, 'filename': info['filename']}
        for fid, info in processed_files.items()
    ]
    return jsonify({'files': files_list})

@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    if file_id in processed_files:
        try:
            filepath = processed_files[file_id]['filepath']
            if os.path.exists(filepath):
                os.remove(filepath)
            del processed_files[file_id]
            return jsonify({'success': True, 'message': 'File deleted'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
