# coding=utf-8


from app import db


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

    @staticmethod
    def get_all():
        return TODOList.query.all()


class TODOItem(db.Model):
    """
    Class that represents a single item of a TODO list.
    
    Each TODO item belongs to a TODO list.
    """
    __tablename__ = 'todoitems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, name, todolist_id):
        self.name = name
        self.todolist_id = todolist_id

    def __repr__(self):
        return '<TODOItem: {}>'.format(self.name)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'todolist_id': self.todolist_id,
        }

    @staticmethod
    def get_all(todolist_id):
        return TODOItem.query.filter_by(todolist_id=todolist_id)
