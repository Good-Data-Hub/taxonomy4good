from taxonomy4good.sustainabilityTaxonomy import SustainabilityTaxonomy, from_file
from taxonomy4good.sustainabilityItem import SustainabilityItem
from taxonomy4good.errors import IDNotFoundError, EmptyTaxonomyError, FileTypeNotSupportedError
import unittest

test_taxonomy = from_file("sample.xlsx")


def update_score_and_weight():
    ol_item = test_taxonomy.search_by_id(4)[0]
    ol_item.score = 10
    ol_item.weight = 0.1
    ap_item = test_taxonomy.search_by_id(3)[0]
    ap_item.score = 5
    ap_item.weight = 0.3
    qc_item = test_taxonomy.search_by_id(17)[0]
    qc_item.score = 20
    qc_item.weight = 0.5


class TestTaxonomy(unittest.TestCase):
    def test_insertion(self):
        parent = test_taxonomy.search_by_id(1)[0]
        test_taxonomy.insert_items(SustainabilityItem(24, "New Item", parent=parent))
        self.assertEqual(len(parent.children), 4)

    def test_removal_byitem(self):
        parent = test_taxonomy.search_by_id(1)[0]
        added_item = SustainabilityItem(24, "New Item", parent=parent)
        test_taxonomy.insert_items(added_item)
        test_taxonomy.remove_subtree(added_item)
        self.assertEqual(len(parent.children), 3)
        print(test_taxonomy.root.children)

    def test_removal_byid(self):
        parent = test_taxonomy.search_by_id(1)[0]
        added_item = SustainabilityItem(24, "New Item", parent=parent)
        test_taxonomy.insert_items(added_item)
        test_taxonomy.remove_by_id(24)

        with self.subTest():
            self.assertEqual(len(parent.children), 3)

        with self.assertRaises(IDNotFoundError) as context:
            test_taxonomy.search_by_id(30)
        self.assertTrue(context.exception)

    def test_items_each_level(self):
        grouped_by_level = test_taxonomy.get_items_each_level()
        with self.subTest():
            self.assertEqual(len(grouped_by_level[1]), 2)
        with self.subTest():
            self.assertEqual(len(grouped_by_level[3]), 16)

    def test_return_items_bylevel(self):
        level1_items = test_taxonomy.get_level_items(1)
        level3_items = test_taxonomy.get_level_items(3)

        with self.subTest():
            self.assertEqual(len(level1_items), 2)
        with self.subTest():
            self.assertEqual(len(level3_items), 16)

    def test_return_all_items(self):
        all_items = test_taxonomy.get_items()
        env_item = test_taxonomy.search_by_id(1)[0]
        environment_items = test_taxonomy.get_items(env_item)

        with self.subTest():
            self.assertEqual(len(all_items), 24)
        with self.subTest():
            self.assertEqual(len(environment_items), 12)

    def test_get_terms(self):
        terms = test_taxonomy.get_terms()

        with self.subTest():
            self.assertEqual(terms[1], "Environment")

        social_item = test_taxonomy.search_by_id(13)[0]
        social_terms = test_taxonomy.get_terms(social_item)

        with self.subTest():
            self.assertEqual(social_terms[0], "Social")

    def test_get_allids(self):

        ids = sum(test_taxonomy.get_all_ids(), [])
        ids.sort()
        list_ids = [*range(24)]
        with self.subTest():
            self.assertEqual(ids, list_ids)

        social_item = test_taxonomy.search_by_id(13)[0]
        social_ids = sum(test_taxonomy.get_all_ids(social_item), [])
        social_ids.sort()
        social_ids_range = [*range(13, 24)]

        with self.subTest():
            self.assertEqual(social_ids, social_ids_range)

        donation_item = test_taxonomy.search_by_id(22)[0]
        donation_id = test_taxonomy.get_all_ids(donation_item)

        with self.subTest():
            self.assertEqual(donation_id[0], 22)

    def test_search_byid(self):

        with self.assertRaises(IDNotFoundError) as context:
            test_taxonomy.search_by_id(30)
        self.assertTrue(context.exception)

        expected_terms = ["Environment", "Social", "Stakeholder relations"]
        items = test_taxonomy.search_by_id([1, 13, 20])
        terms = [item.name for item in items]
        with self.subTest():
            self.assertEqual(expected_terms, terms)

        singe_term = "COP26"
        item = test_taxonomy.search_by_id(9)[0]
        with self.subTest():
            self.assertEqual(singe_term, item.name)

    def test_compute_level(self):
        with self.subTest():
            self.assertEqual(test_taxonomy.level(), 4)

        air_quality_item = test_taxonomy.search_by_id(2)[0]
        with self.subTest():
            self.assertEqual(test_taxonomy.level(air_quality_item), 2)

        leaf_item = test_taxonomy.search_by_id(11)[0]
        with self.subTest():
            self.assertEqual(test_taxonomy.level(leaf_item), 1)

    def test_level_score(self):
        update_score_and_weight()
        level1_scores = test_taxonomy.get_level_scores(1)
        expected = {"Environment": 2.5, "Social": 10}

        with self.subTest():
            self.assertDictEqual(expected, level1_scores)

    def test_score(self):

        update_score_and_weight()
        score = test_taxonomy.compute_scores()

        with self.subTest():
            self.assertEqual(score, 12.5)

        items = test_taxonomy.search_by_id([1, 13])
        chosen_scores = [item.score for item in items]
        with self.subTest():
            self.assertEqual(chosen_scores, [2.5, 10])

    def test_convert_dataframe(self):
        taxonomy_df = test_taxonomy.to_dataframe()
        with self.subTest():
            self.assertEqual(taxonomy_df.shape[0], 24)

        env_item = test_taxonomy.search_by_id(1)[0]
        env_df = test_taxonomy.to_dataframe(env_item)
        with self.subTest():
            self.assertEqual(env_df.shape[0], 12)

    def test_similar_items(self):
        items = test_taxonomy.search_by_id([21, 11])
        similar_items = test_taxonomy.similar_items(items)
        print(similar_items)
        self.assertEqual(len(similar_items), 2)

    def test_similar_items_byid(self):
        similar_items = test_taxonomy.similar_items_byid([11])
        print([s.name for s in similar_items])
        self.assertEqual(len(similar_items), 2)

    def test_items_by_name(self):
        items = test_taxonomy.search_items_by_name(["climate", "impact"])

        with self.subTest():
            self.assertEqual(len(items[0]), 3)

        with self.subTest():
            self.assertEqual(len(items[1]), 2)

    def test_similar_names(self):
        similar = test_taxonomy.search_similar_names(["climate"])
        with self.subTest():
            self.assertEqual(len(similar), 3)

        similar = test_taxonomy.search_similar_names(["climate", "impact"])
        with self.subTest():
            self.assertEqual(len(similar), 2)

    def test_convert_items_todict(self):
        items_dict = test_taxonomy.items_to_dict()
        with self.subTest():
            self.assertEqual(len(items_dict), 24)

        env_item = test_taxonomy.search_by_id(1)[0]
        subitems_dict = test_taxonomy.items_to_dict(env_item)
        print(subitems_dict)
        with self.subTest():
            self.assertEqual(len(subitems_dict), 12)

    def test_convert_structure_todict(self):
        struct_dict = test_taxonomy.taxonomy_to_dict()
        print(struct_dict)

        env_item = test_taxonomy.search_items_by_name("Environment")[0]
        substruct_dict = test_taxonomy.taxonomy_to_dict(env_item)
        print(substruct_dict)

    def test_print_empty_taxonomy(self):
        # If we create SustainabilityTaxonomy with a null root directly, it will
        # attempt to create the taxonomy4good from the full lexicon by default
        root = SustainabilityItem(0, "test root")
        taxonomy = SustainabilityTaxonomy(root)
        taxonomy.root = None

        with self.assertRaises(EmptyTaxonomyError) as context:
            taxonomy.print_hierarchy()
        self.assertTrue(context.exception)

    def test_from_unsupported_file(self):
        with self.assertRaises(FileTypeNotSupportedError) as context:
            taxonomy = from_file("test_file", filetype="csv")

        self.assertTrue(context.exception)


if __name__ == '__main__':
    unittest.main()
