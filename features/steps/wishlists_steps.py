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
Pet Steps

Steps file for Pet.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following wishlists")
def step_impl(context):
    """Delete all Wishlists and load new ones"""

    # Get a list all of the wishlists
    rest_endpoint = f"{context.base_url}/wishlists"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for wishlist in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{wishlist['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new wishlists
    for row in context.table:
        payload = {
            "customer_name": row["customer_name"],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given("the following items")
def step_impl(context):
    """Delete all Items and load new ones"""
    rest_endpoint = f"{context.base_url}/wishlists"
    # all items were already deleted when wishlists were deleted

    # load the database with new items, connected back to wishlists
    for row in context.table:

        context.resp = requests.get(
            rest_endpoint,
            params={"customer-name": row["customer_name"]},
            timeout=WAIT_TIMEOUT,
        )
        expect(context.resp.status_code).equal_to(HTTP_200_OK)
        expect(len(context.resp.json())).equal_to(1)
        wishlist_id = int(context.resp.json()[0]["id"])

    # load the database with new wishlists
    for row in context.table:
        payload = {
            "wishlist_id": wishlist_id,
            "name": row["name"],
            "category": row["category"],
            "quantity": int(row["quantity"]),
            "note": row["note"],
            "price": float(row["price"]),
            "is_favorite": row["is_favorite"] in ["True", "true", "1"],
        }
        context.resp = requests.post(
            f"{rest_endpoint}/{wishlist_id}/items", json=payload, timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
