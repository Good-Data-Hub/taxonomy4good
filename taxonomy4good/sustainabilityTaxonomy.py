from .errors import IDNotFoundError, EmptyTaxonomyError, FileTypeNotSupportedError
from .sustainabilityItem import SustainabilityItem
import pandas as pd
import numpy as np
import ast
import json
import os

BUILTIN_TAXONOMIES = ["eu_taxonomy", "ftse_fsgi", "un_sdg", "world_bank_taxonomy",
                      "china_taxonomy", "esg_taxonomy", "en_master_lexicon"]

TAXONOMIES_DESC = {"eu_taxonomy": "EU Taxonomy",
                   "ftse_fsgi": "FTSE for Social Good Index",
                   "un_sdg": "UN SDGs",
                   "world_bank_taxonomy": "World Bank Taxonomy",
                   "china_taxonomy": "China Taxonomy",
                   "esg_taxonomy": "ESG Taxonomy",
                   "en_master_lexicon": "Full Sustainability Lexicon"}


class SustainabilityTaxonomy:
    """This object is used to create different taxonomies based on required
    standards. Be it for internal reporting or external, various combinations of
    sustainability related words can be created by grouping those words under
    different categories (words), allowing for the creation of multiple reporting
    items with the needed granularity.

    Feel free to play around with the provided Sustainability Lexicon to create
    your own Taxonomy and make sure you are not missing any word.
    """

    def __init__(self, root=None,
                 version_name='Standard Taxonomy',
                 version_num='0.1.0'):
        if root is None:

            # default: ESG Taxonomy
            full_lexicon = from_file(filepath="esg_taxonomy",
                                     version_name=TAXONOMIES_DESC["esg_taxonomy"],
                                     version_num=version_num,
                                     filetype='excel',
                                     meta=True)
            self.root = full_lexicon.root
            self.version_name = full_lexicon.version_name
            self.version_num = full_lexicon.version_num
        else:
            self.root = root
            self.version_name = version_name
            self.version_num = version_num

    def insert_items(self, items):
        """ Insert additional items (terms/lexicons) to this existing taxonomy4good

        :param items: terms to add in the taxonomy4good with their respective information
        :type items: list of SustainabilityItem
        """
        if items is not None:

            # make sure input is treated as a list
            if not isinstance(items, list):
                items = [items]

            # get parents and ids of all items to be inserted
            parent_ids = [item.parent.id for item in items]

            parent_ids = list(set(parent_ids))
            # get parent items from ids
            parents = np.array(self.search_by_id(parent_ids))

            for item in items:
                idx = np.where(parents == item.parent)[0][0]

                # if parent has no children, create a list with the respective child
                if parents[idx].children is None:
                    parents[idx].children = [item]
                else:
                    parents[idx].children.append(item)

    # TODO: fix big in remove function
    def remove_subtree(self, items=None):
        """Remove the passed items along with their children from the taxonomy4good

        :param items: the items of subtrees/substructures to be removed
        :type items: list of SustainabilityItems
        """

        if not isinstance(items, list) and not isinstance(items, np.ndarray):
            items = [items]
        # every supplied item
        for item in items:

            # if item is not a leaf node, perform this function on children first
            if item.children is not None:
                self.remove_subtree(item.children)

            # update the parent item
            if item.parent is not None:
                item.parent.children.remove(item)

            del item

    def remove_by_id(self, ids):
        """Remove from the taxonomy4good items corresponding to the supplied ids

        :param ids: ids corresponding to the items to be removed from the taxonomy4good
        :type ids: int | list of int
        """

        # get items corresponding to the ids
        items = self.search_by_id(ids)

        # remove items from taxonomy4good
        self.remove_subtree(items)

    def get_items_each_level(self, start_root=None):
        """Get lists of items for each level of the taxonomy4good (grouped by level)

        :param start_root: starting node of subtree (default: root of taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: SustainabilityItem list for each level
        :rtype: numpy array
        """

        # if no root is specified, set the root of the taxonomy4good as starting root
        if start_root is None:
            start_root = self.root

        # these will help iterate over the levels of the taxonomy4good
        current_level = 0
        current_items = np.array([start_root])
        items = []
        next_level_items = np.array([])

        # while we did not reach the final level
        while current_level < self.level(start_root):
            next_level_items = np.array([])

            for ci in current_items:
                # specify next level items if current item is not leaf item
                if ci.children is not None:
                    next_level_items = np.concatenate([next_level_items, ci.children])

            # update the state of the iteration step and update the current items to list
            items.append(np.array([ci for ci in current_items]))
            current_level += 1
            current_items = next_level_items

        return np.array(items, dtype=object)

    def get_level_items(self, level):
        """Get items of the specified level

        :param level: desired level of the taxonomy4good we wish to extract items from
        :type level: int
        :returns: list of items in the specified level
        :rtype: numpy array
        """

        return self.get_items_each_level(self.root)[level]

    def get_items(self, start_root=None):
        """Get all the items of the structure

        :param start_root: root item of the desired structure or substructure we wish
                           to get items from (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: all the items of the taxonomy4good
        :rtype: np array (SustainabilityItem)
        """

        # if no root is specified, set the root of the taxonomy4good as starting root
        if start_root is None:
            if self.root is None:
                return np.array([])
            start_root = self.root

        return np.concatenate(self.get_items_each_level(start_root))

    def get_terms(self, start_root=None):
        """Get all terms (names/lexicon) in the taxonomy4good

        :param start_root: root item of the desired structure or substructure we wish
                           to get terms from (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: all the terms of the taxonomy4good
        :rtype: np array (str)
        """

        # extract all items first, then return the name attributes
        items = self.get_items(start_root)
        return [item.name for item in items]

    def get_all_ids(self, start_root=None):
        """Get ids of all the nodes in the current taxonomy4good (grouped by level)

        :param start_root: root item of the desired structure or substructure we wish
                           to get ids from (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: all the terms of the taxonomy4good
        :rtype: np array (int)
        """

        # if no root is specified, set the root of the taxonomy4good as starting root
        if start_root is None:
            start_root = self.root
        items = self.get_items_each_level(start_root)
        ids = []
        for level in range(len(items)):
            ids.append([item.id for item in items[level]])

        return np.array(ids, dtype=object)

    def search_by_id(self, ids):
        """Search for items by their id

        :param ids: list of ids of the nodes to look for
        :type ids: list int
        :returns: items having the supplied ids
        :rtype: list of SustainabilityItem objects
        """
        if isinstance(ids, int):
            ids = [ids]
        # get the ids of current taxonomy4good nodes
        node_ids = np.concatenate(self.get_all_ids().flatten())

        # check if all ids exist in the taxonomy4good
        if not set(ids).issubset(node_ids):
            raise IDNotFoundError(f"{set(ids).difference(node_ids)}"
                                  + " not found in the Taxonomy")

        # get all items in taxonomy4good
        sustainability_items = self.get_items()

        # get items with the corresponding ids
        idx = np.concatenate([np.where(node_ids == id) for id in ids])

        return list(sustainability_items[[idx]].flatten())

    def level(self, start_item=None):
        """ Compute the maximum depth/level of the taxonomy4good

        :param start_item: root item of the desired structure or substructure we wish
                           to compute the depth/level
        :type start_item: SustainabilityItem
        :returns: level of the taxonomy4good
        :rtype: int
        """

        if self.root is None:
            return 0

        if start_item is None:
            start_item = self.root

        # if root has no children, number of levels is 1
        if start_item.children is None:
            return 1

        # if current item has children, get level of children subtrees
        for item in start_item.children:
            lvl = self.level(item) + 1

        # get the maximum level of children subtrees and add 1 for current root
        return max(lvl) if isinstance(lvl, list) else lvl

    def to_csv(self, filepath, start_root=None):
        """Save current taxonomy4good/substructure to a csv file

        :param filepath: path where to save the resulting file
        :type filepath: str
        :param start_root: root item of the structure or substructure to be saved as
                          csv (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        """
        if start_root is None:
            start_root = self.root

        items_df = self.to_dataframe(start_root)
        items_df.to_csv(f"{filepath}.csv")

    def to_excel(self, filepath, start_root=None):
        """Save current taxonomy4good/substructure to an Excel file

        :param filepath: path where to save the resulting file
        :type filepath: str
        :param start_root: root item of the structure or substructure to be saved as
                          Excel (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        """

        if start_root is None:
            start_root = self.root

        items_df = self.to_dataframe(start_root)
        items_df.to_excel(f"{filepath}.xlsx")

    def items_to_json(self, filepath, start_root=None):
        """Save current taxonomy4good/substructure items to a JSON file (records structure)

        :param filepath: path where to save the resulting file
        :type filepath: str
        :param start_root: root item of the structure or substructure to be saved as
                          JSON (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        """

        # If no substructure root is specified, take the root of the overall structure
        if start_root is None:
            start_root = self.root

        items_df = self.to_dataframe(start_root)
        items_df.to_json(f"{filepath}.json", orient='records')

    def taxonomy_to_json(self, filepath, start_root=None):
        """Save current taxonomy4good/substructure items to a JSON file (hierarchical structure)

        :param filepath: path where to save the resulting file
        :type filepath: str
        :param start_root: root item of the structure or substructure to be saved as
                          JSON (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        """

        if start_root is None:
            start_root = self.root
        # convert the current taxonomy4good to a dictionary
        taxonomy_dict = self.taxonomy_to_dict(start_root)

        # save resulting dictionary to a json file
        with open(f"{filepath}.json", "w") as f:
            json.dump(taxonomy_dict, f, indent=4)

    def print_hierarchy(self, start_item=None, current_level=0, islast=False):
        """Print the current hierarchy of the taxonomy4good with the respective values

        :param start_item: starting root of the taxonomy4good/substructure we wish
                            to start from
        :type start_item: SustainabilityItem
        :param current_level: indicating the current level that is being printed
        :type current_level: int
        :param islast: indicating of item is last in the list of children
        :type islast: bool
        """

        # if taxonomy4good is empty, raise error
        if self.root is None:
            raise EmptyTaxonomyError("Taxonomy is empty")

        else:
            # if not substructure root is specified, use the entire taxonomy4good
            if start_item is None:
                start_item = self.root

            self.compute_scores(start_item, False)
            # print root
            if current_level == 0:
                print(f"{start_item.name} : {start_item.score}")
                print("│\n│")
            else:

                # specify the printing structure according to current level
                if current_level == 1:
                    if islast:
                        sep = "└"
                    else:
                        sep = "├"
                    print(sep + "─────" + str(start_item.name) + " : " + str(start_item.score))
                else:
                    if islast:
                        s = " "
                    else:
                        s = "│"
                    print(s + (current_level - 1) * "       " + "└───── " + str(start_item.name)
                          + " : " + str(start_item.score))

            # update level status
            current_level += 1
            if start_item.children is not None:
                for idx in range(len(start_item.children)):
                    if current_level == 1 and idx == len(start_item.children) - 1:
                        islast = True

                    # run function again on children by passing level status
                    self.print_hierarchy(start_item.children[idx], current_level, islast)

    def get_level_scores(self, level):
        """Compute the weighted values/scores for the specified level

        :param level: taxonomy4good level
        :type level: int
        :returns: names of level items and their respective weighted values
        :rtype: dict
        """

        # compute scores for the entire taxonomy4good (bottom up)
        self.compute_scores(self.root, False)

        # get items in the specified level
        level_items = self.get_level_items(level)

        # create the desired data structure (item name : value)
        level_scores = {item.name: item.score for item in level_items}

        return level_scores

    def compute_scores(self, start_root=None, root_score=True):
        """Compute the weighted scores for the entire taxonomy4good

        :param root_score: decide whether to return the score of the root, default is true
        :type root_score: bool
        :param start_root: root of taxonomy4good/substructure for which we want to compute
                            the score (default: root of the entire taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: the weighted value/score of the root node (start_root)
        :rtype: float
        """
        # compute the weighted scores from the attributes up to the root
        score = 0
        if start_root is None:
            if self.root is None:
                raise EmptyTaxonomyError("Taxonomy is empty")

            # otherwise set start root as the root of the overall taxonomy4good
            start_root = self.root

        # return weighted score if current item is leaf node
        if start_root.children is None:
            return start_root.score * start_root.weight

        # compute the weighted score for all the children of current item
        for child in start_root.children:
            score += self.compute_scores(child)

        # update the value by the current weighted value
        start_root.score = score
        if root_score:
            return score

    def summary(self):
        """Print the general information about the entire taxonomy4good"""

        if self.root is None:
            print("The taxonomy4good is empty")
        else:
            print(f"Number of Sustainability items: {self.get_items().size}")
            root_score = self.compute_scores(self.root, True)
            print(f"Overall weighted score: {root_score}")
            print(f"Number of levels : {self.level()}")

            if self.root.children is not None:
                top_level_name = [child.name for child in self.root.children]
                print(f"Top level items are {top_level_name}")
                print(f"Top level items scores: {[item.score for item in self.root.children]}")

    def to_dataframe(self, start_root=None):
        """Convert the entire taxonomy4good to a DataFrame

        :param start_root: the root item of the taxonomy4good/substructure to be converted
                          to a DataFrame (default: root of the overall taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: a dataframe version of the taxonomy4good
        :rtype: pd.DataFrame"""

        if start_root is None:
            start_root = self.root

        # convert taxonomy4good to a dictionary first
        items = self.items_to_dict(start_root)
        return pd.DataFrame(items)

    def similar_items(self, sustainability_items):
        """Gives the items under the same parent

        :param sustainability_items: list of items which items under the same parent
                                     are returned
        :type sustainability_items: list of SustainabilityItem
        :returns: list of child items under the parents of the specified items
        :rtype: list of SustainabilityItem lists"""

        # if input is a single item, return directly the children of its parent
        if not isinstance(sustainability_items, list):
            return sustainability_items.parent.children

        # check if the items have a parent (check if items are not roots)
        sustainability_items = [item for item in sustainability_items
                                if item.parent is not None]

        # get parent items
        parents = [item.parent for item in sustainability_items]
        parents = list(set(parents))

        # get the children from the resulting parents
        similar_items = [p.children for p in parents]

        return similar_items

    def similar_items_byid(self, ids):
        """Gives the items under the same parent as items having the specified ids

        :param ids: list of ids which items under the same parent of the items having
                    the specified ids are returned
        :type ids: list of int
        :returns: list of child items under the parents of the specified items
        :rtype: list of SustainabilityItem lists"""

        sustainability_items = self.search_by_id(ids)
        if len(sustainability_items) == 1:
            sustainability_items = sustainability_items[0]
        return self.similar_items(sustainability_items)

    def search_items_by_name(self, terms, start_root=None):
        """Look for similar SustainabilityItems using a string partial match

        :param terms: list of terms/names to search for
        :type terms: list of str
        :param start_root: the root item of the taxonomy4good/substructured to be searched
                          from (default: root of the overall taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: items having the name attributes partially similar to terms
        :rtype: numpy array of SustainabilityItems
        """

        if start_root is None:
            start_root = self.root

        if not isinstance(terms, list):
            terms = [terms]

        # get all items start from start_root
        items = self.get_items(start_root)
        items_found = []

        # check if terms are substrings of the name attribute in terms
        for term in terms:
            items_found.append([item for item in items
                                if term.lower() in item.name.lower()])

        if len(items_found) == 1:
            items_found = sum(items_found, [])
        return items_found

    def search_similar_names(self, terms, start_root=None):
        """Search for similar names/terms in the taxonomy4good using a string partial match

        :param terms: list of terms/names to search for
        :type terms: list of str
        :param start_root: the root item of the taxonomy4good/substructured to be searched
                          from (default: root of the overall taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: terms partially similar to terms
        :rtype: numpy array of str
        """
        if start_root is None:
            start_root = self.root

        if not isinstance(terms, list):
            terms = [terms]
        # get all items start from start_root
        items = self.get_items(start_root)
        items_found = []

        # check if terms are substrings of the name attribute in terms
        for term in terms:
            items_found.append([item.name for item in items
                                if term.lower() in item.name.lower()])

        if len(items_found) == 1:
            items_found = sum(items_found, [])

        return items_found

    def items_to_dict(self, start_root=None):
        """Convert the entire taxonomy4good to a dictionary (records) starting from start_root

        :param start_root: the root item of the taxonomy4good/substructured of which items
                          are to be converted to dictionary (default: root of the
                          overall taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: list of dictionary converted items (records)
        :rtype: list of dict
        """
        if start_root is None:
            start_root = self.root

        # get all items in the taxonomy4good starting from start_root
        sustainability_items = self.get_items(start_root)

        # convert each item to a dictionary
        dict_items = [item.to_dict() for item in sustainability_items]
        return dict_items

    def taxonomy_to_dict(self, start_root=None):
        """Convert the entire taxonomy4good to a dictionary (structural hierarchy)
        starting from start_root

        :param start_root: the root item of the taxonomy4good/substructured to be converted
                          to dictionary (default: root of the overall taxonomy4good)
        :type start_root: SustainabilityItem
        :returns: dictionary version of the taxonomy4good
        :rtype: dict
        """
        if start_root is None:
            start_root = self.root

        if start_root.children is None:
            return [start_root.to_dict()]

        # this makes sure to avoid unnecessary [] if there is only a single child
        if len(start_root.children) == 1:
            dict_builder = self.taxonomy_to_dict(start_root.children[0])
        else:
            dict_builder = [self.taxonomy_to_dict(child) for child in start_root.children]

        root_dict = start_root.to_dict()
        root_dict['children'] = [dict_builder] if isinstance(dict_builder, dict) else dict_builder

        return root_dict


def from_file(filepath, version_name="Standard Taxonomy", version_num="0.1.0", filetype='excel', meta=False):
    root = SustainabilityItem(id=0, name=version_name)

    if filetype == 'excel':
        if filepath in BUILTIN_TAXONOMIES:
            root.name = TAXONOMIES_DESC[filepath]
            items_df = pd.read_excel(os.path.dirname(os.path.abspath(__file__)) + "/taxonomies/" + filepath + ".xlsx")
            version_name = TAXONOMIES_DESC[filepath]
        else:
            items_df = pd.read_excel(filepath)
    elif filetype == 'json':
        items_df = pd.read_json(filepath)
    else:
        raise FileTypeNotSupportedError(f"{filetype} is currently not supported")

    items_df.replace({np.nan: None}, inplace=True)

    items = [root]

    all_columns = items_df.columns
    meta_data_col = [col for col in all_columns
                     if col not in ["id", "name", "level", "grouping",
                                    "parent", "score", "weight", "children"]]

    # create sustainability items
    for item in items_df.to_dict('records'):
        # create item
        if meta:
            meta_dict = {key: item[key] for key in meta_data_col}
        else:
            meta_dict = {}

        sustainability_item = SustainabilityItem(id=item['id'],
                                                 name=item['name'],
                                                 level=item['level'],
                                                 grouping=item['grouping'],
                                                 parent=item['parent'],
                                                 score=item['score'],
                                                 weight=item['weight'],
                                                 children=item['children'],
                                                 meta_data=meta_dict)

        # if parent is not None, update parent value with SustainabilityItem
        # Update parent children
        if item['parent'] is not None:
            parent = items[int(item['parent'])]

            sustainability_item.parent = parent
            if not isinstance(parent.children, list):
                parent.children = ast.literal_eval(parent.children)

            # print(f"parent: {parent.id}")
            for i in range(len(parent.children)):
                # print(f"current child: {parent.children[i]}")
                if sustainability_item.id == parent.children[i]:
                    child_idx = i

            parent.children[child_idx] = sustainability_item

        else:
            if items[0].children is None:
                items[0].children = []
            items[0].children.append(sustainability_item)
            sustainability_item.parent = items[0]

        items.append(sustainability_item)

    return SustainabilityTaxonomy(items[0], version_name, version_num)
