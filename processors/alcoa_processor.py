# alcoa_processor.py
import os
import logging
import re
import pdfplumber  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime


def process_alcoa_pdf(pdf_path):
    """
    Processes an Alcoa PDF and returns the generated CSV file path.
    Same logic preserved — no output folder, no preview.
    """
    rows = []
    pattern = re.compile(r"(\S+)\s+(\S+)\s+(\d+\.\d{2})\s+PC\s+(\d+)\s+LB/(\d+)\s+KG")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                for line in text.split("\n"):
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
            logging.warning(f"No valid data found in {os.path.basename(pdf_path)}")
            return None

        # Build DataFrame (unchanged)
        df = pd.DataFrame(rows, columns=[
            "pkg_bundle", "Lot/Job Num", "Qty Ship", "UOM", "Net Weight (LB)", "Net Weight (KG)"
        ])

        # Clean and split columns
        df["pkg_bundle"] = df["pkg_bundle"].apply(
            lambda x: x.split(".")[1] if isinstance(x, str) and "." in x else x
        )
        df["Lot/Job Num"] = df["Lot/Job Num"].str.split("/").str[1]

        # Save CSV (same timestamped filename in current working directory)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{base_name}.csv"

        df.to_csv(output_filename, index=False)
        logging.info(f"✅ CSV saved: {output_filename}")

        return output_filename

    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
        return None