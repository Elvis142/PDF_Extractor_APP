import os
import time
import logging
import re
import ctypes
import pdfplumber  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime

# --- PDF Processing Function ---
def process_arvida_pdf(pdf_path):
    rows = []
    pattern = re.compile(r"(\d{9}-\d{2})\s+(\d+)\s+(\S+)\s+(\S+)\s+[\d\.]+\s+[\d\.]+")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for line in text.split('\n'):
                    match = pattern.search(line)
                    if match:
                        lot_number = match.group(1)
                        weight = match.group(2)
                        grade = match.group(3)
                        reference = match.group(4)

                        rows.append([
                            lot_number, weight, grade
                        ])

        if not rows:
            logging.warning(f"No valid data found in {os.path.basename(pdf_path)}")
            return

        df = pd.DataFrame(rows, columns=[
            "Lot Number", "Weight", "Grade"
        ])

        # Save CSV
        
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{base_name}.csv"

        df.to_csv(output_filename, index=False)
        logging.info(f"✅ CSV saved: {output_filename}")

        return output_filename

    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
        return None


