from gedcom_functions import *

gedcom = GEDCOM('Alvarez Family Tree 2022-04-14.ged')

print(gedcom.FID_dict['F902']['MARR'])
# known_grades = gedcom.get_known_grades('F902')
# print(known_grades)
# gedcom.pretty_print_known_grades(known_grades)
# print('---')

library = DispensationLibrary(gedcom)

library.add_dispensa('F902', [(3, 3), (3, 4), (4, 4), (4, 4)])
