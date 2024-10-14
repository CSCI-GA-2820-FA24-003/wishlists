"""
Test Factory to make fake objects for testing
"""

import factory
from faker import Faker
from service.models import Wishlist

test = Faker()


class WishlistFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    item_id = factory.LazyAttribute(lambda _: test.random_int(min=1000, max=9999))
    item_name = factory.Faker("word")
    quantity = factory.LazyAttribute(lambda _: test.random_int(min=1, max=100))
    updated_time = factory.LazyAttribute(
        lambda _: test.date_time_between(start_date="-5y", end_date="now")
    )
    note = factory.Faker("sentence", nb_words=10)
