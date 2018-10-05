import urwid as uw

from dao import Tags, Items


# utils
def outline(w):
    return uw.LineBox(w)


# UI
class CleanButton(uw.Button):
    def __init__(self, caption, callback=None, data=None):
        uw.Button.__init__(self, caption, callback, data)
        self._w = uw.SelectableIcon(caption, 0)


class ListSearchPane(uw.WidgetWrap):
    def __init__(self, list_data, search_caption):
        data_views = [CleanButton(str(datum)) for datum in list_data]
        list_walker = uw.SimpleFocusListWalker(data_views)
        list_view = uw.ListBox(list_walker)

        search = uw.Edit(caption=search_caption)

        root_view = uw.Pile([list_view,
                             ('pack', search)])

        uw.WidgetWrap.__init__(self, root_view)


class TagsPane(ListSearchPane):
    def __init__(self):
        tags = Tags.get_all() + ['testing', 'some', 'more']

        ListSearchPane.__init__(self, tags, 'Filter: ')


class ItemsPane(uw.WidgetWrap):
    def __init__(self):
        items = Items.get_all()

        ListSearchPane.__init__(self, items, 'Query: ')


# MAIN LOOP
def exit_on_q(key):
    if key == 'q':
        raise uw.ExitMainLoop()


def run():
    root_view = uw.Columns([('weight', 0.3, TagsPane()),
                            ('weight', 0.7, ItemsPane())])

    uw.MainLoop(root_view, unhandled_input=exit_on_q).run()
