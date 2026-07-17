from memdb.data.table_entry import TableEntry


class DBData:
    def __init__(self):
        self.tables: dict[str, TableEntry] = {}
