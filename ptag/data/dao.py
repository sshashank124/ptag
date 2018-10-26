import boolean
import peewee
import re

from .models import Tag, Item, TagItemJoin


class Tags:
    valid_name_pattern = re.compile(r'^[a-zA-Z][\w\.]{,49}$')

    def is_valid_name(name):
        return bool(Tags.valid_name_pattern.match(name))

    def get_all():
        return Tag.select()

    def update(tag):
        try:
            if not Tags.is_valid_name(tag.name):
                msg = ("Tag name '{}' doesn't satisfy '{}'"
                       .format(tag.name, Tags.valid_name_pattern.pattern))
                raise RecordInvalidFieldException(msg)

            if tag.save() == 0:
                raise RecordNotFoundException(('No record found '
                                               f'with id {tag.id}'))
        except peewee.IntegrityError:
            raise RecordConstraintException(('Duplicate tag name '
                                             f"'{tag.name}'"))


class Items:
    GLOB_ALL_FILTER = ('*', '.')
    GLOB_NONE_FILTER = ('~', '!')

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
                        .where(peewee.SQL(str(self.expr))))

    def get_all():
        return Item.select()

    def get_untagged():
        raise NotImplementedError()  # TODO

    q = Query()

    def query(query_str):
        if query_str in Items.GLOB_ALL_FILTER:
            return Items.get_all()
        elif query_str in Items.GLOB_NONE_FILTER:
            return Items.get_untagged()
        else:
            if Items.q.parse(query_str):
                return Items.q.execute()
            else:
                return None


class RecordNotFoundException(Exception):
    pass


class RecordConstraintException(Exception):
    pass


class RecordInvalidFieldException(Exception):
    pass
