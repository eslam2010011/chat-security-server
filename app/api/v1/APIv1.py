import os
import shutil
import zipfile

import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File, Query
from fastapi import Request
from jwt import PyJWTError
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse, FileResponse
from starlette.websockets import WebSocket

from app.core.JobManager import JobManager
from app.core.SessionManager import SessionManager
from app.core.SubprocessManager import SubprocessManager
from app.core.ToolRunner import ToolRunner
from app.core.YAMLFileManager import YAMLFileManager

from app.helper.JWTManager import JWTManager
from app.helper.requests_tor import RequestsTor

file_path = os.path.join('database', 'apscheduler.json')
file_path_cs_tools = os.path.join('resources', 'cs_tools.yaml')
file_path_cs_programs = os.path.join('resources', 'programs.yaml')
file_path_cs_installed_tools = os.path.join('resources', 'installed_tools.yaml')
file_path_cs_installed_words = os.path.join('resources', 'words.yaml')

jwt = JWTManager()
manager = SubprocessManager()
ROOT_DIR = os.path.join('tools_v1')
ROOT_Scripts = os.path.join("scripts")
os.getenv("")
tool_runner = ToolRunner(file_path_cs_tools, ROOT_DIR, ROOT_Scripts)
programs = YAMLFileManager(file_path_cs_programs)
install = YAMLFileManager(file_path_cs_installed_tools)
words = YAMLFileManager(file_path_cs_installed_words)
tools = YAMLFileManager(file_path_cs_tools)
scheduler = AsyncIOScheduler()
job = JobManager()


# rt = RequestsTor()


async def verify_token(x_api_key: str = Header(None)):
    try:
        if not x_api_key:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        p = jwt.decode_token(x_api_key)

        return p
    except (KeyError, IndexError, PyJWTError):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


class APIv1(APIRouter):
    global_dependency = Depends(verify_token)

    def __init__(self):
        super().__init__(dependencies=[Depends(verify_token)])
        self.setup_routes()
        self.dependencies = [Depends(verify_token)]

    def setup_routes(self):

        @self.get("/tools")
        def read_tools():
            return {"data": tool_runner.get_Tools().search_name_tools(install.read_data()["tools"])}

        @self.post("/tools")
        async def update_tools(request: Request):
            data = await request.json()
            tools2 = data["tools"]
            yaml_data = yaml.safe_load(tools2)
            parsed_data = tools.read_data()
            parsed_data["tools"].append(yaml_data)
            updated_yaml = tools.write_data(parsed_data)

            return {"data": "done"}

        @self.post("/upload-folder")
        async def upload_folder(file: UploadFile = File(...)):
            try:
                temp_file_path = f"{ROOT_Scripts}/{file.filename}"
                with open(temp_file_path, "wb") as temp_file:
                    shutil.copyfileobj(file.file, temp_file)

                return JSONResponse({"message": "Zip file uploaded successfully"})
            except Exception as e:
                return JSONResponse({"message": "Failed to upload zip file", "error": str(e)})

        @self.post("/script")
        async def add_script(request: Request):
            data = await request.json()
            tools2 = data["script"]
            name = data["name"]
            file_path = ROOT_Scripts + "/" + name
            with open('{}'.format(file_path), 'w') as file:
                file.write(tools2)
            return {"data": "done"}

        @self.get("/get_scripts")
        async def get_scripts():
            extensions = {
                ".java": "java",
                ".py": "python",
                ".js": "node",
                ".rb": "ruby",
                ".sh": "bash",
                ".go": "go run",
                ".rs": "rustc",
            }
            results = []
            for root, dirs, files in os.walk(ROOT_Scripts):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_extension = os.path.splitext(file)[1]
                    if file_extension in extensions:
                        command = extensions[file_extension] + " " + file_path
                        result = {
                            "fileName": file,
                            "command": command,
                        }
                        results.append(result)

            return {"data": results}

        @self.post("/run_scripts")
        async def run_scripts(request: Request, background_tasks: BackgroundTasks):
            data = await request.json()
            session_id = data["session_id"]
            command = data["command"]
            name = data["name"]
            background_tasks.add_task(tool_runner.read_subprocess_output_without_websocket, name, command)
            return {"data": "Script  started in the background"}

        @self.get("/get_output_script")
        async def run_scripts(name: str = Query(...)):

            return {"data": tool_runner.get_session_manager().getScripts(name)}

        @self.get("/words")
        def words():
            return {"data": words.read_data()}

        @self.get("/programs")
        def programs():
            return {"data": tool_runner.get_programs().read_data()}

        @self.get("/search_tools")
        def search_tools(query: str):
            results = tool_runner.get_Tools().search_key_value_autocomplete(query)
            return {"data": results}

        @self.get("/tools/{tool_name}")
        def search_name_tools(tool_name: str):
            return {"data": tool_runner.get_Tools().search_name_tools(tool_name)}

        @self.get("/tools/{tool_name}")
        def install_tools(tool_name: str):
            return {"data": tool_runner.get_Tools().search_name_tools(tool_name)}

        @self.get("/tools/{category}")
        def read_root(category: str):
            return {"data": tool_runner.get_Tools().search_key_value("category", category)}

        @self.get("/{session_id}/chat")
        def read_root(session_id: str):
            return {"data": SessionManager().getChat(session_id)}

        @self.get("/start_scheduler")
        async def start_scheduler():
            return {"message": "Scheduler started."}

        @self.get("/stop_scheduler")
        async def stop_scheduler():
            scheduler.shutdown(wait=False)
            return {"data": "Scheduler stopped."}

        @self.post("/add_new_tab")
        async def add_new_tab(request: Request):
            data = await request.json()
            return {"data": tool_runner.get_session_manager().add_new_tab(sessionId_=data["session_id"])}

        @self.post("/add_job")
        async def add_job(request: Request):
            data = await request.json()
            tool_runner.session_id = data["session_id"]
            tool_runner.add_job(hour=data["hour"], minute=data["minute"], command=data["command"],
                                jobName=data["jobName"])
            return {"data": "Job added successfully"}

        @self.post("/remove_job")
        async def add_job(request: Request):
            data = await request.json()
            tool_runner.remove_job(data["job_id"])
            return {"data": "Job removed successfully"}

        @self.get("/jobs")
        def get_all_jobs():
            return {"data": tool_runner.get_session_manager().get_all_jobs()}

        @self.get("/sessions")
        def get_sessions():
            return {"data": SessionManager().getSessions()}

        @self.get("/{name}/sessions")
        def create_session(name: str):
            return {"data": SessionManager().createSession(name)}

        @self.post("/session/remove")
        async def remove_session(request: Request):
            data = await request.json()
            tool_runner.session_id = data["session_id"]
            print(data["session_id"])
            return {"data": tool_runner.removeSession()}

        @self.websocket("/{tool_name}/run_tool")
        async def websocket_endpoint(tool_name: str, websocket: WebSocket, token=Depends(verify_token)):
            await websocket.accept()
            await tool_runner.run_tool(tool_name, websocket)
            await websocket.close()

        @self.websocket("/{session_id}/chat")
        async def websocket_endpoint(session_id: str, websocket: WebSocket, token=Depends(verify_token)):
            await websocket.accept()
            await tool_runner.run_tool(session_id, websocket)
            await websocket.close()

        @self.websocket("/{tool_name}/install")
        async def websocket_endpoint(tool_name: str, websocket: WebSocket, token=Depends(verify_token)):
            await websocket.accept()
            command = await websocket.receive_json()
            tool_runner.session_id = command["session_id"]
            parsed_data = install.read_data()
            parsed_data["tools"].append(tool_name)
            updated_yaml = install.write_data(parsed_data)
            await tool_runner.install_tool(tool_name, websocket)
            await websocket.close()

        @self.websocket("/{tool_name}/uninstall")
        async def websocket_endpoint(tool_name: str, websocket: WebSocket, token=Depends(verify_token)):
            await websocket.accept()
            await tool_runner.install_tool(tool_name, websocket)
            await websocket.close()

        @self.websocket("/")
        async def websocket_endpoint(websocket: WebSocket, token=Depends(verify_token)):
            await websocket.accept()
            await websocket.close()

        @self.websocket("/commander")
        async def websocket_endpoint(websocket: WebSocket, token=Depends(verify_token)):
            await websocket.accept()
            command = await websocket.receive_json()
            tool_runner.session_id = command["session_id"]
            await tool_runner.run(command=command, websocket=websocket)
            await websocket.close()
