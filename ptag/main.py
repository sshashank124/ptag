from data.models import db, create_tables
from ui.tui_urwid import ui


def main():
    create_tables()
    db.connect()

    # main
    ui.run()

    db.close()


if __name__ == '__main__':
    main()
