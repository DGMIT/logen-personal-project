import pytest
import sample_utils
from fastapi import HTTPException


def test_numbers_are_equal():
    assert sample_utils.is_same_number(1, 1) == True


def test_numbers_are_not_equal() -> None:
    assert sample_utils.is_same_number(1, 2) != True


class TestIsGreaterOrLesser:
    target_number = 0
    dummy_int_list = [1, 2, 3, 4, 6]

    def test_base_number_is_less_than_all(self):
        assert (
            sample_utils.is_number_less_than_other(
                self.target_number, self.dummy_int_list
            )
            == True
        )

    def test_base_number_is_not_greater_than_all(self):
        assert (
            sample_utils.is_number_less_than_other(
                self.target_number, self.dummy_int_list
            )
            != False
        )


def test_target_text_in_string_using_in_method():
    target_text = "Hi"
    main_string = "Hi I'm geonwoo"
    assert sample_utils.is_text_in_string_using_in_method(target_text, main_string)


def test_target_text_in_string_using_find_method():
    target_text = "Hi"
    main_string = "Hi I'm geonwoo"
    assert sample_utils.is_text_in_string_using_find_method(target_text, main_string)


class TestInspectStringLenGroup:
    min_length = 3
    two_len_example = "12"
    three_len_example = "123"
    four_len_example = "1234"
    five_len_example = "12345"
    six_len_example = "123456"
    left_gap_example = " 56"
    right_gap_example = "56 "
    side_gap_example = " 6 "
    inner_gap_example = "3 4"

    def test_returns_false_when_input_is_shorter_than_min_length(self):
        assert (
            sample_utils.is_min_length(self.two_len_example, self.min_length) == False
        )

    def test_returns_true_when_input_equals_min_length(self):
        assert (
            sample_utils.is_min_length(self.three_len_example, self.min_length) == True
        )

    def test_returns_true_when_input_exceeds_min_length(self):
        assert (
            sample_utils.is_min_length(self.four_len_example, self.min_length) == True
        )

    def test_returns_false_when_input_starts_with_whitespace(self):
        assert (
            sample_utils.is_min_length(self.left_gap_example, self.min_length) == False
        )

    def test_returns_false_when_input_ends_with_whitespace(self):
        assert (
            sample_utils.is_min_length(self.right_gap_example, self.min_length) == False
        )

    def test_returns_true_when_input_has_inner_whitespace(self):
        assert (
            sample_utils.is_min_length(self.inner_gap_example, self.min_length) == True
        )


class TestCommonErrorCases:
    # 1. ValueError
    # 어떤 함수에 음수를 넣었을 때 ValueError가 발생해야 한다.
    def test_raise_value_error(self):
        with pytest.raises(ValueError):
            sample_utils.raise_value_error_function()

    # 2. TypeError
    # 숫자가 들어가야 할 자리에 문자열을 넣었을 때 TypeError가 발생해야 한다.
    def test_raise_type_error(self):
        with pytest.raises(TypeError):
            sample_utils.raise_type_error_function()

    # 3. ZeroDivisionError
    # 0으로 나누려고 할 때 ZeroDivisionError가 발생해야 한다
    def test_raise_zero_division_error(self):
        with pytest.raises(ZeroDivisionError):
            sample_utils.raise_zero_division__error_function()

    # 4. KeyError
    # 딕셔너리에 없는 키를 조회할 때 KeyError가 발생해야 한다.
    def test_raise_key_error(self):
        with pytest.raises(KeyError):
            sample_utils.raise_key_error_function()

    # 5. IndexError
    # 리스트의 존재하지 않는 인덱스를 조회할 때 IndexError가 발생해야 한다.
    def test_raise_index_error(self):
        with pytest.raises(IndexError):
            sample_utils.raise_index_error_function()

    # 6. AttributeError
    # 존재하지 않는 속성에 접근할 때 AttributeError가 발생해야 한다.
    def test_raise_attribute_error(self):
        with pytest.raises(AttributeError):
            sample_utils.raise_attribute_error_function()

    # 7. FileNotFoundError
    # 존재하지 않는 파일을 열려고 할 때 FileNotFoundError가 발생해야 한다.
    def test_raise_file_not_found_error(self):
        with pytest.raises(FileNotFoundError):
            sample_utils.raise_file_not_found_error_function()

    # 8. AssertionError
    # assert 조건이 거짓일 때 AssertionError가 발생해야 한다.
    def test_raise_assertion_error(self):
        with pytest.raises(AssertionError):
            sample_utils.raise_assertion_error_function()

    # 9. HTTPException (FastAPI)
    # 인증 없이 보호된 라우터에 접근할 때 HTTPException (401 또는 403)이 발생해야 한다.
    def test_raise_htttpexception_error(self):
        with pytest.raises(HTTPException):
            sample_utils.raise_httpexception_error_function()
