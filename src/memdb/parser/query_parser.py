from memdb.commands.base import QueryInterface


class QueryParser:
    def parse(self, query_str: str) -> QueryInterface:
        """
        1. split query str into list of tokens (with trimming head and tail each one)
        2. switch case on first token:
         case SELECT:
           RETURN select_query
         case CREATE:
           RETURN create_table_query
         case UPDATE:
           RETURN update_query
         case INSERT:
           RETURN insert_query
         case DELETE:
           RETURN delete_query
         case DROP:
           RETURN drop_table_query
         case DESCRIBE:
           RETURN describe_table_query
        :param query_str:
        :return:
        """
        raise NotImplementedError
