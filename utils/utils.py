import os
import sys
import json
from fastapi import HTTPException

def check_filesystem(pdf_id: str):
    file_path = f"./uploads/{pdf_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            pdf_data = json.load(f)
        return pdf_data
    else:
        raise HTTPException(status_code=404, detail="PDF not found in redis or filesystem.")

