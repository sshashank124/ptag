import enum
import urwid

from .constants import C_SUBMIT, C_CANCEL, C_SEARCH
from data.dao import Tags, Items
from .utils import PEdit, PListBox, HDivider


class _FilterableListFragment(urwid.WidgetWrap):
    class Mode(enum.Enum):
        NORMAL = 0
        SEARCH = 1
        FILTERED = 2

    def __init__(self,
                 title,
                 search_caption):
        # HEADER
        title_text = urwid.Text(title)

        # LIST VIEW
        self.list_walker = urwid.SimpleFocusListWalker([])
        self.list_view = PListBox(self.list_walker)
        self.load_data()

        # SEARCH BOX
        self.search_view = PEdit(search_caption)
        urwid.connect_signal(self.search_view, C_SUBMIT, self.filter_list)
        urwid.connect_signal(self.search_view, C_CANCEL, self.exit_search)

        self.mode = self.Mode.NORMAL

        # COMMANDS
        c = self._command_map.copy()
        c['/'] = C_SEARCH
        self._command_map = c

        # SIGNALS
        urwid.register_signal(self.__class__, [C_SUBMIT])

        # MAIN VIEW
        self.pile = urwid.Pile([(urwid.PACK, title_text),
                                (urwid.PACK, HDivider()),
                                self.list_view])
        super().__init__(self.pile)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if self._command_map[key] == C_SEARCH:
            self.enter_search()
        elif self._command_map[key] == C_SUBMIT:
            self.list_item_selected()
        elif self._command_map[key] == C_CANCEL:
            self.exit_filter()
        else:
            return key

    def enter_search(self, text=None):
        if self.mode == self.Mode.NORMAL:
            self.pile.contents.append((self.search_view, (urwid.PACK, None)))
            self.mode = self.Mode.SEARCH
        self.pile.focus_position = len(self.pile.contents) - 1
        if text is not None:
            self.search_view.text = text

    def exit_search(self):
        if self.mode != self.Mode.NORMAL:
            self.pile.contents.pop()
            self.search_view.text = ''
            self.mode = self.Mode.NORMAL

    def exit_filter(self):
        if self.mode == self.Mode.FILTERED:
            self.exit_search()
            self.load_data()

    def load_data(self):
        raise NotImplementedError()

    def list_item_selected(self):
        focus_item = self.list_view.focus
        if focus_item is not None:
            urwid.emit_signal(self, C_SUBMIT, focus_item.data)

    def filter_list(self, filter_str):
        raise NotImplementedError()


class TagsFragment(_FilterableListFragment):
    def __init__(self):
        super().__init__('Tags', '/')

    def filter_list(self, filter_str):
        pass  # TODO: search submission

    def load_data(self):
        self.list_walker[:] = [PListBox.Entry(tag) for tag in Tags.get_all()]


class ItemsFragment(_FilterableListFragment):
    def __init__(self):
        super().__init__('Items', 'expr> ')

    def filter_list(self, filter_str):
        if self.mode == self.Mode.NORMAL:
            return

        items = Items.query(filter_str)
        if items:
            self.mode = self.Mode.FILTERED
            # TODO
        else:
            pass  # TODO: notify failed: perhaps add a universal status bar

    def load_data(self):
        pass  # TODO
