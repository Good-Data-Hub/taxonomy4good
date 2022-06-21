class SustainabilityItem:

    # children here must be initialized to None (leaf nodes) by default,
    # or if data was supplied, SustainabilityItems will be created out of those
    # IDs (fetch from file)
    def __init__(self, id, name, level=0, grouping=None, parent=None,
                 score=0, weight=1, children=None, meta_data=None):
        self.id = id
        self.name = name
        self.level = level
        self.grouping = grouping
        self.parent = parent
        self.score = score
        self.weight = weight
        self.children = children
        self.meta_data = meta_data

    def details(self):
        """prints the values of the attributes of the SustainabilityItem object"""

        print(f'name: {self.name}')
        print(f"id: {self.id}")
        print(f"level: {self.level}")

        if self.children is not None:
            printed_children = [child.id for child in self.children]
        else:
            printed_children = None

        print(f"children: {printed_children}")

        if self.parent is not None:
            parent = self.parent.id
        else:
            parent = None

        print(f"parent: {parent}")
        print(f"score: {self.score}")
        print(f"weight: {self.weight}")

        if self.meta_data is None:
            meta_data = {}
        else:
            meta_data = self.meta_data

        print(f"meta_data: {meta_data}")

    def to_dict(self):
        """Converts the SustainabilityItem object to a dictionary

        :returns: the attributes of the SustainabilityItem object
        :rtype: dict
        """

        if self.parent is not None:
            parent_id = self.parent.id
        else:
            parent_id = None

        if self.children is not None:

            children_ids = [child.id for child in self.children]
        else:
            children_ids = None

        return {'id': self.id, 'name': self.name, 'level': self.level,
                'grouping': self.grouping, "parent": parent_id,
                'weight': self.weight, "score": self.score, 'children': children_ids,
                'meta_data': self.meta_data}



