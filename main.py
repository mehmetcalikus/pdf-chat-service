import os
import json
import uvicorn
import requests

import google.generativeai as genai

from uuid import uuid4
from PyPDF2 import PdfReader
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
from google.api_core.exceptions import InvalidArgument, DeadlineExceeded, ResourceExhausted

from constants import *
from pdf_structure import PDF
from middleware import LogMiddleware
from utils.redis_helpers import RedisHelper
from logger import logger

from dotenv import load_dotenv
app = FastAPI()
app.add_middleware(LogMiddleware) # type: ignore
load_dotenv()

redis_helper = RedisHelper(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=int(os.getenv("REDIS_DB")))
gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Request and Response models
class ChatRequest(BaseModel):
    message: str

def make_gemini_api_call(pdf_id: str, pdf_text: str, message: str):
    try:
        # If the question has been asked to the same PDF before, it fetches the answer from the cache. for faq purposes
        cached_answer = redis_helper.get_cached_answer(pdf_id, message)

        if cached_answer:
            return JSONResponse(content={"response": cached_answer.decode()})

        prompt_with_question = prompt_ + message

        response = model.generate_content(
            contents=[pdf_text, prompt_with_question],
            generation_config=generation_config_,
            safety_settings=safety_settings_,
            stream=False,
            request_options=request_options_
        )
        logger.info("Gemini api call done")
        answer = response.candidates[0].content
        redis_helper.cache_answer(pdf_id, message, answer.parts[0].text)
        return JSONResponse(content={"response": answer.parts[0].text})

    except InvalidArgument as e:
        raise HTTPException(status_code=400, detail="Invalid input for the API call: " + str(e))

    except ResourceExhausted as e:  # Rate Limit Reached
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later: " + str(e))

    except DeadlineExceeded as e:  # Timeout
        raise HTTPException(status_code=504, detail="Request timed out. Please try again: " + str(e))

    except requests.exceptions.ConnectionError as e:  # Network Issues
        raise HTTPException(status_code=503, detail="Connection error. Please check your network: " + str(e))

    except Exception as e:  # Catch-all for any other errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


@app.post("/v1/pdf", description="Upload a pdf file")
async def upload_pdf(file: UploadFile = File(...)):
    # Validate the uploaded file
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File type not supported. Please upload a PDF file.")

    pdf_id = str(uuid4()) #unique id for the pdf

    #pdf size validation
    file_content = file.file.read()
    file_size = len(file_content)
    max_size = TEXT_SIZE_LIMIT_MB * 1024 * 1024  # 10 MB limit
    if file_size > max_size:
        raise HTTPException(status_code=413, detail="File size exceeds the limit of 10MB.")


    # Extract text and metadata from the PDF
    try:
        reader = PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        # Creation of pdf object
        pdf = PDF(pdf_id = pdf_id, filename=file.filename, text=text.strip(), page_count=len(reader.pages))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    # Save the PDF object to Redis
    # if redis is not available somehow, save the pdf object to filesystem
    if not redis_helper.save_to_redis(pdf_id, pdf.to_dict()):
        file_path = f"./uploads/{pdf_id}.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(pdf.to_dict(), f)

    return JSONResponse(content={"pdf_id": pdf.pdf_id})


@app.post("/v1/pdf/{pdf_id}", description="Ask a question to uploaded pdf")
async def ask_smth_to_pdf(pdf_id: str, request: ChatRequest):
    try:
        pdf_data = redis_helper.get_pdf_data(pdf_id)
        pdf_text = pdf_data.get("text", "")
        return make_gemini_api_call(pdf_id, pdf_text, request.message)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)