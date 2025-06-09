import traceback
from fastapi import APIRouter, HTTPException, Path
from services import SupabaseService

router = APIRouter()

@router.get("/glb-files")
async def get_all_glb_files():
    try:
        return SupabaseService.get_all_files()
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Internal server error: {str(e)}"}
        ) from e

@router.delete("/glb-files/{file_id}")
async def delete_glb_file(file_id: int = Path(..., description="The ID of the GLB file to delete")):
    try:
        return SupabaseService.delete_file(file_id)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Internal server error: {str(e)}"}
        ) from e