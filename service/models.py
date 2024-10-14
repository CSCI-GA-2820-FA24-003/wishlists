"""
Models for Wishlist

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Wishlist(db.Model):
    """
    Class that represents a Wishlist
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)  # wishlist id
    name = db.Column(db.String(100), nullable=True)  # wishlist name
    item_id = db.Column(db.Integer, nullable=True)
    item_name = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    updated_time = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.String(1000), nullable=True)

    items = db.relationship(
        "Item", backref="wishlist", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Wishlist to the database
        """
        logger.info("Creating %s", self.name)
        # self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Wishlist to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Wishlist from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Wishlist into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "updated_time": (
                self.updated_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
                if self.updated_time
                else None
            ),
            "note": self.note,
        }

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.item_id = data["item_id"]
            self.item_name = data["item_name"]
            self.quantity = data["quantity"]
            self.updated_time = data["updated_time"]
            self.note = data["note"]

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Wishlists in the database"""
        logger.info("Processing all Wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Wishlist by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Wishlists with the given name

        Args:
            name (string): the name of the Wishlists you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)


class Item(db.Model):
    """
    Class that represents a Item (Item) in a Wishlist
    """

    id = db.Column(db.Integer, primary_key=True)  # id of each item
    wishlist_id = db.Column(db.Integer, db.ForeignKey("wishlist.id"), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f"<Item {self.item_name} in Wishlist {self.wishlist_id}>"

    def serialize(self):
        """
        Insert an Item into a database
        """
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "note": self.note,
        }

    def deserialize(self, data):
        """
        Remove an Item from a database
        """
        try:
            self.item_name = data["item_name"]
            self.quantity = data["quantity"]
            self.note = data.get("note", "")
        except KeyError as error:
            raise DataValidationError(
                f"Invalid Items in the Wishlist: missing {error.args[0]}"
            )
        return self
