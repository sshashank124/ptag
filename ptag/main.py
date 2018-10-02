from models import db, create_tables
from query import Query


def main():
    # init ++++++++
    # models
    create_tables()
    db.connect()
    # init --------

    # main ++++++++
    q = Query()
    if q.parse(input("Query: ")):
        print(q.expr)
        print(q.execute())
    # main --------

    # exit ++++++++
    db.close()
    # exit --------


if __name__ == '__main__':
    main()
