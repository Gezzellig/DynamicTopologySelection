import unittest

from initializer.SetWithCrossProduct import SetWithCrossProduct


class Test_SetWithCrossProduct(unittest.TestCase):
    def test_add_element(self):
        """
        testing the following case
            1
            |
            2
           /|\
          3 4 5
        """
        cross_set = SetWithCrossProduct()
        cross_set.add(frozenset({1}))
        self.assertEqual({frozenset({1})}, cross_set.get())
        cross_set.add(frozenset({1, 2}))
        self.assertEqual({frozenset({1}), frozenset({1, 2})}, cross_set.get())
        cross_set.add(frozenset({1, 2, 3}))
        self.assertEqual({frozenset({1}), frozenset({1, 2}), frozenset({1, 2, 3})}, cross_set.get())
        cross_set.add(frozenset({1, 2, 4}))
        self.assertEqual({frozenset({1}), frozenset({1, 2}), frozenset({1, 2, 3}), frozenset({1, 2, 4}), frozenset({1, 2, 3, 4})}, cross_set.get())
        cross_set.add(frozenset({1, 2, 5}))
        self.assertEqual({frozenset({1}), frozenset({1, 2}), frozenset({1, 2, 3}), frozenset({1, 2, 4}), frozenset({1, 2, 3, 4}), frozenset({1, 2, 5}), frozenset({1, 2, 3, 5}), frozenset({1, 2, 4, 5}), frozenset({1, 2, 3, 4, 5})}, cross_set.get())
