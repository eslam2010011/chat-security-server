from datetime import datetime

import os

from pysondb import db

file_path_session = os.path.join('database', 'session.json')
file_path_chat = os.path.join('database')
file_path_job = os.path.join('database', 'apscheduler.json')
file_path_scripts = os.path.join('database', 'scripts.json')


# hour=hour, minute=minute
class SessionManager:
    def __init__(self):
        try:
            self.session = db.getDb(file_path_session)
            self.jobs = db.getDb(file_path_job)
            self.scripts = db.getDb(file_path_scripts)
        except FileNotFoundError:
            print("FileNotFoundError")

    def add_job(self, job_id, time_zone, task, hour, minute, name):
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        jobId = self.jobs.add(
            {"job_id": job_id, "time_zone": time_zone, "time": int(ts), "task": task, "minute": minute, "hour": hour,
             "jobName": name})

    def remove_job(self, job_id):
        self.jobs.deleteById(int(job_id))

    def get_all_jobs(self):
        return self.jobs.getAll()

    def createSession(self, name):
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        sessionId = self.session.add({"name": name, "time": int(ts), "tabs": []})
        chat_Id = self.createChat(sessionId_=sessionId, question="Welcome New Chat")
        self.session.updateById(sessionId, {"tabs": [chat_Id]})
        return self.session.getById(sessionId)

    def add_new_tab(self, sessionId_):
        chat_Id = self.createChat(sessionId_=sessionId_, question="Welcome New Chat")
        tabs = self.session.getById(sessionId_)["tabs"]
        tabs = tabs + [chat_Id]
        self.session.updateById(sessionId_, {"tabs": tabs})
        return chat_Id

    def remove_session(self, sessionId_):
        _session_ = self.session.getById(sessionId_)
        for tab in _session_["tabs"]:
            if os.path.isfile(f"{file_path_chat}/{tab}.json"):
                os.remove(f"{file_path_chat}/{tab}.json")
        self.session.deleteById(int(sessionId_))
        if os.path.isfile(f"{file_path_chat}/{sessionId_}.json"):
            os.remove(f"{file_path_chat}/{sessionId_}.json")
        return "done"

    def getSessions(self):
        sorted_data = sorted(self.session.getAll(), key=lambda x: x["time"], reverse=True)
        return sorted_data

    def createChat(self, sessionId_, question):
        chat = db.getDb(f"{file_path_chat}/{sessionId_}.json")
        data = chat.add({"question": question, "answer": ""})
        return data

    def updateChat(self, sessionId_, chatId, answer):
        chat = db.getDb(f"{file_path_chat}/{sessionId_}.json")
        last_answer = chat.getById(chatId)["answer"]
        final_answer = f"{last_answer}\n{answer}"
        chat.updateById(chatId, {"answer": final_answer})

    def getChat(self, sessionId_):
        if os.path.exists(f"{file_path_chat}/{sessionId_}.json"):
            chat = db.getDb(f"{file_path_chat}/{sessionId_}.json")
            return chat.getAll()
        else:
            return {"data": None}

    def createJob(self, job_id, command):
        data = self.jobs.add({"job_id": job_id, "command": command})
        return data

    def getScripts(self, name):
        script = db.getDb(f"{file_path_chat}/{name}.json")
        rows = script.getAll()
        if rows:
            last_row = rows[-1]["answer"]
            return last_row
        else:
            return "not found"
