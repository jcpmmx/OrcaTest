# coding=utf-8


import os

from flask import current_app
from flask_restful import fields, reqparse, Api, Resource, abort, marshal_with
from flask_restful import inputs

from app.models import TODOItem, TODOList
from config import Env


class TODOItemsEndpoint(Resource):
    """
    API endpoint to manage TODO items.
    """
    default_todolist = None
    request_parser = None

    _RESPONSE_FIELDS = {
        'id': fields.Integer,
        'name': fields.String,
        'completed': fields.Boolean,
        'created': fields.DateTime('iso8601'),
        'modified': fields.DateTime('iso8601'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_todolist = TODOList.get_default_todolist()

    @marshal_with(_RESPONSE_FIELDS)
    def get(self, todoitem_id=None):
        # Getting a particular TODO item
        if todoitem_id:
            return TODOItem.query.filter_by(id=todoitem_id).first()
        # Getting them all
        return TODOItem.get_all(todolist_id=self.default_todolist.id)

    @marshal_with(_RESPONSE_FIELDS)
    def post(self):
        self._set_request_parser()
        request_data = self.request_parser.parse_args()
        self._verify_data(request_data)

        new_todoitem = TODOItem(**request_data)
        new_todoitem.save()
        return new_todoitem, 201

    @marshal_with(_RESPONSE_FIELDS)
    def put(self, todoitem_id=None):
        existing_todoitem = self._get_todoitem_or_abort(todoitem_id)
        self._set_request_parser(name_required=False)
        request_data = self.request_parser.parse_args()
        self._verify_data(request_data)

        existing_todoitem.update(**request_data)
        existing_todoitem.save()
        return existing_todoitem, 200

    @marshal_with(_RESPONSE_FIELDS)
    def delete(self, todoitem_id=None):
        existing_todoitem = self._get_todoitem_or_abort(todoitem_id)
        existing_todoitem.delete()
        return {}, 204

    def _set_request_parser(self, name_required=True):
        """
        Establishes the params expected by this endpoint on HTTP POST and PUT methods.
        """
        self.request_parser = reqparse.RequestParser(bundle_errors=True)
        self.request_parser.add_argument('name', type=str, required=name_required, help='What do you have to do?')
        self.request_parser.add_argument('completed', type=inputs.boolean, help='Did you do it?')

    def _verify_data(self, data):
        """
        Verifies if the request data is OK. If not, aborts with HTTP 400.
        """
        # This is just a sample data check
        if isinstance(data.get('name'), str) and len(data['name']) < 3:
            abort(400, message={'name': 'You must add a name of at least 3 chars'})
        # Adding default data
        data['todolist_id'] = self.default_todolist.id

    def _get_todoitem_or_abort(self, todoitem_id):
        """
        Verifies if the given TODO item exists. If not, aborts with HTTP 404.
        """
        if not todoitem_id:
            abort(404, message='You must provide a valid ID')
        existing_todoitem = TODOItem.query.filter_by(id=todoitem_id).first()
        if not existing_todoitem:
            abort(404, message='The requested TODO item does not exist')
        return existing_todoitem


def configure_api(app):
    """
    Attaches an API to the given Flask app.
    """
    api = Api(app)
    api.add_resource(TODOItemsEndpoint, '/api/todoitem', '/api/todoitem/<int:todoitem_id>')
