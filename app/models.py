# coding=utf-8


from flask import current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TODOList(db.Model):
    """
    Class that represents a TODO list.
    
    This is in case we want to potentially manage multiple lists instead of a master list.
    """
    __tablename__ = 'todolists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    todoitems = db.relationship('TODOItem', lazy=True, backref=db.backref('todolists', lazy='joined'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<TODOList: {}>'.format(self.name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_default_todolist(cls):
        # For simplicity, we're using a default TODO list for all TODO items
        return cls.query.filter_by(name=current_app.config['DEFAULT_TODO_LIST_NAME']).first()


class TODOItem(db.Model):
    """
    Class that represents a single item of a TODO list.
    
    Each TODO item belongs to a TODO list.
    """
    __tablename__ = 'todoitems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, name, todolist_id, completed=False):
        self.name = name
        self.todolist_id = todolist_id
        self.completed = completed

    def __repr__(self):
        return '<TODOItem: {}>'.format(self.name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **data):
        changed = False
        data.pop('id', None)  # Avoiding PK changes
        for attr_name, new_value in data.items():
            current_value = getattr(self, attr_name, None)
            if new_value and new_value != current_value:  # Caveat: 'Noney' values can't be set right now
                setattr(self, attr_name, new_value)
                changed = True
        if changed:
            self.save()

    @classmethod
    def get_all(cls, todolist_id):
        return cls.query.filter_by(todolist_id=todolist_id).order_by(cls.created.desc()).all()
