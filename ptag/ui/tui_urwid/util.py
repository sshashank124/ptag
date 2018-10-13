import urwid as uw


SIGNAL_SUBMIT = 'signal_submit'
SIGNAL_CANCEL = 'signal_cancel'

COMMAND_CURSOR_CLEAR_LEFT = 'cursor clear left'
COMMAND_CURSOR_CLEAR_RIGHT = 'cursor clear right'


class SelectableText(uw.Text):
    def selectable(self):
        return True

    def keypress(self, _, key):
        return key


class PEdit(uw.WidgetWrap):
    class _Edit(uw.Edit):
        def __init__(self, caption):
            super().__init__(caption)

            c = self._command_map.copy()
            c['ctrl a'] = uw.CURSOR_MAX_LEFT
            c['ctrl e'] = uw.CURSOR_MAX_RIGHT
            c['ctrl b'] = uw.CURSOR_LEFT
            c['ctrl f'] = uw.CURSOR_RIGHT
            c['ctrl u'] = COMMAND_CURSOR_CLEAR_LEFT
            c['ctrl k'] = COMMAND_CURSOR_CLEAR_RIGHT
            self._command_map = c

        def keypress(self, size, key):
            key = super().keypress(size, key)
            if self._command_map[key] == COMMAND_CURSOR_CLEAR_LEFT:
                self.edit_text = self.edit_text[self.edit_pos:]
                self.edit_pos = 0
            elif self._command_map[key] == COMMAND_CURSOR_CLEAR_RIGHT:
                self.edit_text = self.edit_text[:self.edit_pos]
            else:
                return key

    def __init__(self, search_caption):
        self.edit_view = PEdit._Edit(caption=search_caption)
        super().__init__(uw.AttrMap(self.edit_view, 'highlight'))

        uw.register_signal(self.__class__,
                           [SIGNAL_SUBMIT,
                            SIGNAL_CANCEL])

    @property
    def text(self):
        return self.edit_view.edit_text

    @text.setter
    def text(self, value):
        self.edit_view.edit_text = value

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key == 'enter':
            uw.emit_signal(self, SIGNAL_SUBMIT, self.text)
        elif key == 'esc':
            self.text = ''
            uw.emit_signal(self, SIGNAL_CANCEL)
        else:
            return key


class PListBox(uw.ListBox):
    class Entry(uw.WidgetWrap):
        def __init__(self, data):
            self.data = data
            self.text_view = SelectableText(str(self.data))
            super().__init__(uw.AttrMap(self.text_view, None, 'highlight'))

    def __init__(self, list_walker):
        super().__init__(list_walker)

        c = self._command_map.copy()
        c['g'] = uw.CURSOR_MAX_LEFT
        c['G'] = uw.CURSOR_MAX_RIGHT
        c['ctrl b'] = uw.CURSOR_PAGE_UP
        c['ctrl f'] = uw.CURSOR_PAGE_DOWN
        self._command_map = c


class VDivider(uw.SolidFill):
    def __init__(self):
        super().__init__(u'│')


class HDivider(uw.Divider):
    def __init__(self):
        super().__init__(u'─')
