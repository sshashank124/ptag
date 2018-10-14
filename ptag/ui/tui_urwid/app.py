import urwid

from .constants import C_CANCEL, C_SUBMIT
from .list_fragments import TagsFragment, ItemsFragment
from .utils import VDivider


class App:
    palette = [('highlight', 'standout', 'default')]

    def __init__(self):
        # COMMANDS
        c = urwid.command_map
        c['h'] = urwid.CURSOR_LEFT
        c['j'] = urwid.CURSOR_DOWN
        c['k'] = urwid.CURSOR_UP
        c['l'] = urwid.CURSOR_RIGHT
        c['esc'] = C_CANCEL

        # UI
        self.tags_fragment = TagsFragment()
        urwid.connect_signal(self.tags_fragment,
                             C_SUBMIT,
                             self.handle_tag_selected)

        self.items_fragment = ItemsFragment()

        elems = [(urwid.WEIGHT, 3, self.tags_fragment),
                 (1, VDivider()),
                 (urwid.WEIGHT, 7, self.items_fragment)]
        self.root_view = urwid.Columns(elems)

    def handle_tag_selected(self, tag):
        self.items_fragment.enter_search(tag.name)
        self.root_view.focus_position = 2

    def run(self):
        self.loop = urwid.MainLoop(self.root_view,
                                   App.palette,
                                   unhandled_input=App.exit_on_q)
        self.loop.run()

    def exit_on_q(key):
        if key == 'q':
            raise urwid.ExitMainLoop()
