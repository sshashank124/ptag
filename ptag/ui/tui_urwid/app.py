from threading import Timer
import urwid

from . import constants as C
from .list_fragments import TagsFragment, ItemsFragment
from .utils import ContextText, VDivider


class App:
    palette = [(C.PLT_HIGHLIGHT, 'standout,bold', 'default'),
               (C.PLT_INTERACT, 'standout,yellow', 'default'),
               (C.MSG_LVL_INFO, 'standout,dark green', 'default'),
               (C.MSG_LVL_WARN, 'standout,yellow', 'default'),
               (C.MSG_LVL_ERROR, 'standout,dark red', 'default')]

    def __init__(self):
        # COMMANDS
        c = urwid.command_map
        c['h'] = urwid.CURSOR_LEFT
        c['j'] = urwid.CURSOR_DOWN
        c['k'] = urwid.CURSOR_UP
        c['l'] = urwid.CURSOR_RIGHT
        c['esc'] = C.CANCEL

        # UI
        self.tags_fragment = TagsFragment()
        urwid.connect_signal(self.tags_fragment,
                             C.SUBMIT,
                             self.handle_tag_selected)
        urwid.connect_signal(self.tags_fragment,
                             C.MESSAGE,
                             self.handle_message)

        self.items_fragment = ItemsFragment()
        urwid.connect_signal(self.items_fragment,
                             C.MESSAGE,
                             self.handle_message)

        tags_items = [(urwid.WEIGHT, 3, self.tags_fragment),
                      (1, VDivider('┃')),
                      (urwid.WEIGHT, 7, self.items_fragment)]
        self.columns = urwid.Columns(tags_items)

        # TODO: add detailed item view

        self.statusbar = ContextText()
        self.statusbar_styled = urwid.AttrMap(self.statusbar, 'highlight')
        self.set_statusbar_timer()

        self.main_view = urwid.Pile([self.columns])
        self.root_view = self.main_view

    def handle_tag_selected(self, tag):
        self.items_fragment.enter_search(tag.name)
        self.columns.focus_position = 2

    def set_statusbar_visible(self, visible):
        if visible:
            if not self.statusbar.visible:
                self.main_view.contents.append((self.statusbar_styled,
                                               (urwid.PACK, None)))
        elif not visible:
            if self.statusbar.visible:
                self.main_view.contents.pop()
        self.statusbar.visible = visible

    def set_statusbar_timer(self):
        self.statusbar_timer = Timer(C.MSG_DURATION,
                                     self.set_statusbar_visible,
                                     args=[False])

    def handle_message(self, msg_lvl, msg):
        self.statusbar.set(msg_lvl, '{0}: {1}'.format(msg_lvl.upper(), msg))
        self.set_statusbar_visible(True)

        if self.statusbar_timer.is_alive():
            self.statusbar_timer.cancel()

        self.set_statusbar_timer()
        self.statusbar_timer.start()

    def run(self):
        self.loop = urwid.MainLoop(self.root_view,
                                   App.palette,
                                   unhandled_input=App.exit_on_q)
        self.loop.run()

    def exit_on_q(key):
        if key == 'q':
            raise urwid.ExitMainLoop()
