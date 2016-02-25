from aleph.contrib.openoil import alerts
from aleph.model import Alert, User
from aleph.core import db
import datetime

def get_test_user():
    return db.session.query(User).first()

def test_db_alert_dates():
    al = Alert(query = 'test data',
               user = get_test_user(),
               label = 'test query',
               checking_interval = 5)

    db.session.add(al)
    db.session.commit()
    assert al.due_to_check()

    al.mark_as_checked()
    db.session.add(al)
    db.session.commit()
    assert not al.due_to_check()

    al.checked_at = datetime.datetime.utcnow() - datetime.timedelta(days=6)
    db.session.add(al)
    db.session.commit()
    assert al.due_to_check()
    
    al.checked_at = datetime.datetime.utcnow() - datetime.timedelta(days=4)
    db.session.add(al)
    db.session.commit()
    assert not al.due_to_check()    

    db.session.delete(al)
    db.session.commit()

    
