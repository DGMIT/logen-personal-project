import sample_utils


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
