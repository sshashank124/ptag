from data.models import db, create_tables
from ui.tui_urwid.app import App


def main():
    create_tables()
    db.connect()

    # main
    app = App()
    app.run()

    db.close()


if __name__ == '__main__':
    main()
