from scrapy import Item, Field

class VetItem(Item):
    url = Field()
    name = Field()
    subtitle = Field()
    address = Field()
    phone = Field()
    opening_hours = Field()
    category = Field()
    metadata = Field()