def inc(x: int) -> int:
    return x + 1


def is_same_number(number1: int, number2: int) -> bool:
    return number1 == number2


def is_number_less_than_other(target_number: int, number_list: list[int]):
    for number in number_list:
        if number < target_number:
            return False
    return True
