import os
import time
import logging
import re
import ctypes
import pdfplumber  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime

# --- PDF Processing Function ---
def process_kitimat_pdf(pdf_path):
    rows = []
    pattern = re.compile(r'^(\d{9})\s+([\d.]+)\s+(\d{5})')

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = [line.strip() for line in text.split('\n') if line.strip()]
                for line in lines:
                    match = pattern.match(line)
                    if match:
                        lot, poids, aa = match.groups()
                        rows.append([lot, poids, aa])

        if not rows:
            logging.warning(f"No valid data found in {os.path.basename(pdf_path)}")
            return

        df = pd.DataFrame(rows, columns=["Lot", "Poids/Lb", "AA"])

        # Save CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{base_name}.csv"
        
        df.to_csv(output_filename, index=False)
        logging.info(f"✅ CSV saved: {output_filename}")

        return output_filename

    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
        return None

