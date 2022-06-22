from taxonomy4good import SustainabilityTaxonomy, SustainabilityItem
from taxonomy4good import from_file

taxo = from_file("en_master_lexicon")

taxo.print_hierarchy()