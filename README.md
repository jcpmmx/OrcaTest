# TODO - Flask backend
> Originally developed as a take-home test project for Orca.

### System requirements
- Python (v3.6.5)
- PostgreSQL (v10.5)

### Built and tested with
- Python (v3.6.5)
- Flask (v1.0.2)
- Flask-RESTful (v0.3.6)
- requests (v2.20)
- PostgreSQL (v10.5) + psycopg2 (v2.7.6.1)
- SQLAlchemy (v1.2.14) + Flask-SQLAlchemy (v2.3.2)
- gunicorn (v19.9) (Heroku only)

### How to run this locally
1. Clone this repo
2. Install all Python libraries (ideally inside a `virtualenv`): `pip install -r requirements.txt` 
3. Create 2 new PostgreSQL databases: `createdb orca` and `createdb orca_test` (for test cases)
4. Run `python manage.py db init` and `python manage.py db upgrade` to set your DB instance
5. Run `python run.py` to run Flask's development server and go to `http://localhost:5000`
6. Run `python tests.py` to run test cases

---

### About this solution

This Flask application contains 2 SQLAlchemy models:  
- `TODOList`: represents a collection of related TODO items (e.g. "Groceries" or "NY trip"). Internally, the app comes with only one master TODO list, and lists are not available via API.
- `TODOItem`: a single thing to do  (e.g. "Buy tomatoes" or "Choose museums to visit"). Items have one of 2 possible statuses: completed or not (default value). All items are associated to the master TODO list.

The app also provides 1 API endpoints to interact with TODO items.
This endpoint is RESTful and works with JSON by default.

1. `GET /api/todoitems`: returns a list of all TODO items, sorted by last modified items first.  
e.g.  
```
Request: HTTP GET

Response: HTTP/1.0 200 OK
[
    {
        "completed": false,
        "created": "2018-12-02T14:21:58.199851",
        "id": 1,
        "modified": "2018-12-02T14:21:58.199851",
        "name": "Add a great README to the repo"
    },
    ...
]
```

2. `POST /api/todoitems`: creates a new item.  
e.g.  
```
Request: HTTP POST
{
    "name": "Get hired by a great company"
}

Response: HTTP/1.0 201 CREATED
{
    "completed": false,
    "created": "2018-12-02T14:27:58.199851",
    "id": 2,
    "modified": "2018-12-02T14:27:58.199851",
    "name": "Get hired by a great company"
}
```
e.g. Response for an empty POST request  
```
Request: HTTP POST
{}

HTTP/1.0 400 BAD REQUEST
{
    "message": {
        "name": "You must add a name of at least 3 chars"
    }
}
```

3. `PUT /api/todoitems/<id>`: modifies a given item.  
With it, we can toggle the status of an item (e.g. completed --> undo).
e.g.  
```
Request: HTTP PUT /api/todoitems/2
{
    "completed": true
}

Response: HTTP/1.0 201 CREATED
{
    "completed": true,
    "created": "2018-12-02T14:27:58.199851",
    "id": 2,
    "modified": "2018-12-02T14:33:58.199851",
    "name": "Get hired by a great company"
}
```

4. `DELETE /api/todoitems/<id>`: deletes a given item.  
e.g.  
```
Request: HTTP DELETE /api/todoitems/2

Response: HTTP/1.0 204 NO CONTENT
```

### Limitations
- As mentioned before, the app only comes with support for a master TODO list

### Nice to haves
- Add Flask-API support so our API is browsable
- Add API docs (e.g. Swagger)
- Add TODO lists as API resources so we can manage multiple lists
