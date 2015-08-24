from flask import Blueprint
from flask.ext.login import current_user
from apikit import obj_or_404, request_data, jsonify

from aleph.model import User
from aleph.core import db
from aleph import authz


blueprint = Blueprint('users', __name__)


@blueprint.route('/api/1/users', methods=['GET'])
def index():
    authz.require(authz.is_admin())
    users = []
    for user in User.all():
        data = user.to_dict()
        del data['email']
        users.append(data)
    return jsonify({'results': users, 'total': len(users)})


@blueprint.route('/api/1/users/<int:id>', methods=['GET'])
def view(id):
    authz.require(id == current_user.id or authz.is_admin())
    user = obj_or_404(User.by_id(id))
    data = user.to_dict()
    if user.id != current_user.id:
        del data['email']
    return jsonify(data)


@blueprint.route('/api/1/users/<int:id>', methods=['POST', 'PUT'])
def update(id):
    user = obj_or_404(User.by_id(id))
    authz.require(user.id == current_user.id or authz.is_admin())
    user.update(request_data())
    db.session.add(user)
    db.session.commit()
    return jsonify(user)
