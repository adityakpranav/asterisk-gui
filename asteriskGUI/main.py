
#main.py

import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
from logger import logger
import datetime
from schemas import HangupRequest 
from config import FILTER_URLS

from routes import web, streamCall, telephony, testAMICommand, extensionSetting, streamConfCall
from asterisk_worker import handle_call_events

app = FastAPI(title="Asterisk PBX")
templates = Jinja2Templates(directory="templates")
# Mount the static directory so FastAPI can serve the logo image
app.mount("/static", StaticFiles(directory="data"), name="static")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    # Extract client IP and store on request.state
    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = (
        forwarded_for.split(",").strip()
        if forwarded_for
        else (request.client.host if request.client else "Unknown")
    )
    request.state.client_ip = client_ip

    response = await call_next(request)
    
    if (request.url.path not in FILTER_URLS):
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"IP: {client_ip} | {request.method} {request.url.path} | "
            f"Status: {response.status_code} | {duration_ms:.2f}ms"
        )

    return response

# Attach structural sub-modules
app.include_router(web.router)
app.include_router(streamCall.router)
app.include_router(telephony.router)
app.include_router(testAMICommand.router)
app.include_router(extensionSetting.router)
app.include_router(streamConfCall.router)


@app.on_event("startup")
async def startup_event():
    # Start tracking channels as soon as the webserver spins up
    asyncio.create_task(handle_call_events())
