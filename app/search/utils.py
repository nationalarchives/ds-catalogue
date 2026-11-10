import re


def camelcase_to_underscore(name: str) -> str:
    """
    Convert CamelCase or camelCase string to snake_case.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def underscore_to_camelcase(word, lower_first=True):
    """Convert snake_case string to CamelCase or camelCase."""
    result = "".join(char.capitalize() for char in word.split("_"))
    if lower_first:
        result = result[0].lower() + result[1:]
    return result


def quote_if_needed(value: str) -> str:
    """Escape backslashes and double quotes and quote values containing spaces.

    Mirrors server-side quoting used when building advanced-search `q` param.
    """
    if not isinstance(value, str) or not value:
        return value

    safe = value.replace("\\", "\\\\").replace('"', '\\"')
    if " " in safe:
        return f'"{safe}"'
    return safe if safe != value else value
