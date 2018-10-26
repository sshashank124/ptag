import boolean
from peewee import SQL

from .models import Tag, Item, TagItemJoin


class Tags:
    def get_all():
        return Tag.select()


class Items:
    GLOB_ALL_FILTER = ('*', 'all')

    class Query:
        class AND_SQL(boolean.AND):
            def __str__(self):
                return '(' + ' AND '.join(str(a) for a in self.args) + ')'

        class OR_SQL(boolean.OR):
            def __str__(self):
                return '(' + ' OR '.join(str(a) for a in self.args) + ')'

        class NOT_SQL(boolean.NOT):
            def __str__(self):
                return '(NOT {})'.format(self.args[0])

        class Symbol_SQL(boolean.Symbol):
            def __str__(self):
                return '(id IN "{}")'.format(self.obj)

        parser = boolean.BooleanAlgebra(AND_class=AND_SQL,
                                        OR_class=OR_SQL,
                                        NOT_class=NOT_SQL,
                                        Symbol_class=Symbol_SQL)

        def parse(self, query_str):
            try:
                self.expr = Items.Query.parser.parse(query_str)
                tags = [s.obj for s in self.expr.symbols]
                self.tags = Tag.select().where(Tag.name << tags)
                return len(self.tags) == len(tags)
            except boolean.ParseError:
                return False

        def execute(self):
            if self.expr is None:
                return None

            ctes = [(TagItemJoin
                     .select(TagItemJoin.item_id)
                     .where(TagItemJoin.tag_id == tag.id)
                     .cte(tag.name))
                    for tag in self.tags]

            return list(Item
                        .select()
                        .with_cte(*ctes)
                        .where(SQL(str(self.expr))))

    def get_all():
        return Item.select()

    q = Query()

    def query(query_str):
        if query_str.lower() not in Items.GLOB_ALL_FILTER:
            if Items.q.parse(query_str):
                return Items.q.execute()
            else:
                return None
        else:
            return Items.get_all()
