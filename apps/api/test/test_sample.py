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
