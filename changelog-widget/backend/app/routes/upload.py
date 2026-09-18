"""
routes/upload.py
----------------
Admin-only endpoint for uploading images (cover images, inline screenshots).
Validates MIME type, file size, generates unique filename, and saves to upload_dir.
"""

import os
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.config.settings import settings
from app.middleware.auth import get_current_admin_user
from app.models.user import UserModel

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_FILE_SIZE = settings.max_upload_size_mb if hasattr(settings, "max_upload_size_mb") else 5
MAX_FILE_BYTES = MAX_FILE_SIZE * 1024 * 1024


class UploadResponse(BaseModel):
    url: str
    filename: str
    size_bytes: int
    content_type: str


@router.post(
    "/image",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image (Admin only)",
    description="Uploads an image file (JPEG, PNG, WebP, GIF up to 5MB) for changelog cover or content.",
)
async def upload_image(
    file: UploadFile = File(...),
    admin_user: UserModel = Depends(get_current_admin_user),
):
    # 1. Validate MIME type
    content_type = file.content_type
    if not content_type or content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{content_type}'. Allowed types: JPEG, PNG, WebP, GIF.",
        )

    # 2. Read contents and validate size
    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if file_size > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE") else 413,
            detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE}MB.",
        )

    # 3. Secure unique filename
    ext = ALLOWED_MIME_TYPES[content_type.lower()]
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    upload_dir = getattr(settings, "upload_dir", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    destination_path = os.path.join(upload_dir, unique_filename)

    # 4. Save file to disk
    with open(destination_path, "wb") as f:
        f.write(contents)

    # 5. Build relative URL (safe for both dev & prod reverse proxies)
    url = f"/static/uploads/{unique_filename}"

    return UploadResponse(
        url=url,
        filename=unique_filename,
        size_bytes=file_size,
        content_type=content_type,
    )
