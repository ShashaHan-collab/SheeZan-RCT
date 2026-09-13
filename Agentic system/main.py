import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import account, conversation, realtime
from config import web_dir

PORT = 9214

app = FastAPI(title="Wellbeing companion demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account.router)
app.include_router(conversation.router)
app.include_router(realtime.router)

if not os.path.isdir(web_dir):
    raise RuntimeError(
        f"Frontend build not found at {web_dir}.\n"
        "Build it first:  cd user_interaction && npm install && npm run build"
    )
app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
