import asyncio
import os
import subprocess

import jwt
import yaml
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import uvicorn as uvicorn
from fastapi import FastAPI, Request, WebSocket, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.v1.APIv1 import APIv1

file_path_session = os.path.join('data', 'apscheduler.json')
secret_key = os.getenv("SECRET_KEY")

app = FastAPI()
app.include_router(APIv1())


async def test():
    code = '''
    def print_hi(name):
        print(f'Hi, {name}')  


    if __name__ == '__main__':
        print_hi('PyCharm')

        '''


    with open("secret_key.py", "wb") as f:
        f.write(code)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

