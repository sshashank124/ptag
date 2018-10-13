import enum
import urwid as uw

from data.dao import Tags, Items
from .util import (PEdit, PListBox,
                   HDivider, VDivider,
                   SIGNAL_SUBMIT, SIGNAL_CANCEL)


class SearchableListFragment(uw.WidgetWrap):
    class Mode(enum.Enum):
        NORMAL = 0
        SEARCH = 1
        FILTERED = 2

    def __init__(self,
                 title,
                 list_data,
                 search_caption):
        # HEADER
        title_text = uw.Text(title)

        # LIST VIEW
        data_views = [PListBox.Entry(datum) for datum in list_data]
        self.list_view = PListBox(uw.SimpleFocusListWalker(data_views))

        # SEARCH BOX
        self.search_view = PEdit(search_caption)
        uw.connect_signal(self.search_view, SIGNAL_SUBMIT, self.filter_list)
        uw.connect_signal(self.search_view, SIGNAL_CANCEL, self.exit_search)

        self.mode = self.Mode.NORMAL

        # SIGNALS
        uw.register_signal(self.__class__, [SIGNAL_SUBMIT])

        # MAIN VIEW
        self.pile = uw.Pile([(uw.PACK, title_text),
                             (uw.PACK, HDivider()),
                             self.list_view])
        super().__init__(self.pile)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key == '/':
            self.enter_search()
        elif key == 'enter':
            self.list_item_selected()
        else:
            return key

    def enter_search(self):
        if self.mode == self.Mode.NORMAL:
            self.pile.contents.append((self.search_view, (uw.PACK, None)))
            self.mode = self.Mode.SEARCH
        self.pile.focus_position = len(self.pile.contents) - 1

    def exit_search(self):
        if self.mode != self.Mode.NORMAL:
            self.pile.contents.pop()
            self.mode = self.Mode.NORMAL

    def list_item_selected(self):
        focus_item = self.list_view.focus
        if focus_item is not None:
            uw.emit_signal(self, SIGNAL_SUBMIT, focus_item.data)

    def filter_list(self, filter_str):
        raise NotImplementedError()


class TagsFragment(SearchableListFragment):
    def __init__(self):
        tags = Tags.get_all()
        super().__init__('Tags', tags, '/')

    def filter_list(self, filter_str):
        pass


class ItemsFragment(SearchableListFragment):
    def __init__(self):
        items = Items.get_all()
        super().__init__('Items', items, 'expr> ')

    def filter_list(self, filter_str):
        pass


# MAIN
class App:
    palette = [('highlight', 'standout', 'default')]

    def __init__(self):
        # UPDATE COMMANDS
        c = uw.command_map
        c['h'] = uw.CURSOR_LEFT
        c['j'] = uw.CURSOR_DOWN
        c['k'] = uw.CURSOR_UP
        c['l'] = uw.CURSOR_RIGHT

        self.tags_fragment = TagsFragment()
        uw.connect_signal(self.tags_fragment,
                          SIGNAL_SUBMIT,
                          self.handle_tag_selected)

        self.items_fragment = ItemsFragment()

        self.root_view = uw.Columns([(uw.WEIGHT, 0.3, self.tags_fragment),
                                     (1, VDivider()),
                                     (uw.WEIGHT, 0.7, self.items_fragment)])

    def handle_tag_selected(self, tag):
        # filter items fragment
        self.items_fragment.search_view.text = 'received: {}'.format(str(tag))
        pass

    def run(self):
        self.loop = uw.MainLoop(self.root_view,
                                App.palette,
                                unhandled_input=App.exit_on_q)
        self.loop.run()

    def exit_on_q(key):
        if key == 'q':
            raise uw.ExitMainLoop()


def run():
    app = App()
    app.run()
