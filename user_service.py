# user_service.py
from database import SessionLocal, User
from logs import logger
import json
from points import add_points

def register_user(user_id, username=None, invited_by=None):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username=username, points=10, invited_by=invited_by)
        db.add(user)
        db.commit()
        logger.info("Registered user %s", user_id)
        # if invited_by is set, add invite points to referrer
        if invited_by:
            ref = db.query(User).filter(User.id == invited_by).first()
            if ref:
                ref.invited_count = (ref.invited_count or 0) + 1
                ref.points = (ref.points or 0) + 2
                db.commit()
    db.close()
    return True

def add_favorite(user_id, course):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, points=10)
        db.add(user)
        db.commit()
    favs = user.favorites or []
    # prevent duplicate by link
    existing_links = {f.get("link") for f in favs if f.get("link")}
    if course.get("link") not in existing_links:
        favs.append(course)
        user.favorites = favs
        db.commit()
        logger.info("User %s added favorite", user_id)
        db.close()
        return True
    db.close()
    return False

def get_favorites(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    favs = user.favorites or []
    db.close()
    return favs