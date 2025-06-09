import os
import uuid
import shutil
import traceback
import requests
import cadquery as cq
import trimesh
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, UPLOAD_DIR, CONVERTED_DIR

class ConversionService:
    @staticmethod
    def convert_step_to_glb(file):
        """Convert STEP file to GLB format"""
        orig_name = file.filename
        uid = uuid.uuid4().hex
        stp_path = os.path.join(UPLOAD_DIR, f"{uid}.step")
        stl_path = os.path.join(CONVERTED_DIR, f"{uid}.stl")
        glb_name = f"{uid}.glb"
        glb_path = os.path.join(CONVERTED_DIR, glb_name)

        # Save uploaded STEP file
        with open(stp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Convert STEP → STL → GLB
        cq_obj = cq.importers.importStep(stp_path)
        cq.exporters.export(cq_obj, stl_path)
        mesh = trimesh.load_mesh(stl_path)
        scene = trimesh.Scene(mesh)
        glb_bytes = trimesh.exchange.gltf.export_glb(scene)

        with open(glb_path, "wb") as f:
            f.write(glb_bytes)

        return {
            "original_filename": orig_name,
            "glb_name": glb_name,
            "glb_path": glb_path
        }

class SupabaseService:
    @staticmethod
    def upload_glb(glb_path, glb_name):
        """Upload GLB file to Supabase Storage"""
        with open(glb_path, "rb") as f:
            upload_resp = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{glb_name}",
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/octet-stream"
                },
                data=f
            )
        
        if upload_resp.status_code not in (200, 201):
            raise Exception(f"Supabase upload failed: {upload_resp.text}")
        
        return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{glb_name}"

    @staticmethod
    def save_file_metadata(glb_url, size_mb, original_filename, glb_name):
        """Save file metadata to Supabase database"""
        db_payload = {
            "glb_url": glb_url,
            "size_mb": size_mb,
            "original_filename": original_filename,
            "converted_filename": glb_name,
            "error_message": None
        }

        db_resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/glb_files",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=db_payload
        )

        if db_resp.status_code not in (200, 201):
            raise Exception(f"Supabase DB insert failed: {db_resp.text}")

        return db_resp.json()[0]

    @staticmethod
    def get_all_files():
        """Get all GLB files from database"""
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/glb_files",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Accept": "application/json"
            },
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch GLB files: {response.text}")

        return response.json()

    @staticmethod
    def delete_file(file_id):
        """Delete GLB file from database"""
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/glb_files?id=eq.{file_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "return=representation"
            }
        )

        if response.status_code not in (200, 204):
            raise Exception(f"Failed to delete GLB file: {response.text}")

        return {"message": f"File with id {file_id} deleted successfully."}