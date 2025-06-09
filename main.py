from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config import CONVERTED_DIR, setup_directories
from routes import conversion, files
import uvicorn

# Setup directories
setup_directories()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversion.router)
app.include_router(files.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# import os, uuid, shutil, traceback
# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# import cadquery as cq
# import trimesh
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi import HTTPException
# from fastapi import Path

# import requests
# from dotenv import load_dotenv

# # Load Supabase env
# load_dotenv()
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins
#     allow_credentials=False,  # Must be False when allow_origins=["*"]
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# UPLOAD_DIR = "uploads"
# CONVERTED_DIR = "converted"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(CONVERTED_DIR, exist_ok=True)

# app.mount("/files", StaticFiles(directory=CONVERTED_DIR), name="files")

# @app.post("/convert")
# async def convert(file: UploadFile = File(...)):
#     orig_name = file.filename
#     uid = uuid.uuid4().hex
#     stp_path = os.path.join(UPLOAD_DIR, f"{uid}.step")
#     stl_path = os.path.join(CONVERTED_DIR, f"{uid}.stl")
#     glb_name = f"{uid}.glb"
#     glb_path = os.path.join(CONVERTED_DIR, glb_name)

#     # Save uploaded STEP file
#     with open(stp_path, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     try:
#         # Convert STEP → STL → GLB
#         cq_obj = cq.importers.importStep(stp_path)
#         cq.exporters.export(cq_obj, stl_path)
#         mesh = trimesh.load_mesh(stl_path)
#         scene = trimesh.Scene(mesh)
#         glb_bytes = trimesh.exchange.gltf.export_glb(scene)

#         with open(glb_path, "wb") as f:
#             f.write(glb_bytes)

#         # Upload GLB to Supabase Storage
#         with open(glb_path, "rb") as f:
#             upload_resp = requests.post(
#                 f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{glb_name}",
#                 headers={
#                     "Authorization": f"Bearer {SUPABASE_KEY}",
#                     "Content-Type": "application/octet-stream"
#                 },
#                 data=f
#             )

#         if upload_resp.status_code not in (200, 201):
#             print(traceback.format_exc())

#             return JSONResponse(
#                 status_code=500,
#                 content={"error": "Supabase upload failed", "details": upload_resp.text}
#             )

#         # Construct public URL (assuming the bucket is public)
#         glb_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{glb_name}"
#         size_mb = round(os.path.getsize(glb_path) / (1024 * 1024), 2)

#         # Insert metadata into Supabase `glb_files` table
#         db_payload = {
#             "glb_url": glb_url,
#             "size_mb": size_mb,
#             "original_filename": orig_name,
#             "converted_filename": glb_name,
#             "error_message": None
#         }

#         db_resp = requests.post(
#             f"{SUPABASE_URL}/rest/v1/glb_files",
#             headers={
#                 "apikey": SUPABASE_KEY,
#                 "Authorization": f"Bearer {SUPABASE_KEY}",
#                 "Content-Type": "application/json",
#                 "Prefer": "return=representation"
#             },
#             json=db_payload
#         )

#         if db_resp.status_code not in (200, 201):
#             print(traceback.format_exc())

#             return JSONResponse(
#                 status_code=500,
#                 content={"error": "Supabase DB insert failed", "details": db_resp.text}
#             )

#         return db_resp.json()[0]

#     except Exception as e:
#         print(traceback.format_exc())
#         return JSONResponse(status_code=500, content={"error": f"Conversion failed: {str(e)}"})


# @app.get("/glb-files")
# async def get_all_glb_files():
#     try:
#         response = requests.get(
#             f"{SUPABASE_URL}/rest/v1/glb_files",
#             headers={
#                 "apikey": SUPABASE_KEY,
#                 "Authorization": f"Bearer {SUPABASE_KEY}",
#                 "Accept": "application/json"
#             },
#         )

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail={"error": "Failed to fetch GLB files", "details": response.text}
#             )

#         return response.json()

#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail={"error": f"Internal server error: {str(e)}"})
    
    
# @app.delete("/glb-files/{file_id}")
# async def delete_glb_file(file_id: int = Path(..., description="The ID of the GLB file to delete")):
#     try:
#         response = requests.delete(
#             f"{SUPABASE_URL}/rest/v1/glb_files?id=eq.{file_id}",
#             headers={
#                 "apikey": SUPABASE_KEY,
#                 "Authorization": f"Bearer {SUPABASE_KEY}",
#                 "Prefer": "return=representation"
#             }
#         )

#         if response.status_code not in (200, 204):
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail={"error": "Failed to delete GLB file", "details": response.text}
#             )

#         return {"message": f"File with id {file_id} deleted successfully."}

#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail={"error": f"Internal server error: {str(e)}"})