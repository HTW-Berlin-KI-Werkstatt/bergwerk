from datetime import datetime
from data import db as data_db

def track_text(uid, role, text, buttons, language):
    ts = datetime.now().timestamp()
    if uid != "cron":
        data_db.track_text(uid, role, text, buttons, language, ts)
    