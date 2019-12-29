from mongoengine import Document
from mongoengine import FloatField
from mongoengine import IntField
from mongoengine import StringField


class ShopInfo(Document):
    id = IntField(required=True, primary_key=True)
    name = StringField(required=True)
    address = StringField()
    phone_number = StringField()
    url = StringField()
    rating = StringField()
    reviews = IntField()
    avg_cost = FloatField()
    production_rating = FloatField()
    environment_rating = FloatField()
    service_rating = FloatField()

    def __str__(self):
        return (f'<ShopInfo id={self.id}, name={self.name}, address={self.address}, '
                f'phone_number={self.phone_number}, url={self.url}, rating={self.rating}, '
                f'reviews={self.reviews}, avg cost={self.avg_cost}, '
                f'prod rating={self.production_rating}, env rating={self.environment_rating}, '
                f'service rating={self.service_rating}>')
