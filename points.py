# points.py
from database import SessionLocal, User, PointTransaction
from logs import logger

def get_or_create_user(user_id, username=None):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username=username, points=10)  # welcome 10 pts
        db.add(user)
        db.commit()
    db.expunge_all()
    db.close()
    return user

def add_points(user_id, amount, reason=""):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, points=0)
        db.add(user)
        db.commit()
    user.points = (user.points or 0) + int(amount)
    txn = PointTransaction(user_id=user_id, amount=int(amount), reason=reason)
    db.add(txn)
    db.commit()
    db.close()
    logger.info("Added %s pts to %s for %s", amount, user_id, reason)
    return True

def deduct_points(user_id, amount, reason=""):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user or (user.points or 0) < int(amount):
        db.close()
        return False
    user.points = (user.points or 0) - int(amount)
    txn = PointTransaction(user_id=user_id, amount=-int(amount), reason=reason)
    db.add(txn)
    db.commit()
    db.close()
    logger.info("Deducted %s pts from %s for %s", amount, user_id, reason)
    return True

def get_points(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    pts = user.points if user else 0
    db.close()
    return pts