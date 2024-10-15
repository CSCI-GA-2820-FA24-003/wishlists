######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestWishlist API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Wishlist
from .factories import WishlistFactory
from datetime import datetime

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_wishlist(self):
        """It should Create a new Wishlist"""
        test_wishlist = WishlistFactory()
        logging.debug("Test Wishlist: %s", test_wishlist.serialize())
        response = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = response.get_json()
        updated_time_from_response = datetime.strptime(
            new_wishlist["updated_time"], "%a, %d %b %Y %H:%M:%S GMT"
        )
        self.assertEqual(new_wishlist["id"], test_wishlist.id)
        self.assertEqual(new_wishlist["name"], test_wishlist.name)
        self.assertEqual(new_wishlist["product_id"], test_wishlist.product_id)
        self.assertEqual(new_wishlist["product_name"], test_wishlist.product_name)
        self.assertEqual(new_wishlist["quantity"], test_wishlist.quantity)
        self.assertEqual(
            updated_time_from_response.replace(microsecond=0),
            test_wishlist.updated_time.replace(microsecond=0),
        )
        self.assertEqual(new_wishlist["note"], test_wishlist.note)
        # Todo: Uncomment this code when get_wishlists is implemented
        # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_wishlist = response.get_json()
        # self.assertEqual(new_wishlist["name"], test_wishlist.name)
        # self.assertEqual(new_wishlist["id"], test_wishlist.id)
        # self.assertEqual(new_wishlist["product_id"], test_wishlist.product_id)
        # self.assertEqual(new_wishlist["product_name"], test_wishlist.product_name)
        # self.assertEqual(new_wishlist["quantity"], test_wishlist.quantity)
        # self.assertEqual(new_wishlist["updated_time"], test_wishlist.updated_time)
        # self.assertEqual(new_wishlist["note"], test_wishlist.note)


def test_delete_item(self):
    """It should Delete an Item via API"""
    wishlist = self._create_wishlists(1)[0]
    item = ItemsFactory()
    response = self.client.post(
        f"{BASE_URL}/{wishlist.id}/items",
        json=item.serialize(),
        content_type="application/json",
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    item_id = response.get_json()["id"]

    # delete the item and confirm the deletion
    delete_resp = self.client.delete(f"{BASE_URL}/{wishlist.id}/items/{item_id}")
    self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)

    get_resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items/{item_id}")
    self.assertEqual(get_resp.status_code, status.HTTP_404_NOT_FOUND)
