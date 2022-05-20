"""
Consanguinidad 7.0 functions

PIDs are of the form P3, P644, F1203, etc. and are the primary indices used for function calls.

Reworking GEDCOM __init__ to build library with everything the analysis needs to run.
"""

class GEDCOM:
  def __init__(self, file_name):
    with open(file_name, 'r') as gedcom_file:
      self.gedcom = gedcom_file.read()
    self.PID_dict = {}
    self.FID_dict = {}
    for chunk0 in self.gedcom.split('\n0'):
      if 'INDI' in chunk0:
        PID = chunk0.split('@')[1]
        FAMC = None
        FAMS = []
        GIVN = ''
        SURN = ''
        for chunk1 in chunk0.split('\n1'):
          if 'FAMC' in chunk1:
            FAMC = chunk1.split('@')[1]
          if 'FAMS' in chunk1:
            FAMS.append(chunk1.split('@')[1])
          if 'NAME' in chunk1:
            for chunk2 in chunk1.split('\n2'):
              if 'GIVN' in chunk2:
                GIVN = chunk2.split('GIVN ')[1]
              if 'SURN' in chunk2:
                SURN = chunk2.split('SURN ')[1]
        self.PID_dict[PID] = {'FAMC': FAMC, 
                              'FAMS': FAMS, 
                              'GIVN': GIVN, 
                              'SURN': SURN}
      if 'FAM' in chunk0:
        FID = chunk0.split('@')[1]
        husband = None
        wife = None
        children = []
        marriage = None
        for chunk1 in chunk0.split('\n1'):
          if 'HUSB' in chunk1:
            husband = chunk1.split('@')[1]
          if 'WIFE' in chunk1:
            wife = chunk1.split('@')[1]
          if 'CHIL' in chunk1:
            children.append(chunk1.split('@')[1])
          if 'MARR ' in chunk1: # no marriage = no space after MARR
            marriage = chunk1.split('\n2')[0].split('MARR ')[1]
        self.FID_dict[FID] = {'husband': husband, 
                              'wife': wife, 
                              'children': children, 
                              'marriage': marriage}
    for family in self.FID_dict:
      husband = self.FID_dict[family]['husband']
      husband_name = ''
      if husband != None:
        husband_name = (self.PID_dict[husband]['GIVN'] + ' ' 
                        + self.PID_dict[husband]['SURN'])
      wife = self.FID_dict[family]['wife']
      wife_name = ''
      if wife != None:
        wife_name = (self.PID_dict[wife]['GIVN'] + ' ' 
                     + self.PID_dict[wife]['SURN'])
      self.FID_dict[family]['names'] = husband_name + ' x ' + wife_name

  def get_ancestors(self, root_PID):
    # trail format: 0 = male, 1 = female
    ancestors = {1: [(root_PID, '')]}
    for grade in range(2, 5):
      ancestors[grade] = []
      for PID, trail in ancestors[grade-1]:
        if trail == '':
          FAMC = self.PID_dict[PID]['FAMC']
          if FAMC != None:
            husband = self.FID_dict[FAMC]['husband']
            wife = self.FID_dict[FAMC]['wife']
            if husband != None:
              ancestors[grade].append((husband, ''))
            else:
              ancestors[grade].append((PID, '0'))
            if wife != None:
              ancestors[grade].append((wife, ''))
            else:
              ancestors[grade].append((PID, '1'))
          else:
            ancestors[grade].append((PID, '0'))
            ancestors[grade].append((PID, '1'))
        else:
          ancestors[grade].append((PID, trail+'0'))
          ancestors[grade].append((PID, trail+'1'))
    return ancestors

  def get_grade_field(self, family):
    # cross each side together to get full candidates
    grade_field = {}
    male_side = self.get_ancestors(self.FID_dict[family]['husband'])
    female_side = self.get_ancestors(self.FID_dict[family]['wife'])
    for male_grade in range(2, 5):
      for female_grade in range(2, 5):
        grade_field[(male_grade, female_grade)] = []
        for ancestor1 in male_side[male_grade]:
          for ancestor2 in female_side[female_grade]:
            grade_field[(male_grade, female_grade)].append((ancestor1, ancestor2))
    return grade_field

  def get_known_grades(self, grade_field):
    known_grades = [] # (grade, candidate)
    for grade in grade_field:
      for candidate in grade_field[grade]:
        if candidate[0][0] != candidate[1][0]:
          male_side_FAMC = self.PID_dict[candidate[0][0]]['FAMC']
          female_side_FAMC = self.PID_dict[candidate[1][0]]['FAMC']
          if (male_side_FAMC != None 
              and female_side_FAMC != None):
            if male_side_FAMC == female_side_FAMC:
              known_grades.append((grade, candidate))
            else:
              male_side_father = self.FID_dict[male_side_FAMC]['husband']
              male_side_mother = self.FID_dict[male_side_FAMC]['wife']
              female_side_father = self.FID_dict[female_side_FAMC]['husband']
              female_side_mother = self.FID_dict[female_side_FAMC]['wife']
              if (male_side_father != None 
                  and male_side_father == female_side_father):
                known_grades.append((grade, candidate))
              if (male_side_mother != None 
                  and male_side_mother == female_side_mother):
                known_grades.append((grade, candidate))
    return known_grades
      

class CandidatesLibrary:
  def __init__(self):
    # self.library = {} # {FAMID: (grade_field, grades), ...}
    # each family results in a batch, which is reduced by the negation batch
    self.batches = {} # {FAMID: [batches]}
    self.elim_batches = {} # list of negated candidates from each family
    self.reduced_batches = {} # produced using elimination batch

  def _reduce(self):
    self.reduced_batches = {}
    for family, batches in self.batches.items(): # go through batches
      reduced_batches = []
      for batch, tokens in batches: # go through each batch of a family
        reduced_candidates = []
        elim_families = []
        for candidate in batch:
          if (candidate[0][0] != candidate[1][0] 
              and batch.count(candidate) <= tokens):
            # non-sibling relationship elimination; token-count elimination
            candidate_found = False
            for elim_family, elim_batch in self.elim_batches.items():
              if candidate in elim_batch:
                # search for candidate in elim_batches
                candidate_found = True
                elim_families.append(elim_family)
            if not candidate_found:
              # reduction step
              reduced_candidates.append(candidate)
        if reduced_candidates == []:
          print('Contradiction! Source family:', family, 
                'Elimination families:', elim_families)
        reduced_batches.append((reduced_candidates, tokens, elim_families))
      self.reduced_batches[family] = reduced_batches

  def add_dispensa(self, family, grade_field, known_grades, grades):
    short_grades = grades.copy()
    short_grade_field = grade_field.copy()
    for grade, candidate in known_grades:
      real_grade = grade
      if grade[0] > grade[1]:
        grade = (grade[1], grade[0])
      if grade not in short_grades:
        print('Contradiction!', family, 'given grades and known grades do not match!', 
              family, 'was not added to library.')
        return
      short_grade_field[real_grade].remove(candidate)
      short_grades.remove(grade)
    batches = [] # format: [([candidates], tokens), ...]
    elim_batch = [] # format: [candidates]
    if short_grades != []:
      for grade in set(short_grades):
        count = short_grades.count(grade)
        if grade[0] != grade[1]:
          igrade = (grade[1], grade[0])
          batches.append((short_grade_field[grade] + short_grade_field[igrade], count))
        else:
          batches.append((short_grade_field[grade], count))
    for m in range(2, 5):
      for f in range(2, 5):
        if ((m, f) not in short_grades 
            and (f, m) not in short_grades):
          elim_batch += short_grade_field[(m, f)]
    self.batches[family] = batches
    self.elim_batches[family] = elim_batch
    self._reduce()

  def remove_dispensa(self, family):
    if family in self.batches:
      self.batches.pop(family)
      self.elim_batches.pop(family)
      self._reduce()
    else:
      print(family, 'not in library.')
