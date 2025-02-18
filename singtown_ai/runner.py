from pydantic import BaseModel, ValidationError
import os
from uuid import UUID
from typing import List
import requests
from enum import Enum

HOST: str | None
headers = {
    "Authorization": f"Bearer {os.getenv('TRAINER_TOKEN')}"
}

class TaskStatus(str, Enum):
    pending = 'pending'
    succees = 'success'
    failed = 'failed'

class Metric(BaseModel):
    epoch: int
    metric: str

class Task(BaseModel):
    id: UUID
    project: UUID
    status: TaskStatus
    crated_at: str
    epochs: int
    metrics: List[Metric]
    log: str
    result: str

class Label(BaseModel):
    name: str
    color: str
    description: str

class Annotation(BaseModel):
    name: str
    label: str
    url: str

class Project(BaseModel):
    id: UUID 
    type: str  
    author: str  
    license: str  
    labels: List[Label] 
    train: List[Annotation]
    val: List[Annotation]

def login(host: str, token: str):
    global HOST
    global headers
    HOST = host
    headers = {
        "Authorization": f"Bearer {token}"
    }

def retrieve_task(id: UUID):
    response = requests.get(f"{HOST}/tasks/{id}", headers=headers)
    if not response.ok:
        return None
    return Task(**response.json())

def retrieve_project(id: UUID):
    response = requests.get(f"{HOST}/tasks/{id}/project", headers=headers)
    if not response.ok:
        return None
    return Project(**response.json())

def update_status(id:UUID, status:TaskStatus):
    response = requests.post(f"{HOST}/tasks/{id}/status", json={"status": status}, headers=headers)
    if not response.ok:
        return None

def upload_result(id:str, result_file:str):
    with open(result_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{HOST}/tasks/{id}/upload", files=files, headers=headers)
        if not response.ok:
            raise Exception(f"upload error: {response}")

def upload_log(id:UUID, log: str):
    response = requests.post(f"{HOST}/tasks/{id}/log", json={"log": log}, headers=headers)
    if not response.ok:
        return None

def upload_metric(id:UUID, epoch:int, metric:str):
    response = requests.post(f"{HOST}/tasks/{id}/metrics", json={"epoch": epoch, "metric": metric}, headers=headers)
    if not response.ok:
        return None

def downlaod_images(annotations: List[Annotation], save_path: str):
    os.makedirs(save_path, exist_ok=True)
    for anno in annotations:
        with open(os.path.join(save_path, anno.name), "wb") as f:
            f.write(requests.get(anno.url).content)
