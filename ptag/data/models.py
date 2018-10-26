import peewee


db = peewee.SqliteDatabase('ptag.db', pragmas={'foreign_keys': 1})


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Tag(BaseModel):
    name = peewee.CharField(unique=True)
    description = peewee.CharField(null=True)

    def get_items(self):
        return (Item
                .select()
                .join(TagItemJoin)
                .where(TagItemJoin.tag == self))

    def __str__(self):
        return self.name

    def contains_i(self, s):
        return s.lower() in self.__str__().lower()


class Item(BaseModel):
    text = peewee.CharField()
    description = peewee.CharField(null=True)

    def get_tags(self):
        return (Tag
                .select()
                .join(TagItemJoin)
                .where(TagItemJoin.item == self))

    def __str__(self):
        return self.text


class TagItemJoin(BaseModel):
    tag = peewee.ForeignKeyField(Tag, backref='items')
    item = peewee.ForeignKeyField(Item, backref='tags')

    class Meta:
        indexes = ((('tag', 'item'), True),)


def create_tables():
    with db:
        db.create_tables([Tag, Item, TagItemJoin])
