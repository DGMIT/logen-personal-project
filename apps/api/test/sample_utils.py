def inc(x: int) -> int:
    return x + 1


def is_same_number(number1: int, number2: int) -> bool:
    return number1 == number2


def is_number_less_than_other(target_number: int, number_list: list[int]):
    for number in number_list:
        if number < target_number:
            return False
    return True


def is_text_in_string_using_in_method(target_text: str, main_string: str) -> bool:
    if target_text in main_string:
        return True
    return False


def is_text_in_string_using_find_method(target_text: str, main_string: str) -> bool:
    if main_string.find(target_text) != -1:
        return True
    return False


def is_min_length(s: str, min_len: int) -> bool:
    if len(s.strip()) >= min_len:
        return True
    return False
