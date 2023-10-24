from typing import List
import traceback
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from ...core.protocaas_types import ProtocaasProject, ProtocaasFile, ProtocaasJob
from ...clients.db import fetch_project, fetch_project_files, fetch_project_jobs

router = APIRouter()

# get project
class GetProjectResponse(BaseModel):
    project: ProtocaasProject
    success: bool

class ProjectError(Exception):
    pass

@router.get("/projects/{project_id}")
async def get_project(project_id) -> GetProjectResponse:
    try:
        project = await fetch_project(project_id)
        if project is None:
            raise ProjectError(f"No project with ID {project_id}")
        return GetProjectResponse(project=project, success=True)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e

# get project files
class GetProjectFilesResponse(BaseModel):
    files: List[ProtocaasFile]
    success: bool

@router.get("/projects/{project_id}/files")
async def get_project_files(project_id) -> GetProjectFilesResponse:
    try:
        files = await fetch_project_files(project_id)
        return GetProjectFilesResponse(files=files, success=True)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e

# get project jobs
class GetProjectJobsResponse(BaseModel):
    jobs: List[ProtocaasJob]
    success: bool

@router.get("/projects/{project_id}/jobs")
async def get_project_jobs(project_id) -> GetProjectJobsResponse:
    try:
        jobs = await fetch_project_jobs(project_id)
        return GetProjectJobsResponse(jobs=jobs, success=True)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e