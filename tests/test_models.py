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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Wishlist, db
from .factories import WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Wishlist   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(TestCase):
    """Test Cases for Wishlist Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_wishlist(self):
        """It should create a Wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        found = Wishlist.all()
        self.assertEqual(len(found), 1)
        data = Wishlist.find(wishlist.id)
        self.assertEqual(data.name, wishlist.name)
        self.assertEqual(data.product_id, wishlist.product_id)
        self.assertEqual(data.product_name, wishlist.product_name)
        self.assertEqual(data.quantity, wishlist.quantity)
        self.assertEqual(data.updated_time, wishlist.updated_time)
        self.assertEqual(data.note, wishlist.note)

    def test_delete_wishlist_item(self):
        """It should Delete an item from a Wishlist"""
        wishlist = WishlistFactory()
        item = ItemsFactory(wishlist=wishlist)
        wishlist.items.append(item)
        wishlist.create()

        # Confirmation that the item exists in the wish list
        self.assertIsNotNone(wishlist.id)
        self.assertEqual(len(wishlist.items), 1)
        self.assertEqual(wishlist.items[0].id, item.id)

        # Delete items and update the wishlist
        item.delete()
        wishlist.update()

        # Retrieve the wish list from the database and confirm that the item has been deleted
        updated_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(updated_wishlist.items), 0)
        self.assertIsNone(Item.find(item.id))
