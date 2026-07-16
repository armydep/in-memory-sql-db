QUERY_DELIMITER = ";"
EXIT_COMMANDS = {"exit", "quit"}


def split_complete_queries(buffer: str) -> tuple[list[str], str]:
    parts = buffer.split(QUERY_DELIMITER)
    complete = [part.strip() for part in parts[:-1] if part.strip()]
    return complete, parts[-1]


def is_exit_command(command: str) -> bool:
    return command.strip().lower() in EXIT_COMMANDS
