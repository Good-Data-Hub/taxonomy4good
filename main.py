from sustainability_taxonomy import SustainabilityItem
from sustainability_taxonomy import from_file

item1 = SustainabilityItem(0, "Demo")
item1.details()

std_tax = from_file("sample.xlsx")

last_items = std_tax.get_level_items(4)
last_items[0].score = 10

last_items[4].score = -3
last_items[4].weight = 2

# root_score = std_tax.compute_scores()
std_tax.print_hierarchy()



