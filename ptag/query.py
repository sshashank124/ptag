import boolean as b
from peewee import SQL
from typing import List

from models import Tag, Item, TagItemJoin


class AND_SQL(b.AND):
    def __str__(self):
        return '(' + ' AND '.join(str(a) for a in self.args) + ')'


class OR_SQL(b.OR):
    def __str__(self):
        return '(' + ' OR '.join(str(a) for a in self.args) + ')'


class NOT_SQL(b.NOT):
    def __str__(self):
        return '(NOT {})'.format(self.args[0])


class Symbol_SQL(b.Symbol):
    def __str__(self):
        return '(id IN {})'.format(self.obj)


parser = b.BooleanAlgebra(AND_class=AND_SQL,
                          OR_class=OR_SQL,
                          NOT_class=NOT_SQL,
                          Symbol_class=Symbol_SQL)


class Query():
    def parse(self, query_str: str) -> bool:
        # throw various errors for various problems
        try:
            self.expr = parser.parse(query_str)
            tags = [s.obj for s in self.expr.symbols]
            self.tags = list(Tag.select().where(Tag.name << tags))
            return len(self.tags) == len(tags)
        except b.ParseError:
            return False

    def execute(self) -> List[Item]:
        # handle default case: SELECT * from item
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
