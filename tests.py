# coding=utf-8


import json
import os
import random
import unittest

from app import create_app
from app.models import db
from config import Env, load_initial_db_data


class TODOItemsEndpointTestCase(unittest.TestCase):
    """
    Test cases for the TODO Items API endpoint.
    """

    def setUp(self):
        self.app = create_app(Env.TESTING)
        self.client = self.app.test_client()
        self.todoitems_endpoint = '/api/todoitems'
        self.todoitems_detail_endpoint = '/api/todoitems/{todoitem_id}'
        with self.app.app_context():
            db.create_all()
            load_initial_db_data(self.app, db)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_http_methods(self):
        # Testing allowed methods
        self.assertEqual(self.client.get(self.todoitems_endpoint).status_code, 200)
        self.assertEqual(self.client.post(self.todoitems_endpoint).status_code, 400)  # OK: no data provided
        self.assertEqual(self.client.put(self.todoitems_endpoint).status_code, 404)  # OK: no ID provided
        self.assertEqual(self.client.delete(self.todoitems_endpoint).status_code, 404)  # OK: no ID provided
        # Testing unallowed methods
        self.assertEqual(self.client.patch(self.todoitems_endpoint).status_code, 405)

    def test_create(self):
        # Testing happy path
        request_data = {'name': "Do Orca's take-home project!"}
        response = self.client.post(self.todoitems_endpoint, json=request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn('name', response_json)
        self.assertIn(request_data['name'], response_json['name'])
        self.assertTrue(len(response_json))
        (self.assertIn(x, response_json) for x in ('id', 'name', 'completed', 'created', 'modified'))

        # Testing different combinations of bad input data
        malformed_request_data_1 = {}  # Empty data
        malformed_request_data_2 = {'name': 'XX'}  # Short name
        response_with_error_1 = self.client.post(self.todoitems_endpoint, json=malformed_request_data_1)
        response_with_error_2 = self.client.post(self.todoitems_endpoint, json=malformed_request_data_2)
        self.assertEqual(response_with_error_1.status_code, 400)
        self.assertEqual(response_with_error_2.status_code, 400)
        self.assertIn('name', response_with_error_1.get_json()['message'])
        self.assertIn('at least 3 chars', response_with_error_2.get_json()['message']['name'])

    def test_retrieve(self):
        # Creating some TODO items first
        todoitems_amount = random.randint(2, 5)
        for idx in range(1, todoitems_amount+1):
            request_data = {'name': "Crushing Orca's take-home project #{}!".format(idx)}
            response = self.client.post(self.todoitems_endpoint, json=request_data)
            self.assertEqual(response.status_code, 201)

        # Testing that TODO items were in fact created
        response = self.client.get(self.todoitems_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), todoitems_amount)
        # Testing all details about the last TODO item returned by the previous API call
        last_id = response.get_json()[todoitems_amount-1]['id']
        response = self.client.get(self.todoitems_detail_endpoint.format(todoitem_id=last_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['id'], last_id)

    def test_update(self):
        # Creating a new TODO item
        name = 'Learn Flask!'
        request_data = {'name': name}
        response = self.client.post(self.todoitems_endpoint, json=request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn(name, response_json['name'])

        todoitem_url = self.todoitems_detail_endpoint.format(todoitem_id=response_json['id'])
        # Editing the status of the TODO item recently created
        self.assertFalse(response_json['completed'])
        new_request_data = {'completed': True}
        response = self.client.put(todoitem_url, json=new_request_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['completed'])
        # Editing the name of the TODO item recently created
        new_name = 'Learn ElectronJS as well!'
        new_request_data = {'name': new_name}
        response = self.client.put(todoitem_url, json=new_request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_name, response_json['name'])
        self.assertTrue(response_json['completed'])
        # Non-existing TODO items cannot be updated
        response = self.client.put(self.todoitems_detail_endpoint.format(todoitem_id='000'))
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        # Creating a new TODO item
        request_data = {'name': 'Join team Orca!'}
        response = self.client.post(self.todoitems_endpoint, json=request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn(request_data['name'], response_json['name'])

        todoitem_url = self.todoitems_detail_endpoint.format(todoitem_id=response_json['id'])
        # Deleting the TODO item recently created
        response = self.client.delete(todoitem_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(response.get_data(as_text=True))
        # And now it's gone
        response = self.client.delete(todoitem_url)
        self.assertEqual(response.status_code, 404)
        # Non-existing TODO items cannot be deleted
        response = self.client.delete(self.todoitems_detail_endpoint.format(todoitem_id='000'))
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
