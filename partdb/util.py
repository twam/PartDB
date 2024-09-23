
def snake_case_to_camel_case(string: str) -> str:
    return ''.join(string.title() for word in string.split('_'))
