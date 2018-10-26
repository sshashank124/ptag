import urwid

from . import constants as C
from data.dao import (Tags, Items,
                      RecordNotFoundException, RecordConstraintException,
                      RecordInvalidFieldException)
from .utils import Edit, PListBox, HDivider


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

        self.load_default_data()
        self.set_data(self.default_list_data)

        # SEARCH BOX
        self.search_view = Edit(caption=search_caption)
        urwid.connect_signal(self.search_view, C.SUBMIT, self.filter_list)
        urwid.connect_signal(self.search_view, C.CANCEL, self.exit_search)

        self.filter_str = ''

        # COMMANDS
        c = self._command_map.copy()
        c['/'] = C.SEARCH
        c['r'] = C.REFRESH
        c['i'] = C.ITEM_EDIT
        c['a'] = C.ITEM_ADD
        c['d'] = C.ITEM_DEL
        self._command_map = c

        # SIGNALS
        urwid.register_signal(self.__class__, [C.SUBMIT, C.MESSAGE])

        # MAIN VIEW
        self.pile = urwid.Pile([(urwid.PACK, self.title_text),
                                (urwid.PACK, HDivider()),
                                self.list_view])
        super().__init__(self.pile)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        cmd = self._command_map[key]
        if cmd == C.SEARCH:
            self.enter_search()
        elif cmd == C.REFRESH:
            self.refresh_list()
        elif cmd == C.SUBMIT:
            self.list_item_selected()
        elif cmd == C.CANCEL:
            self.exit_filter()
        elif cmd == C.ITEM_EDIT:
            self.list_item_edit()
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

    def set_filter(self, filter_str):
        if filter_str != self.filter_str:
            if filter_str:
                self.title_text.set_text('{} [{}]'.format(self.title,
                                                          filter_str))
            else:
                self.title_text.set_text(self.title)
            self.filter_str = filter_str

    def enter_search(self, text=None):
        self.set_search_visible(True)
        if text is not None:
            self.search_view.text = text

    def exit_search(self):
        self.set_search_visible(False)

    def exit_filter(self):
        if self.filter_str:
            self.set_filter('')
            self.exit_search()
            self.set_data(self.default_list_data)

    def load_default_data(self, data):
        raise NotImplementedError()

    def set_data(self, data):
        self.list_walker[:] = PListBox.to_entries(data)

    def list_item_selected(self):
        focus_item = self.list_view.focus
        if focus_item is not None:
            urwid.emit_signal(self, C.SUBMIT, focus_item.data)

    def filter_list(self, filter_str):
        if self._filter_list(filter_str):
            self.pile.focus_position = 2

    def _filter_list(self, filter_str):
        raise NotImplementedError()

    def list_item_edit(self):
        if self.list_view.focus:
            self._list_item_edit(self.list_view.focus,
                                 self.list_view.focus_position)

    def _list_item_edit(self, item, position):
        raise NotImplementedError()

    def refresh_list(self):
        raise NotImplementedError()


class TagsFragment(_FilterableListFragment):
    def __init__(self):
        super().__init__('TAGS', '/')

    def load_default_data(self):
        self.default_list_data = list(Tags.get_all())

    def set_data(self, data):
        self.list_walker[:] = PListBox.to_entries(data,
                                                  PListBox.EditableEntry)

    def _filter_list(self, filter_str):
        if filter_str:
            self.set_filter(filter_str)
            filtered_list_data = filter(lambda d: d.contains_i(filter_str),
                                        self.default_list_data)
            self.set_data(filtered_list_data)
            return True
        else:
            self.exit_filter()

        return False

    def _list_item_edit(self, item, position):
        self.list_walker[position].set_editable(True, self.update_tag_name)

    def update_tag_name(self, list_entry, new_name):
        old_name = list_entry.data.name
        try:
            list_entry.data.name = new_name
            Tags.update(list_entry.data)
            urwid.emit_signal(self,
                              C.MESSAGE,
                              C.MSG_LVL_INFO,
                              f"Tag name successfully updated to '{new_name}'")
            list_entry.set_editable(False)
        except (RecordNotFoundException,
                RecordConstraintException,
                RecordInvalidFieldException) as e:
            list_entry.data.name = old_name
            urwid.emit_signal(self,
                              C.MESSAGE,
                              C.MSG_LVL_ERROR,
                              str(e))

    def refresh_list(self):
        self.load_default_data()
        if self.filter_str:
            self.filter_list(self.filter_str)
        else:
            self.set_data(self.default_list_data)


# TODO: might need self.cached field and force cache for outside changes
class ItemsFragment(_FilterableListFragment):
    def __init__(self):
        super().__init__('ITEMS', 'expr> ')

    def load_default_data(self):
        self.default_list_data = []

    def _filter_list(self, filter_str):
        if filter_str:
            items = Items.query(filter_str)
            if items:
                self.set_filter(filter_str)
                self.set_data(items)
                return True
            else:
                urwid.emit_signal(self,
                                  C.MESSAGE,
                                  C.MSG_LVL_ERROR,
                                  'Invalid Query')
        else:
            self.exit_filter()

        return False

    def refresh_list(self):
        if self.filter_str:
            self.filter_list(self.filter_str)
        else:
            self.load_default_data()
            self.set_data(self.default_list_data)
