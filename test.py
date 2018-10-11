import urwid


class FocusableText(urwid.Text):
    _selectable = True

    def keypress(self, _, key):
        return key


palette = [('header', 'white', 'black'),
           ('reveal focus', 'black', 'dark cyan', 'standout')]

items = [FocusableText("foo"),
         FocusableText("bar"),
         FocusableText("baz")]

content = urwid.SimpleListWalker([
    urwid.AttrMap(w, None, 'reveal focus') for w in items])

listbox = urwid.ListBox(content)

show_key = urwid.Text("Press any key", wrap='clip')
head = urwid.AttrMap(show_key, 'header')
top = urwid.Frame(listbox, head)


def exit_on_cr(input):
    if input in ('q', 'Q'):
        raise urwid.ExitMainLoop()


def out(s):
    show_key.set_text(str(s))


loop = urwid.MainLoop(top,
                      palette,
                      unhandled_input=exit_on_cr)
loop.run()
