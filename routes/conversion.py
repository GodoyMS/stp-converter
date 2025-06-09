import os
import traceback
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from services import ConversionService, SupabaseService

router = APIRouter()

@router.post("/convert")
async def convert(file: UploadFile = File(...)):
    try:
        # Convert STEP to GLB
        conversion_result = ConversionService.convert_step_to_glb(file)
        
        # Upload to Supabase
        glb_url = SupabaseService.upload_glb(
            conversion_result["glb_path"], 
            conversion_result["glb_name"]
        )
        
        # Calculate file size
        size_mb = round(os.path.getsize(conversion_result["glb_path"]) / (1024 * 1024), 2)
        
        # Save metadata to database
        result = SupabaseService.save_file_metadata(
            glb_url,
            size_mb,
            conversion_result["original_filename"],
            conversion_result["glb_name"]
        )
        
        return result

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500, 
            content={"error": f"Conversion failed: {str(e)}"}
        )