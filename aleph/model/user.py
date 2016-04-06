import logging
from datetime import datetime

from aleph.core import db, login_manager, url_for
from aleph.model.util import make_token
from aleph.model.forms import UserForm

log = logging.getLogger(__name__)

from flask_user import UserMixin
from flask_user.forms import RegisterForm
from flask_wtf import Form
from wtforms import StringField, SubmitField, validators


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#
# Much code adapted from
# https://github.com/lingthio/Flask-User-starter-app/blob/master/app/core/models.py
# 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode,
                      #following attributes are for flask-user
                      nullable=False,
                      unique=True)
    display_name = db.Column(db.Unicode, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    # Aleph-specific columns
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    twitter_id = db.Column(db.Unicode)
    facebook_id = db.Column(db.Unicode)

    api_key = db.Column(db.Unicode, default=make_token)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)


    # Columns required for flask-user

    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    # 'active' already defined above
    # omitting first and last name

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('user', lazy='dynamic'))


    
    def is_active(self):
        return self.active

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User(%r,%r)>' % (self.id, self.email)

    def __unicode__(self):
        return self.display_name

    def to_dict(self):
        return {
            'id': self.id,
            'api_url': url_for('users.view', id=self.id),
            'email': self.email,
            'display_name': self.display_name
        }

    def update(self, data):
        data = UserForm().deserialize(data)
        self.display_name = data.get('display_name')
        self.email = data.get('email')

    @classmethod
    def load(cls, data):
        user = None
        if 'twitter_id' in data:
            user = cls.by_twitter_id(data.get('twitter_id'))
        elif 'facebook_id' in data:
            user = cls.by_facebook_id(data.get('facebook_id'))
        if user is None:
            user = cls()

        user.twitter_id = data.get('twitter_id')
        user.facebook_id = data.get('facebook_id')
        if not user.display_name:
            user.display_name = data.get('display_name')
        if not user.email:
            user.email = data.get('email')
        db.session.add(user)
        return user

    @classmethod
    def all(cls):
        q = db.session.query(cls).filter_by(active=True)
        return q

    @classmethod
    def by_id(cls, id):
        q = db.session.query(cls).filter_by(id=int(id))
        return q.first()

    @classmethod
    def by_api_key(cls, api_key):
        q = db.session.query(cls).filter_by(api_key=api_key)
        return q.first()

    @classmethod
    def by_twitter_id(cls, twitter_id):
        q = db.session.query(cls).filter_by(twitter_id=str(twitter_id))
        return q.first()

    @classmethod
    def by_facebook_id(cls, facebook_id):
        q = db.session.query(cls).filter_by(facebook_id=str(facebook_id))
        return q.first()


# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes

# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])


# Define the User profile form
class UserProfileForm(Form):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')
