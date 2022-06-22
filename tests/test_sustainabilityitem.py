import unittest
import pytest
from taxonomy4good.sustainabilityItem import SustainabilityItem

root = SustainabilityItem(0, "root")
item1 = SustainabilityItem(1, "item1", level=1, parent=root)
item2 = SustainabilityItem(2, "item2", level=1, parent=root)
root.children = [item1, item2]

root_dict = {'id': 0, 'name': "root", 'level': 0,
             'grouping': None, "parent": None,
             'weight': 1, "score": 0, 'children': [1, 2],
             'meta_data': None}

item1_dict = {'id': 1, 'name': "item1", 'level': 1,
              'grouping': None, "parent": 0,
              'weight': 1, "score": 0, 'children': None,
              'meta_data': None}

root_details = "name: root\nid: 0\nlevel: 0\nchildren: [1, 2]\nparent: None\nscore: 0\nweight: 1\nmeta_data: {}\n"

item1_details = "name: item1\nid: 1\nlevel: 1\nchildren: None\nparent: 0\nscore: 0\nweight: 1\nmeta_data: {}\n"


class TestItems(unittest.TestCase):
    def test_root_dict(self):
        self.assertEqual(root.to_dict(), root_dict)

    def test_item_dict(self):
        self.assertEqual(item1.to_dict(), item1_dict)

    def test_update_score(self):
        with self.subTest():
            self.assertEqual(item1.score, 0)

        item1.score = 2
        with self.subTest():
            self.assertEqual(item1.score, 2)

    def test_weight_update(self):
        with self.subTest():
            self.assertEqual(item1.weight, 1)

        item1.weight = 0.10
        with self.subTest():
            self.assertEqual(item1.weight, 0.10)


if __name__ == '__main__':
    unittest.main()
