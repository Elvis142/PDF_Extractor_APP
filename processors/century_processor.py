import os
import time
import logging
import re
import ctypes
import pdfplumber  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime


# --- PDF Processing Function ---
def process_century_pdf(pdf_path):
    rows = []
    pattern = re.compile(
        r"([A-Z0-9/]+)\s+(\d{10})\s+(\d+)\s+(PC)\s+(\d{1,4},?\d{0,3})LB/(\d{1,4})KG"
    )

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                for line in text.split('\n'):
                    match = pattern.search(line)
                    if match:
                        batch = match.group(2)
                        weight_lb = int(match.group(5).replace(",", ""))
                        weight_kg = int(match.group(6))
                        rows.append([batch, weight_kg, weight_lb])

        if not rows:
            logging.warning(f"No valid data found in {os.path.basename(pdf_path)}")
            return

        df = pd.DataFrame(rows, columns=["Batch Number", "Net Weight (KG)", "Net Weight (LB)"])

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

