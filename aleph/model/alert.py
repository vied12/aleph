from aleph.core import db
from aleph.model.user import User
from datetime import datetime, timedelta

class Alert(db.Model):
    '''
    Also consider adding:
    - active/inactive
    - label (short human-readable text)
    '''
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship(User, backref=db.backref('alerts'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_at = db.Column(db.DateTime, default=None,
                           )
    query = db.Column(db.Unicode)
    label = db.Column(db.Unicode)
    checking_interval = db.Column(db.Integer, default=None)
    # number of days between checks. None == 'never check'

    def due_to_check(self):
        '''
        Return True if it is time to run this query
        
        NB We expect this script to run at nearly-but-not-precisely
        the same time each day, and we want to run at an intuitive
        'once per day', rather than skipping because today's run
        has happened a few seconds earlier.
        Therefore we allow 2 hours of wiggle room
        [we aren't worried about sending duplicate alerts, because that
        will be handled precisely by filtering result insert dates against
        the checked_at field
        '''
        if self.checking_interval == None: # query is disabled
            return False
        if self.checked_at == None: # query is being run for the first time
            return True
        min_check_date = datetime.utcnow() - timedelta(days=self.checking_interval) + timedelta(hours=2)
        return self.checked_at <= min_check_date

    def mark_as_checked(self):
        self.checked_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        attrs = ('id', 'label', 'query', 'checking_interval', 'user_id', 'created_at', 'checked_at')
        return {attr: getattr(self, attr) for attr in attrs}
        
    @classmethod
    def by_id(cls, id, role=None):
        q = db.session.query(cls).filter_by(id=id)
        if role is not None: #only applies if we are using authz roles
            q = q.filter(cls.role_id == role.id)
        return q.first()

