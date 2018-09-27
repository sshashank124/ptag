from models import Tag, Item
from models import db, create_tables


def main():
    # init ++++++++
    # models
    create_tables()
    db.connect()
    # init --------

    # main ++++++++
    for tag in Tag.get_all():
        print(tag, list(tag.get_items()))

    print()

    for item in Item.get_all():
        print(item, list(item.get_tags()))
    # main --------

    # exit ++++++++
    db.close()
    # exit --------


if __name__ == '__main__':
    main()
