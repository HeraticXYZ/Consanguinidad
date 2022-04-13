# employing cousinhoods

from gedcom_functions import *
import numpy as np

gedcom = GEDCOM('Alvarez Family Tree.ged')

# Cintron Colon family = F434
# Morales Pacheco Morales family = F2408
"""
target_family = 'F434'
print('Families for:', gedcom.get_names(target_family))
relevant_families = gedcom.get_relevant_families(target_family)


print()
print('Generation 3')
for fam_cand in relevant_families:
  # \"""
  if fam_cand[1] != 3:
    continue
  marriage = gedcom.get_marriage(fam_cand[0])
  if marriage == '':
    continue
  # \"""
  famid = fam_cand[0]
  print()
  print(famid, '=', gedcom.get_names(famid))
  print()
  print(gedcom.get_marriage(famid))
  # print()
  # print('Known grades:', gedcom.get_known_grades(gedcom.get_grade_field(famid)))
  print()
  gedcom.print_ancestors(famid)
  print()
  print('-' * 80)
"""

# Add family to library
# Remove family from library
# Return reduced batches
  
# Command formats:
# add F2372 (3,3);(4,4);(4,4) (leave a space at the end if no grade)
# remove F2372
# view F434

library = CandidatesLibrary()

while True:
  library.command(gedcom)

"""
grade_field = gedcom.get_grade_field('F2372')
for grade, candidate_list in grade_field.items():
  print(grade)
  for candidate in candidate_list:
    print(gedcom.get_name(candidate[0][0]), "|", gedcom.get_name(candidate[1][0]))

# gedcom.print_ancestors('F2372')
known_grades = gedcom.get_known_grades(grade_field)
print(known_grades)
grades = [(3,3), (4,4), (4,4)]

library.add_dispensa('F2372', grade_field, grades, known_grades)
library.print_reduced_batches(gedcom)
"""

