from gedcom_functions import *
import numpy as np

# Cintron Colon family = F434
# Morales Pacheco Morales family = F2408

# Commands:
# add (family to library)
# remove (family from library)
# view (reduced batches)
  
# Command formats:
# add F2372 (3,3);(4,4);(4,4)
# remove F2372
# view F434

gedcom = GEDCOM('Alvarez Family Tree.ged')
library = CandidatesLibrary()
while True:
  library.command(gedcom)
