"""
main.py — the FastAPI web server.

Endpoints so far:
  POST /upload   upload a .zip of a Python project, get back the dependency graph
  POST /impact   for one function: who calls it, what it calls, what could break

Run from backend/:
    uvicorn main:app --reload --port 8000
Then try it at http://localhost:8000/docs
"""

import io
import os
import shutil
import tempfile
import uuid
import zipfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from extractor import extract_project
from graph_builder import build_graph, get_impact, graph_to_json

MAX_UPLOAD_BYTES = 20 * 1024 * 1024        # 20 MB zip file
MAX_UNZIPPED_BYTES = 200 * 1024 * 1024     # stop "zip bombs" that expand to huge sizes

app = FastAPI(title="Codebase X-Ray")

# Let the React dev server (port 5173) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage: project_id -> {"graph": networkx graph, "nodes": {node_id: node}}
# (Everything is lost when the server restarts. That's fine for a hackathon.)
PROJECTS = {}


def safe_extract(zip_file, dest):
    """Unzip into dest, refusing any entry that tries to escape dest (zip-slip)."""
    dest = os.path.realpath(dest)
    total_size = 0
    for member in zip_file.infolist():
        # Skip junk folders that macOS adds to zips.
        if member.filename.startswith("__MACOSX/"):
            continue
        target = os.path.realpath(os.path.join(dest, member.filename))
        if target != dest and not target.startswith(dest + os.sep):
            raise HTTPException(400, f"Unsafe path in zip: {member.filename}")
        total_size += member.file_size
        if total_size > MAX_UNZIPPED_BYTES:
            raise HTTPException(400, "Zip expands to more than 200 MB.")
        zip_file.extract(member, dest)


def find_project_root(folder):
    """If the zip has just one top-level folder (e.g. my_project/), use that as the root."""
    entries = [e for e in os.listdir(folder) if not e.startswith(".")]
    if len(entries) == 1 and os.path.isdir(os.path.join(folder, entries[0])):
        return os.path.join(folder, entries[0])
    return folder


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # 1. Basic checks: must be a .zip and not too big.
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Please upload a .zip file.")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, "Zip file is larger than 20 MB.")

    # 2. Unzip into a temporary folder. We only READ the files — never run them.
    temp_dir = tempfile.mkdtemp()
    try:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zip_file:
                safe_extract(zip_file, temp_dir)
        except zipfile.BadZipFile:
            raise HTTPException(400, "That file is not a valid zip.")

        # 3. Parse the Python files and build the graph.
        extracted = extract_project(find_project_root(temp_dir))
    finally:
        # The code is copied into each node, so the files aren't needed anymore.
        shutil.rmtree(temp_dir, ignore_errors=True)

    graph = build_graph(extracted)
    project_id = uuid.uuid4().hex[:8]
    result = graph_to_json(graph, extracted, project_id)

    # 4. Remember it so /impact and /explain can use it later.
    PROJECTS[project_id] = {
        "graph": graph,
        "nodes": {node["id"]: node for node in result["nodes"]},
    }
    return result


# The request body for /impact. IDs go in the JSON body (not the URL)
# because they contain "::" and "/".
class NodeRequest(BaseModel):
    project_id: str
    node_id: str


@app.post("/impact")
def impact(request: NodeRequest):
    project = PROJECTS.get(request.project_id)
    if project is None:
        raise HTTPException(404, "Project not found. Upload a .zip first.")
    if request.node_id not in project["graph"]:
        raise HTTPException(404, f"Function not found: {request.node_id}")
    return get_impact(project["graph"], request.node_id)
