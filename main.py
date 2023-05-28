from gedcom_functions import *

gedcom = GEDCOM('Alvarez Family Tree 2022-04-14.ged')

library = DispensationLibrary(gedcom)
library.add_dispensa('F902', [(3, 3), (3, 4), (4, 4), (4, 4)])

descendants = gedcom.get_relevant_descendants('F434')
print('Relevant descendants of', gedcom.FID_dict['F434']['NAME'])
print()
gedcom.pretty_print_descendants(descendants)
