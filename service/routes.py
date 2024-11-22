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
    """Health check endpoint: Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


# or
# @app.route("/health", methods=["GET"])
# def health():
#    """Health check endpoint: Let them know our heart is still beating"""
#    app.logger.info("Health check endpoint called")
#    return jsonify({"status": "OK"}), status.HTTP_200_OK
######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")
    # return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# List wishlist
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """Return list of all Wishlists"""
    wls = []

    is_favorite = request.args.get("is_favorite")
    # Parse any arguments from the query string
    if is_favorite:
        app.logger.info("Find by is_favorite: %s", is_favorite)
        # create bool from string
        is_favorite_value = is_favorite.lower() in ["true", "yes", "1"]
        wls = Wishlist.find_by_favorite(is_favorite_value)
    else:
        app.logger.info("Find all")
        wls = Wishlist.all()
    results = [wl.serialize() for wl in wls]
    app.logger.info("Returning %d WLs", len(results))

    return jsonify(results), status.HTTP_200_OK


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

    location_url = url_for("get_wishlists", wishlist_id=wishlist.id, _external=True)

    return (
        jsonify(wishlist.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# UPDATE A NEW Wishlist
######################################################################
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

    # Ensure the ID is set before updating
    if not wishlist.id:
        abort(status.HTTP_400_BAD_REQUEST, "Cannot update wishlist with empty ID.")

    # Save the updates to the database
    wishlist.update()
    app.logger.info("Wishlist with ID: %d updated.", wishlist.id)
    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# READ A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist
    This endpoint will return a Wishlist based on it's id
    """
    app.logger.info("Request for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist
    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

    # Retrieve the wishlist to delete and delete it if it exists
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################


######################################################################
# CREATE AN ITEM
######################################################################
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


######################################################################
# GET AN ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["GET"])
def get_items(wishlist_id, item_id):
    """
    Get an Item

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


######################################################################
# DELETE AN ITEM
######################################################################
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
# UPDATE AN ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["PUT"])
def update_item(wishlist_id, item_id):
    """
    Update an Item in a Wishlist


    This endpoint will update an Item based on the body that is posted
    """
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(404, description=f"Wishlist with id '{wishlist_id}' was not found.")

    item = Items.find(item_id)
    if not item or item.wishlist_id != wishlist_id:
        abort(
            404,
            description=f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
        )

    data = request.get_json()
    item.deserialize(data)

    # Ensure the ID is set before updating
    if not item.id:
        abort(status.HTTP_400_BAD_REQUEST, "Cannot update item with empty ID.")

    item.update()
    return jsonify(item.serialize()), 200


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


######################################################################
# QUERY ITEMS BASED ON THEIR ATTRIBUTES
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def get_all_items(wishlist_id):
    """
    Get all Items in WL
    """
    name = request.args.get("name")
    category = request.args.get("category")
    price = request.args.get("price", type=float)
    is_favorite = request.args.get("is_favorite")
    app.logger.info("Request to create an Item for Wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    if name:
        app.logger.info("Filtering by name: %s", name)
        items = Items.find_by_name(wishlist_id=wishlist_id, name=name)
    if category:
        app.logger.info("Filtering by category: %s", category)
        items = Items.find_by_category(wishlist_id=wishlist_id, category=category)
    elif price is not None:
        app.logger.info("Filtering by price: %s", price)
        items = Items.find_by_price(wishlist_id=wishlist_id, price=price)
    elif is_favorite:
        app.logger.info("Find by is_favorite: %s", is_favorite)
        # create bool from string
        is_favorite_value = is_favorite.lower() in ["true", "yes", "1"]
        items = Items.find_by_favorite(wishlist_id, is_favorite_value)
    else:
        app.logger.info("Retrieving all items in wishlist")
        items = Items.all()

    results = [item.serialize() for item in items]
    app.logger.info("[%s] Items returned", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# MARK AN ITEM AS FAVORITE
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>/favorite", methods=["PUT"])
def mark_item_favorite(wishlist_id, item_id):
    """
    Mark an item as favorite in a wishlist
    """
    app.logger.info(
        "Request to mark item [%s] as favorite in Wishlist with id: %s",
        item_id,
        wishlist_id,
    )

    # Find the item and return 404 if not found
    item = Items.find(item_id)
    if not item or item.wishlist_id != wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    # Mark the item as favorite
    item.is_favorite = True
    item.update()
    app.logger.info(
        "Item [%s] marked as favorite in Wishlist [%s]", item_id, wishlist_id
    )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# CANCEL AN ITEM AS FAVORITE
######################################################################
@app.route(
    "/wishlists/<int:wishlist_id>/items/<int:item_id>/favorite", methods=["DELETE"]
)
def cancel_item_favorite(wishlist_id, item_id):
    """
    Cancel an item as favorite in a wishlist
    """
    app.logger.info(
        "Request to cancel item [%s] as favorite in Wishlist with id: %s",
        item_id,
        wishlist_id,
    )

    # Find the item and return 404 if not found
    item = Items.find(item_id)
    if not item or item.wishlist_id != wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    # Cancel the item as favorite
    item.is_favorite = False
    item.update()
    app.logger.info(
        "Item [%s] canceled as favorite in Wishlist [%s]", item_id, wishlist_id
    )

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# MARK AN WISHLIST AS FAVORITE
######################################################################
@app.route("/wishlists/<int:wishlist_id>/favorite", methods=["PUT"])
def mark_wishlist_favorite(wishlist_id):
    """
    Mark an item as favorite in a wishlist
    """
    app.logger.info(
        "Request to mark wishlist [%s] as favorite",
        wishlist_id,
    )

    # Find the item and return 404 if not found
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Mark the item as favorite
    wishlist.is_favorite = True
    wishlist.update()
    app.logger.info("Wishlist [%s] marked as favorite", wishlist_id)

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# CANCEL AN ITEM AS FAVORITE
######################################################################
@app.route("/wishlists/<int:wishlist_id>/favorite", methods=["DELETE"])
def cancel_wishlist_favorite(wishlist_id):
    """
    Cancel an item as favorite in a wishlist
    """
    app.logger.info(
        "Request to cancel wishlist [%s] as favorite",
        wishlist_id,
    )

    # Find the item and return 404 if not found
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Cancel the wishlist as favorite
    wishlist.is_favorite = False
    wishlist.update()
    app.logger.info("Wishlist [%s] canceled as favorite", wishlist_id)

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


# search item using query str
"""
@app.route("/wishlists/<int:wishlist_id>/items/name", methods=["GET"])
def search_items(wishlist_id):
    
    Search Item by name in given WL
    
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    item_name = request.args.get("search", default="")

    for itm in wishlist.serialize()["items"]:
        if itm["name"] == item_name:
            return itm, status.HTTP_200_OK

    abort(
        status.HTTP_404_NOT_FOUND,
        f"Item '{item_name}' could not be found in id '{wishlist_id}'  :(",
    )
"""
