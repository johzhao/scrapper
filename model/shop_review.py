from mongoengine import Document
from mongoengine import FloatField
from mongoengine import IntField
from mongoengine import StringField


class ShopReview(Document):
    id = IntField()
    username = StringField(required=True)
    shop_id = IntField(required=True)
    shop_name = StringField(required=True)
    rating = FloatField()
    comment = StringField()
    timestamp = StringField()

    def __str__(self):
        return (f'<ShopReview, id={self.id}, username={self.username}, shop_id={self.shop_id}, '
                f'shop_name={self.shop_name}, rating={self.rating}, comment={self.comment}, '
                f'timestamp={self.timestamp}>')
