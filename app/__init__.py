# coding=utf-8


from flask import abort, jsonify, request
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

from config import Env, configure_app

db = SQLAlchemy()


def create_app(config_name):
    app = FlaskAPI(__name__)
    configure_app(app, config_name)
    db.init_app(app)

    from app.models import TODOItem  # To avoid circular imports

    @app.route('/api/todoitems/', methods=['POST', 'GET'])
    def todoitems():
        default_todolist = _get_default_todolist(app)

        if request.method == 'POST':
            # Creating a new TODO item
            name = request.data.get('name')
            if name:
                todoitem = TODOItem(name=name, todolist_id=default_todolist.id)
                todoitem.save()
                return jsonify(todoitem.to_dict()), 201

        else:
            # Retrieving all TODO items
            results = [todoitem.to_dict() for todoitem in TODOItem.get_all(todolist_id=default_todolist.id)]
            return jsonify(results), 200

    @app.route('/api/todoitems/<int:todoitem_id>/', methods=['GET', 'PUT', 'DELETE'])
    def todoitems_detail(todoitem_id):
        todoitem = TODOItem.query.filter_by(id=todoitem_id).one_or_none()
        if not todoitem:
            abort(404)

        if request.method == 'DELETE':
            # Deleting a TODO item
            todoitem.delete()
            return '', 204

        elif request.method == 'PUT':
            # Editing an existing TODO item
            name = request.data.get('name')
            if name:
                todoitem.name = name
                todoitem.save()

        return jsonify(todoitem.to_dict()), 200

    return app


def _get_default_todolist(app):
    # Since this is v1, we're using a default TODO list for all TODO items
    from app.models import TODOList  # To avoid circular imports

    default_todolist_filters = {'name': app.config['DEFAULT_TODO_LIST_NAME']}
    default_todolist = TODOList.query.filter_by(**default_todolist_filters).one_or_none()
    if not default_todolist:
        default_todolist = TODOList(**default_todolist_filters)
        default_todolist.save()

    return default_todolist
