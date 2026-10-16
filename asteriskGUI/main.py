
#main.py

import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import datetime
from schemas import HangupRequest 


from routes import web, streamCall, telephony, testAMICommand, extensionSetting
from asterisk_worker import handle_call_events

app = FastAPI(title="Asterisk PBX")
templates = Jinja2Templates(directory="templates")
# Mount the static directory so FastAPI can serve the logo image
app.mount("/static", StaticFiles(directory="data"), name="static")

# Attach structural sub-modules
app.include_router(web.router)
app.include_router(streamCall.router)
app.include_router(telephony.router)
app.include_router(testAMICommand.router)
app.include_router(extensionSetting.router)


@app.on_event("startup")
async def startup_event():
    # Start tracking channels as soon as the webserver spins up
    asyncio.create_task(handle_call_events())
