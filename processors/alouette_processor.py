import os
import time
import logging
import re
import ctypes
import pdfplumber  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime


# --- PDF Processing Function ---
def process_alouette_pdf(pdf_path):
    rows = []
    # Updated regex pattern with thousands separator for line number
    pattern = re.compile(
        r"(\d{1,3}(?:,\d{3})?)\s+([A-Z0-9]+)\s+(\d{2})\s+[\d.,]+\s+[\d.,]+\s+[\d.,]+\s+[\d.,]+\s+(\d+)\s+([\d,]+)"
    )

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for line in text.split('\n'):
                    match = pattern.search(line)
                    if match:
                        line_number = int(match.group(1).replace(",", ""))
                        serial = match.group(2)
                        item_num = match.group(3)
                        net_kg = int(match.group(4))
                        net_lb = int(match.group(5).replace(",", ""))

                        rows.append([
                            line_number, serial, item_num, net_kg, net_lb
                        ])

        if not rows:
            logging.warning(f"No valid data found in {os.path.basename(pdf_path)}")
            return

        df = pd.DataFrame(rows, columns=[
            "Line Number", "Serial Number", "Item Number", "Net Weight (KG)", "Net Weight (LBS)"
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

