import urwid as uw

from data.dao import Tags, Items


# utils
# TODO: remove
def outline(w):
    return uw.LineBox(w)


# UI
class VDivider(uw.SolidFill):
    def __init__(self):
        super().__init__(u'\u2502')


class FocusableText(uw.WidgetWrap):
    class _Text(uw.Text):
        _selectable = True

        def keypress(self, _, key):
            return key

    def __init__(self, text):
        root_view = uw.AttrMap(FocusableText._Text(text), None, 'highlight')
        super().__init__(root_view)


class ListSearchPane(uw.WidgetWrap):
    def __init__(self, list_data, search_caption):
        data_views = [FocusableText(str(datum)) for datum in list_data]
        list_walker = uw.SimpleFocusListWalker(data_views)
        list_view = uw.ListBox(list_walker)

        self.search = uw.Edit(caption=search_caption)

        self.pile = uw.Pile([list_view])
        super().__init__(self.pile)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key == '/':
            self.pile.contents.append((self.search, (uw.PACK, None)))
            self.pile.set_focus(self.search)
        else:
            return key


class TagsPane(ListSearchPane):
    def __init__(self):
        tags = Tags.get_all() + ['testing' for i in range(100)]
        super().__init__(tags, '/')


class ItemsPane(ListSearchPane):
    def __init__(self):
        items = Items.get_all()
        super().__init__(items, 'expr: ')


# MAIN LOOP
def exit_on_q(key):
    if key == 'q':
        raise uw.ExitMainLoop()


def run():
    palette = [('highlight', 'default,standout', 'default')]

    root_view = uw.Columns([(uw.WEIGHT, 0.3, TagsPane()),
                            (uw.FIXED, 1, VDivider()),
                            (uw.WEIGHT, 0.7, ItemsPane())])

    c = root_view._command_map
    c['h'] = uw.CURSOR_LEFT
    c['j'] = uw.CURSOR_DOWN
    c['k'] = uw.CURSOR_UP
    c['l'] = uw.CURSOR_RIGHT

    uw.MainLoop(root_view, palette, unhandled_input=exit_on_q).run()
