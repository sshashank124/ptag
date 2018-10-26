import urwid

from . import constants as C


class SelectableText(urwid.WidgetWrap):
    def __init__(self, *args, **kwargs):
        text_view = urwid.Text(*args, **kwargs)
        super().__init__(urwid.AttrMap(text_view, None, C.PLT_HIGHLIGHT))

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    @property
    def text(self):
        return self._w.base_widget.text

    @text.setter
    def text(self, value):
        self._w.base_widget.set_text(value)


class ContextText(urwid.WidgetWrap):
    def __init__(self, *args, **kwargs):
        self.visible = False
        super().__init__(urwid.Text(''))

    def set(self, attr, text):
        self._set_w(urwid.AttrMap(urwid.Text(text), attr))


class Edit(urwid.WidgetWrap):
    class _Edit(urwid.Edit):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            c = self._command_map.copy()
            c['ctrl a'] = urwid.CURSOR_MAX_LEFT
            c['ctrl e'] = urwid.CURSOR_MAX_RIGHT
            c['ctrl b'] = urwid.CURSOR_LEFT
            c['ctrl f'] = urwid.CURSOR_RIGHT
            c['ctrl u'] = C.TXT_LINE_CLR_L
            c['ctrl k'] = C.TXT_LINE_CLR_R
            c['ctrl w'] = C.TXT_WORD_CLR_L
            c['ctrl d'] = C.TXT_CHAR_CLR_R
            self._command_map = c

        def keypress(self, size, key):
            key = super().keypress(size, key)
            i = self.edit_pos
            t = self.edit_text
            cmd = self._command_map[key]
            # line
            if cmd == C.TXT_LINE_CLR_L:
                self.edit_text = t[i:]
                self.edit_pos = 0
            elif cmd == C.TXT_LINE_CLR_R:
                self.edit_text = t[:i]
            # word
            elif cmd == C.TXT_WORD_CLR_L:
                cut_idx = t[:i].rstrip().rfind(' ') + 1
                self.edit_text = t[:cut_idx] + t[i:]
                self.edit_pos = cut_idx
            # char
            elif cmd == C.TXT_CHAR_CLR_R:
                self.edit_text = t[:i] + t[i+1:]
            elif cmd in (urwid.CURSOR_PAGE_UP,
                         urwid.CURSOR_PAGE_DOWN,
                         urwid.CURSOR_UP,
                         urwid.CURSOR_DOWN):
                pass
            elif (cmd == urwid.CURSOR_LEFT and
                  self.edit_pos == 0):
                pass
            elif (cmd == urwid.CURSOR_RIGHT and
                  self.edit_pos == len(self.edit_text)):
                pass
            else:
                return key

    def __init__(self, *args, **kwargs):
        self.visible = False
        edit_view = Edit._Edit(*args, **kwargs)
        super().__init__(urwid.AttrMap(edit_view, C.PLT_INTERACT))

        urwid.register_signal(self.__class__, [C.SUBMIT, C.CANCEL])

    @property
    def text(self):
        return self._w.base_widget.edit_text

    @text.setter
    def text(self, value):
        self._w.base_widget.edit_text = value
        self._w.base_widget.edit_pos = len(value)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        cmd = self._command_map[key]
        if cmd == C.SUBMIT:
            urwid.emit_signal(self, C.SUBMIT, self.text)
        elif (cmd == C.CANCEL) or \
             (key in ('backspace', 'delete') and not self.text):
            urwid.emit_signal(self, C.CANCEL)
        else:
            return key


class PListBox(urwid.ListBox):
    class Entry(urwid.WidgetWrap):
        def __init__(self, data):
            self.data = data
            super().__init__(SelectableText(str(self.data)))

    class EditableEntry(Entry):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.editable = False
            self.submit_key = None
            self.cancel_key = None

        def set_editable(self, editable, submit_cb=None):
            if editable:
                if not self.editable:
                    self.replace_text_with_edit(submit_cb)
            elif not editable:
                if self.editable:
                    self.replace_edit_with_text()
            self.editable = editable

        def replace_text_with_edit(self, submit_cb):
            self._set_w(Edit(edit_text=str(self.data)))
            if not self.submit_key and submit_cb:
                self.submit_key = urwid.connect_signal(self._w,
                                                       C.SUBMIT,
                                                       submit_cb,
                                                       weak_args=[self])
            if not self.cancel_key:
                self.cancel_key = urwid.connect_signal(self._w,
                                                       C.CANCEL,
                                                       self.set_editable,
                                                       user_args=[False])

        def replace_edit_with_text(self):
            if self.submit_key:
                urwid.disconnect_signal(self._w, C.SUBMIT, self.submit_key)
                self.submit_key = None
            if self.cancel_key:
                urwid.disconnect_signal(self._w, C.CANCEL, self.cancel_key)
                self.cancel_key = None
            self._set_w(SelectableText(str(self.data)))

    def __init__(self, list_walker, entry_type=Entry):
        super().__init__(list_walker)

        c = self._command_map.copy()
        c['g'] = urwid.CURSOR_MAX_LEFT
        c['G'] = urwid.CURSOR_MAX_RIGHT
        c['ctrl b'] = urwid.CURSOR_PAGE_UP
        c['ctrl f'] = urwid.CURSOR_PAGE_DOWN
        c['ctrl u'] = urwid.CURSOR_PAGE_UP
        c['ctrl d'] = urwid.CURSOR_PAGE_DOWN
        self._command_map = c

    def to_entries(data, entry_type=Entry):
        return [entry_type(d) for d in data]


class VDivider(urwid.SolidFill):
    def __init__(self, fill_char=u'│'):
        super().__init__(fill_char)


class HDivider(urwid.Divider):
    def __init__(self, fill_char=u'─'):
        super().__init__(fill_char)
