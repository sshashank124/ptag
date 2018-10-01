from peewee import SqliteDatabase, Model, CharField, ForeignKeyField


db = SqliteDatabase('tagmap.db', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class Tag(BaseModel):
    name = CharField(unique=True)
    description = CharField(null=True)

    def get_items(self):
        return (Item
                .select()
                .join(TagItemJoin)
                .where(TagItemJoin.tag == self))

    def __str__(self):
        return 'Tag({})'.format(self.name)


class Item(BaseModel):
    text = CharField()
    description = CharField(null=True)

    def get_tags(self):
        return (Tag
                .select()
                .join(TagItemJoin)
                .where(TagItemJoin.item == self))

    def __str__(self):
        return 'Item({})'.format(self.text)


class TagItemJoin(BaseModel):
    tag = ForeignKeyField(Tag, backref='items')
    item = ForeignKeyField(Item, backref='tags')

    class Meta:
        indexes = ((('tag', 'item'), True),)


def create_tables():
    with db:
        db.create_tables([Tag, Item, TagItemJoin])
