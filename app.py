import os
import re
import logging
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pdfplumber
import pandas as pd

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("alcoa_webapp.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_alcoa_pdf(pdf_path):
    """Process Alcoa PDF and return CSV data"""
    rows = []
    pattern = re.compile(r"(\S+)\s+(\S+)\s+(\d+\.\d{2})\s+PC\s+(\d+)\s+LB/(\d+)\s+KG")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
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
                        rows.append([
                            pkg_bundle, lot_job, qty, "PC", weight_lb, weight_kg
                        ])

        if not rows:
            raise ValueError("No valid data found in PDF")

        # Build DataFrame
        df = pd.DataFrame(rows, columns=[
            "pkg_bundle", "Lot/Job Num", "Qty Ship", "UOM", "Net Weight (LB)", "Net Weight (KG)"
        ])

        df["pkg_bundle"] = df["pkg_bundle"].apply(
            lambda x: x.split('.')[1] if isinstance(x, str) and '.' in x else x
        )
        df["Lot/Job Num"] = df["Lot/Job Num"].str.split('/').str[1]

        # Save CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{base_name}_{timestamp}_packing_list.csv"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

        df.to_csv(output_path, index=False)
        logging.info(f"✅ CSV saved: {output_path}")
        
        return output_filename, len(rows)

    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

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
        
        try:
            # Process the PDF
            csv_filename, row_count = process_alcoa_pdf(filepath)
            
            # Clean up uploaded PDF
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': f'Successfully processed {filename}',
                'csv_file': csv_filename,
                'rows_processed': row_count
            })
        except Exception as e:
            # Clean up uploaded PDF on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({
                'error': f'Error processing PDF: {str(e)}'
            }), 500
    
    return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

@app.route('/processed-files')
def list_processed_files():
    """List all processed CSV files"""
    files = []
    for filename in os.listdir(app.config['PROCESSED_FOLDER']):
        if filename.endswith('.csv'):
            filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
            file_stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': file_stat.st_size,
                'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sort by creation time (newest first)
    files.sort(key=lambda x: x['created'], reverse=True)
    return jsonify(files)

@app.route('/download/<filename>')
def download_file(filename):
    """Download a processed CSV file"""
    try:
        return send_from_directory(
            app.config['PROCESSED_FOLDER'],
            filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a processed CSV file"""
    try:
        filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': f'Deleted {filename}'})
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
