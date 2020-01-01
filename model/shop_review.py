from mongoengine import Document
from mongoengine import FloatField
from mongoengine import IntField
from mongoengine import StringField


class ShopReview(Document):
    id = StringField(required=True, primary_key=True)
    username = StringField()
    shop_id = IntField(required=True)
    shop_name = StringField(required=True)
    rating = FloatField()
    comment = StringField(required=True)
    timestamp = StringField(required=True)

    def __str__(self):
        return (f'<ShopReview, id={self.id}, username={self.username}, shop_id={self.shop_id}, '
                f'shop_name={self.shop_name}, rating={self.rating}, comment={self.comment}, '
                f'timestamp={self.timestamp}>')
