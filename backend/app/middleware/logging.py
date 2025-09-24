# app/middleware/logging.py
import logging

logging.basicConfig(filename="app.log", level=logging.INFO)

async def log_requests(request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response: {response.status_code}")
    return response