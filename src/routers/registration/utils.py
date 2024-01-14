async def is_cyrillic(string: str):
    alpha = "йцукенгшщзхъфывапролджэячсмитьбю`ё"
    # Remove spaces from the string
    string_without_spaces = "".join(char for char in string if char != " ").lower()

    return all(char in alpha for char in string_without_spaces)
