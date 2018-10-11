from data.models import db, create_tables
from ui import tui


def main():
    create_tables()
    db.connect()

    # main
    tui.run()

    db.close()


if __name__ == '__main__':
    main()
