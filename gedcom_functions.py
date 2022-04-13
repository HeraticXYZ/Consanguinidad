"""
Consanguinidad 6.0 functions

PIDs and family IDs are of the form P3, P644, F1203, etc. and are the primary indices used for function calls.
"""

class GEDCOM:
  def __init__(self, file_name):
    with open(file_name, "r") as gedcom_file:
      self.gedcom = gedcom_file.read()

  def get_keys(self, PID):
    # returns FAMS# and FAMC#
    FAMS = None
    FAMC = None
    for chunk in self.gedcom.split('\n0'):
      if PID+'@ INDI' in chunk:
        for line in chunk.split('\n'):
          if 'FAMS' in line:
            FAMS = line.split('@')[-2]
          if 'FAMC' in line:
            FAMC = line.split('@')[-2]
    return [FAMS, FAMC]
  
  def get_children(self, family):
    children = [] # list of PIDs
    for chunk in self.gedcom.split('\n0'):
      if family+'@ FAM' in chunk:
        for line in chunk.split('\n'):
          if 'CHIL' in line:
            children.append(line.split('@')[-2])
    return children
  
  def get_spouses(self, family):
    wife = None
    husband = None
    for chunk in self.gedcom.split('\n0'):
      if family+'@ FAM' in chunk:
        for line in chunk.split('\n'):
          if 'WIFE' in line:
            wife = line.split('@')[1]
          if 'HUSB' in line:
            husband = line.split('@')[1]
    return [wife, husband]

  def get_name(self, PID):
    name = ''
    for chunk in self.gedcom.split('\n0'):
      if PID+'@ INDI' in chunk:
        for line in chunk.split('\n'):
          if 'NAME' in line:
            name = line.split('NAME ')[1]
    return name

  def get_names(self, family):
    spouses = self.get_spouses(family)
    wife = self.get_name(spouses[0]) if spouses[0] != None else ''
    husband = self.get_name(spouses[1]) if spouses[1] != None else ''
    return husband + ' x ' + wife

  def get_marriage(self, family):
    text = '' # marriage text
    for chunk in self.gedcom.split('\n0'):
      if family+'@ FAM' in chunk:
        for line in chunk.split('\n'):
          if 'MARR ' in line: # no marriage = no space after MARR
            text = line.split('MARR ')[1]
    return text

  def get_relevant_families(self, family):
    # crawls down from a family to all descendant marriages within range, set to 3
    relevant_families = [] # refers to FAMSIDs
    cur_gen = [family] # refers to FAMSIDs
    i = 1
    for gen in range(3):
      new_gen = [] # FSIDs of children of given FSIDs
      for fam in cur_gen:
        children = [] # their FAMSIDs
        for PID in self.get_children(fam):
          child = self.get_keys(PID)[0]
          if child != None:
            children.append(child)
            if self.get_marriage(child) != None:
              relevant_families.append((child, i))
        new_gen += children
      cur_gen = new_gen
      i += 1
      print('gen', gen+1, 'done')
    return relevant_families

  def get_ancestors(self, PID):
    # employing siblinghoods = grade shifted down by 1
    ancestors = {1: [(PID, '')]}
    for grade in range(2, 5):
      ancestors[grade] = []
      for person in ancestors[grade-1]:
        if person[1] == '':
          FAMC = self.get_keys(person[0])[1]
          if FAMC != None:
            parents = self.get_spouses(FAMC)
            if parents[0] != None:
              ancestors[grade].append((parents[0], ''))
            else:
              ancestors[grade].append((person[0], '0'))
            if parents[1] != None:
              ancestors[grade].append((parents[1], ''))
            else:
              ancestors[grade].append((person[0], '1'))
          else:
            ancestors[grade].append((person[0], '0'))
            ancestors[grade].append((person[0], '1'))
        else:
          ancestors[grade].append((person[0], person[1]+'0'))
          ancestors[grade].append((person[0], person[1]+'1'))
    return ancestors

  def print_ancestors(self, family, gen=4):
    # reverse female-male order to male-female order for readability
    female_side = self.get_ancestors(self.get_spouses(family)[0])
    male_side = self.get_ancestors(self.get_spouses(family)[1])
    m_list = male_side[gen][::-1]
    f_list = female_side[gen][::-1]
    for i in range(2**(gen-1)):
      m_names = self.get_name(m_list[i][0]) + ' ' + str(m_list[i][1])
      f_names = self.get_name(f_list[i][0]) + ' ' + str(f_list[i][1])
      print(m_names.ljust(50), '|', f_names.ljust(50))
  
  def get_grade_field(self, family):
    # cross each side together to get full candidates
    # candidate format: ((FAMID, offset), (FAMID, offset))
    # {(g, g): [((FAMID, offset), (FAMID, offset)), ...], (g, g): [...], ...}
    # number of tokens = (2 ^ offset1) * (2 ^ offset2)
    female_side = self.get_ancestors(self.get_spouses(family)[0])
    male_side = self.get_ancestors(self.get_spouses(family)[1])
    
    grade_field = {}
    for female_grade in range(2, 5):
      for male_grade in range(2, 5):
        grade_field[(female_grade, male_grade)] = []
        for person1 in female_side[female_grade]:
          for person2 in male_side[male_grade]:
            grade_field[(female_grade, male_grade)].append((person1, person2))

    return grade_field

  def get_known_grades(self, grade_field):
    known_grades = [] # (grade, candidate)
    for grade in grade_field:
      for candidate in grade_field[grade]:
        if candidate[0][0] != candidate[1][0]:
          female_side_FAMC = self.get_keys(candidate[0][0])[1]
          male_side_FAMC = self.get_keys(candidate[1][0])[1]
          if (female_side_FAMC != None 
              and male_side_FAMC != None):
            if female_side_FAMC == male_side_FAMC:
              known_grades.append((grade, candidate))
            else:
              female_side_parents = self.get_spouses(female_side_FAMC)
              male_side_parents = self.get_spouses(male_side_FAMC)
              if (female_side_parents[0] != None 
                  and female_side_parents[0] == male_side_parents[0]):
                known_grades.append((grade, candidate))
              if (female_side_parents[1] != None 
                  and female_side_parents[1] == male_side_parents[1]):
                known_grades.append((grade, candidate))
    return known_grades

class CandidatesLibrary:
  def __init__(self):
    # each family results in a batch, which is reduced by the negation batch
    self.batches = {} # {FAMID: [batches]}
    self.elim_batches = {} # list of negated candidates from each family
    self.reduced_batches = {} # produced using elimination batch

  def __reduce(self):
    # builds reduced_batches
    self.reduced_batches = {}
    for family, batches in self.batches.items(): # go through batches
      reduced_batches = []
      for batch in batches: # go through each batch of a family
        reduced_candidates = []
        elim_families = []
        for candidate in batch[0]:
          if (candidate[0][0] != candidate[1][0] 
              and batch[0].count(candidate) <= batch[1]):
            candidate_found = False
            for elim_family, elim_batch in self.elim_batches.items():
              if candidate in elim_batch:
                candidate_found = True
                elim_families.append(elim_family)
            if not candidate_found:
              reduced_candidates.append(candidate)
        if reduced_candidates == []:
          print('Contradiction! Source family:', family, 
                'Elimination families:', elim_families)
        reduced_batches.append((reduced_candidates, batch[1], elim_families))
      self.reduced_batches[family] = reduced_batches

  def add_dispensa(self, family, grade_field, grades, known_grades):
    short_grades = grades.copy()
    short_grade_field = grade_field.copy()
    for pair in known_grades:
      if pair[0] not in short_grades:
        print('Contradiction!', family, 'given grades and known grades do not match!')
        return -1
      short_grade_field[pair[0]].remove(pair[1])
      if pair[0][0] <= pair[0][1]:
        short_grades.remove(pair[0])
      else:
        short_grades.remove((pair[0][1], pair[0][0]))

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
    
    for f in range(2, 5):
      for m in range(2, 5):
        if ((f, m) not in short_grades 
            and (m, f) not in short_grades):
          elim_batch += short_grade_field[(f, m)]
    
    self.batches[family] = batches
    self.elim_batches[family] = elim_batch
    self.__reduce()
    
  def remove_dispensa(self, family):
    self.batches.pop(family)
    self.elim_batches.pop(family)
    self.__reduce()

  def get_reduced_batches(self):
    # returns raw reduced batches in ascending order of size
    return sorted(list(self.reduced_batches.values()), key=lambda b:len(b[0]))

  def print_reduced_batches(self, gedcom):
    for family, reduced_batches in self.reduced_batches.items():
      print()
      print('Source:', family)
      print()
      for batch in reduced_batches:
        print('Token count:', batch[1])
        for cand in batch[0]:
          first = gedcom.get_name(cand[0][0]) + ' ' + str(cand[0][1])
          second = gedcom.get_name(cand[1][0]) + ' ' + str(cand[1][1])
          print(first.ljust(50), '><', second.ljust(50))
        print()
      print('-' * 100)

  def command(self, gedcom):
    args = ['']
    while args == ['']:
      args = input('Enter command: ').split(' ')
    command = args[0]
    if command == 'add':
      family = args[1]
      grade_field = gedcom.get_grade_field(family)
      if (len(args) > 2 
          and args[-1] != ''):
        grades = [(int(s[1]), int(s[-2])) for s in args[2].split(';')]
      else:
        grades = []
      known_grades = gedcom.get_known_grades(grade_field)
      self.add_dispensa(family, grade_field, grades, known_grades)
    if command == 'remove':
      family = args[1]
      self.remove_dispensa(family)
    if command == 'view':
      self.print_reduced_batches(gedcom)
    if command == 'exit':
      return 0
    return -1
