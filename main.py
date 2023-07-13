import os

import uvicorn as uvicorn
from fastapi import FastAPI

from app.api.v1.APIv1 import APIv1

app = FastAPI()
app.include_router(APIv1())


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


if __name__ == "__main__":
    create_folder("tools_v1")
    create_folder("database")
    uvicorn.run(app, host="0.0.0.0", port=8001)
