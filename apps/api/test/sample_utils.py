from fastapi import HTTPException


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


def raise_value_error_function():
    raise ValueError("ValueError 에러 발생")


def raise_type_error_function():
    raise TypeError("TypeError 에러 발생")


def raise_zero_division__error_function():
    raise ZeroDivisionError("ZeroDivisionError 에러 발생")


def raise_key_error_function():
    raise KeyError("KeyError 에러 발생")


def raise_index_error_function():
    raise IndexError("IndexError 에러 발생")


def raise_attribute_error_function():
    raise AttributeError("AttributeError 에러 발생")


def raise_file_not_found_error_function():
    raise FileNotFoundError("FileNotFoundError 에러 발생")


def raise_assertion_error_function():
    raise AssertionError("AssertionError 에러 발생")


def raise_httpexception_error_function():
    raise HTTPException(status_code=400, detail="400")
