from db import SessionLocal
from models import AccessToken

db = SessionLocal()
db.query(AccessToken).delete()

db.commit()
db.close()
