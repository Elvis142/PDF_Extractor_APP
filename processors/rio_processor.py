import os
import time
import logging
import re
import ctypes
import pdfplumber  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime

# --- PDF Processing Function ---
def process_rio_pdf(pdf_path):
    all_rows = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 4:
                        sample_no, lot_no, kg, lb = parts
                        try:
                            kg = float(kg.replace(',', ''))
                            lb = float(lb.replace(',', ''))
                            all_rows.append([sample_no, lot_no, kg, lb])
                        except:
                            continue

        if not all_rows:
            logging.warning(f"No valid rows extracted in: {pdf_path}")
            return

        df = pd.DataFrame(all_rows, columns=[
            "Sample No", "Lot No", "Net Weight (KG)", "Net Weight (LB)"
        ])

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