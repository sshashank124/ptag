import urwid

from .constants import C_SUBMIT, C_CANCEL, C_SEARCH, C_MESSAGE
from .constants import C_MSG_LVL_WARN
from data.dao import Tags, Items
from .utils import PEdit, PListBox, HDivider


class _FilterableListFragment(urwid.WidgetWrap):
    def __init__(self,
                 title,
                 search_caption):
        # HEADER
        self.title = title
        self.title_text = urwid.Text(self.title)

        # LIST VIEW
        self.list_walker = urwid.SimpleFocusListWalker([])
        self.list_view = PListBox(self.list_walker)
        self.set_data(self.default_list_data)

        # SEARCH BOX
        self.search_view = PEdit(search_caption)
        urwid.connect_signal(self.search_view, C_SUBMIT, self.filter_list)
        urwid.connect_signal(self.search_view, C_CANCEL, self.exit_search)

        self.filtered = False

        # COMMANDS
        c = self._command_map.copy()
        c['/'] = C_SEARCH
        self._command_map = c

        # SIGNALS
        urwid.register_signal(self.__class__, [C_SUBMIT, C_MESSAGE])

        # MAIN VIEW
        self.pile = urwid.Pile([(urwid.PACK, self.title_text),
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

    def set_search_visible(self, visible):
        if visible:
            if not self.search_view.visible:
                self.pile.contents.append((self.search_view,
                                           (urwid.PACK, None)))
            self.pile.focus_position = len(self.pile.contents) - 1
        elif not visible:
            if self.search_view.visible:
                self.pile.contents.pop()
        self.search_view.visible = visible

    def set_filtered(self, filtered):
        if filtered:
            if not self.filtered:
                self.title_text.set_text(self.title + ' [*]')
        elif not filtered:
            if self.filtered:
                self.title_text.set_text(self.title)
        self.filtered = filtered

    def enter_search(self, text=None):
        self.set_search_visible(True)
        if text is not None:
            self.search_view.text = text

    def exit_search(self):
        self.set_search_visible(False)

    def exit_filter(self):
        if self.filtered:
            self.set_filtered(False)
            self.exit_search()
            self.set_data(self.default_list_data)

    def set_data(self, data):
        self.list_walker[:] = PListBox.to_entries(data)

    def list_item_selected(self):
        focus_item = self.list_view.focus
        if focus_item is not None:
            urwid.emit_signal(self, C_SUBMIT, focus_item.data)

    def filter_list(self, filter_str):
        raise NotImplementedError()


class TagsFragment(_FilterableListFragment):
    def __init__(self):
        self.default_list_data = list(Tags.get_all())
        super().__init__('TAGS', '/')

    def filter_list(self, filter_str):
        if filter_str:
            self.set_filtered(True)
            filtered_list_data = filter(lambda d: d.contains_i(filter_str),
                                        self.default_list_data)
            self.set_data(filtered_list_data)
        else:
            self.exit_filter()


class ItemsFragment(_FilterableListFragment):
    def __init__(self):
        self.default_list_data = []
        super().__init__('ITEMS', 'expr> ')

    def filter_list(self, filter_str):
        if filter_str:
            items = Items.query(filter_str)
            if items:
                self.set_filtered(True)
                self.set_data(items)
            else:
                urwid.emit_signal(self,
                                  C_MESSAGE,
                                  C_MSG_LVL_WARN,
                                  'Invalid Query')
        else:
            self.exit_filter()
