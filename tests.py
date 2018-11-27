# coding=utf-8


import json
import os
import random
import unittest

from app import create_app, db
from config import Env


class TODOItemsTestCase(unittest.TestCase):
    """
    Test cases for the TODOItems model.
    """

    def setUp(self):
        self.app = create_app(config_name=Env.TESTING)
        self.client = self.app.test_client
        self.api_todoitems_endpoint = '/api/todoitems/'
        self.api_todoitems_detail_endpoint = '/api/todoitems/{todoitem_id}/'
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_api_todoitems_create(self):
        request_data = {'name': "Do Orca's take-home project!"}
        response = self.client().post(self.api_todoitems_endpoint, json=request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn('name', response_json)
        self.assertIn(request_data['name'], response_json['name'])

    def test_api_todoitems_retrieve(self):
        # Creating some TODO items first
        todoitems_amount = random.randint(2, 5)
        for idx in range(1, todoitems_amount+1):
            request_data = {'name': "Crushing Orca's take-home project #{}!".format(idx)}
            response = self.client().post(self.api_todoitems_endpoint, json=request_data)
            self.assertEqual(response.status_code, 201)

        # Checking that TODO items were in fact created
        response = self.client().get(self.api_todoitems_endpoint)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json), todoitems_amount)

        # Checking all details about the last TODO item returned by the previous API call
        last_id = response.get_json()[todoitems_amount-1]['id']
        response = self.client().get(self.api_todoitems_detail_endpoint.format(todoitem_id=last_id))
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['id'], last_id)

    def test_api_todoitems_update(self):
        # Creating a new TODO item
        name = 'Learn Flask!'
        request_data = {'name': name}
        response = self.client().post(self.api_todoitems_endpoint, json=request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn(name, response_json['name'])

        # Editing the TODO item recently created
        new_name = 'Learn ElectronJS as well!'
        request_data = {'name': new_name}
        response = self.client().put(
            self.api_todoitems_detail_endpoint.format(todoitem_id=response_json['id']), json=request_data
        )
        response_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_name, response_json['name'])

    def test_api_todoitems_delete(self):
        # Creating a new TODO item
        request_data = {'name': 'Join team Orca!'}
        response = self.client().post(self.api_todoitems_endpoint, json=request_data)
        response_json = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn(request_data['name'], response_json['name'])

        # Deleting the TODO item recently created
        todoitem_url = self.api_todoitems_detail_endpoint.format(todoitem_id=response_json['id'])
        response = self.client().delete(todoitem_url)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(response.get_json())

        # And now it's gone
        response = self.client().delete(todoitem_url)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()