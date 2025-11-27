# uploader.py
from database import SessionLocal, CourseUpload
from logs import logger

def create_upload(uploader_id, title, description, url, image=None):
    db = SessionLocal()
    cu = CourseUpload(
        uploader_id=uploader_id,
        title=title,
        description=description,
        url=url,
        image=image,
        approved=False
    )
    db.add(cu)
    db.commit()
    db.close()
    logger.info("Upload created by %s: %s", uploader_id, title)
    return cu