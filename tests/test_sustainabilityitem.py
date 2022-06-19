import unittest
import pytest
from sustainability_taxonomy.sustainabilityItem import SustainabilityItem

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

    @pytest.fixture(autouse=True)
    def _pass_fixtures(self, capsys):
        self.capsys = capsys

    def test_print_root_details(self):
        root.details()
        printed_text = self.capsys.readouterr()
        self.assertEqual(root_details, printed_text.out)

    def test_print_item_details(self):
        item1.details()
        printed_text = self.capsys.readouterr()
        self.assertEqual(item1_details, printed_text.out)


if __name__ == '__main__':
    unittest.main()
