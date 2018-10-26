import urwid as uw

from .constants import (C_SUBMIT, C_CANCEL,
                        C_TXT_LINE_CLR_L, C_TXT_LINE_CLR_R,
                        C_TXT_WORD_CLR_L,
                        C_TXT_CHAR_CLR_R)


class SelectableText(uw.Text):
    def selectable(self):
        return True

    def keypress(self, _, key):
        return key


class ContextText(uw.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible = False


class PEdit(uw.WidgetWrap):
    class _Edit(uw.Edit):
        def __init__(self, caption):
            super().__init__(caption)

            c = self._command_map.copy()
            c['ctrl a'] = uw.CURSOR_MAX_LEFT
            c['ctrl e'] = uw.CURSOR_MAX_RIGHT
            c['ctrl b'] = uw.CURSOR_LEFT
            c['ctrl f'] = uw.CURSOR_RIGHT
            c['ctrl u'] = C_TXT_LINE_CLR_L
            c['ctrl k'] = C_TXT_LINE_CLR_R
            c['ctrl w'] = C_TXT_WORD_CLR_L
            c['ctrl d'] = C_TXT_CHAR_CLR_R
            self._command_map = c

        def keypress(self, size, key):
            key = super().keypress(size, key)
            i = self.edit_pos
            t = self.edit_text
            # line
            if self._command_map[key] == C_TXT_LINE_CLR_L:
                self.edit_text = t[i:]
                self.edit_pos = 0
            elif self._command_map[key] == C_TXT_LINE_CLR_R:
                self.edit_text = t[:i]
            # word
            elif self._command_map[key] == C_TXT_WORD_CLR_L:
                cut_idx = t[:i].rstrip().rfind(' ') + 1
                self.edit_text = t[:cut_idx] + t[i:]
                self.edit_pos = cut_idx
            # char
            elif self._command_map[key] == C_TXT_CHAR_CLR_R:
                self.edit_text = t[:i] + t[i+1:]
            else:
                return key

    def __init__(self, search_caption):
        self.edit_view = PEdit._Edit(caption=search_caption)
        self.visible = False
        super().__init__(uw.AttrMap(self.edit_view, 'highlight'))

        uw.register_signal(self.__class__,
                           [C_SUBMIT,
                            C_CANCEL])

    @property
    def text(self):
        return self.edit_view.edit_text

    @text.setter
    def text(self, value):
        self.edit_view.edit_text = value
        self.edit_view.edit_pos = len(value)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if self._command_map[key] == C_SUBMIT:
            uw.emit_signal(self, C_SUBMIT, self.text)
        elif (self._command_map[key] == C_CANCEL) or \
             (key in ('backspace', 'delete') and not self.text):
            uw.emit_signal(self, C_CANCEL)
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
        c['ctrl u'] = uw.CURSOR_PAGE_UP
        c['ctrl d'] = uw.CURSOR_PAGE_DOWN
        self._command_map = c

    def to_entries(data):
        return [PListBox.Entry(d) for d in data]


class VDivider(uw.SolidFill):
    def __init__(self, fill_char=u'│'):
        super().__init__(fill_char)


class HDivider(uw.Divider):
    def __init__(self, fill_char=u'─'):
        super().__init__(fill_char)
