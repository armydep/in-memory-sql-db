from memdb.data.table import Table


class DBData:
    def __init__(self):
        self.tables: dict[str, Table] = {}
