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
Item Wishlist Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Wishlist from the inventory of wishlists in the WishlistShop

"""

from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application
from service.models import Wishlist, Items
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        """Wishlists REST API Service: The Wishlists service allows users to save items they are
            interested in but not yet ready to purchase. You can access details about wishlists
            (/wishlists) and items ((/wishlists/ { wishlist_id }/items)) within each wishlist.""",
        status.HTTP_200_OK,
    )
    # return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# List wishlist
# @app.route("/wishlists", methods=["GET"])
# def list_wishlists():


######################################################################
# CREATE A NEW Wishlist
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Create a Wishlist

    This endpoint will create a Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to Create a Wishlist...")
    check_content_type("application/json")

    wishlist = Wishlist()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    wishlist.deserialize(data)

    # Save the new Wishlist to the database
    wishlist.create()
    app.logger.info("Wishlist with new id [%s] saved!", wishlist.id)

    # Return the location of the new Wishlist
    # Todo: uncomment this code when get_wishlists is implemented
    # location_url = url_for("get_wishlists", wishlist_id=wishlist.id, _external=True)
    location_url = "unknown"
    return (
        jsonify(wishlist.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


# Delete wishlist

# Read wishlist
# @app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
# def get_wishlists(wishlist_id):


# Update wishlist
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlists(wishlist_id):
    """
    Update a Wishlist

    This endpoint will update a Wishlist based the body that is posted
    """
    app.logger.info("Request to Update a wishlist with id [%s]", wishlist_id)
    check_content_type("application/json")

    # Attempt to find the Wishlist and abort if not found
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    # Update the Wishlist with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    wishlist.deserialize(data)

    # Save the updates to the database
    wishlist.update()

    app.logger.info("Wishlist with ID: %d updated.", wishlist.id)
    return jsonify(wishlist.serialize()), status.HTTP_200_OK


# List an item in wishlist
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["GET"])
def get_items(wishlist_id, item_id):
    """
    Get an Item from a Wishlist

    This endpoint returns just an item
    """
    app.logger.info(
        "Request to retrieve Items %s for Wishlist id: %s", (item_id, wishlist_id)
    )

    # See if the item exists and abort if it doesn't
    item = Items.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{item_id}' could not be found.",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


# Create an item in wishlist
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def create_items(wishlist_id):
    """
    Create an Item on an Wishlist

    This endpoint will add an item to an wishlist
    """
    app.logger.info("Request to create an Item for Wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Create an item from the json data
    item = Items()
    item.deserialize(request.get_json())

    # Append the item to the wishlist
    wishlist.items.append(item)
    wishlist.update()

    # Prepare a message to return
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_items", wishlist_id=wishlist.id, item_id=item.id, _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


# Read an item in wishlist
# @app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["GET"])
# def get_items(wishlist_id, item_id):


# Update an item in wishlist
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["PUT"])
def update_item(wishlist_id, item_id):
    """
    Update an Item in a Wishlist

    This endpoint will update an Item based on the body that is posted
    """
    # Find the wishlist by ID
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(404, description=f"Wishlist with id '{wishlist_id}' was not found.")

    # Find the item by ID
    item = Items.find(item_id)
    if not item or item.wishlist_id != wishlist_id:
        abort(
            404,
            description=f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
        )

    # Get the request payload
    data = request.get_json()
    # Deserialize the data to update the item
    try:
        item.deserialize(data)  # Assuming deserialize properly updates the item fields
        item.update()  # Save the updated item to the database
    except Exception as e:
        abort(400, description=f"Error updating item: {str(e)}")

    # Return the updated item in the response
    return jsonify(item.serialize()), 200


# Delete an item in wishlist
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(wishlist_id, item_id):
    """
    Delete an Item from a Wishlist
    """
    app.logger.info("Deleting Item %s from Wishlist %s", item_id, wishlist_id)

    item = Items.find(item_id)
    if item:
        item.delete()
        app.logger.info("Item %s deleted successfully", item_id)

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
