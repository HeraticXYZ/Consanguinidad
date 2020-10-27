# Consanguinity analyzer from GEDCOM File
# Fernando Alexander Alvarez-Mercado
# 2020.06.22

class Person:
  def __init__(self, PID, name, FAMC, FAMS, sex):
    self.PID = PID
    self.name = name
    self.FAMC = FAMC
    self.FAMS = FAMS
    self.sex = sex
  def pretty_print(self):
    print(self.PID)
    print(self.name)
    print(self.FAMC)
    print(self.FAMS)
    print(self.sex)

class Family:
  def __init__(self, FID, husband, wife, children, dispensa):
    self.FID = FID
    self.husband = husband
    self.wife = wife
    self.children = children
    self.dispensa = dispensa
  def pretty_print(self):
    print(self.FID)
    print(self.husband)
    print(self.wife)
    print(self.children)
    print(self.dispensa)

class Batches: # generates multiple batches and reduction batch from a single family
  def __init__(self, family, families):
    self.batches = []
    reduction_grades = {"2", "2c3", "3", "3c4", "4"}
    grades = family.dispensa.split(", ")
    token_pairs = []
    for grade in grades: # gen proper batches
      if grade == "0":
        break
      count = 1
      temp_grade = grade
      if "de" in grade: # multiplicity
        temp = grade.split("de")
        count = int(temp[0])
        temp_grade = temp[1]
      pairs = []
      for pair in gen_pairs(family, temp_grade, families): # initial pairs
        if siblinghood(pair, families) == True: # if determined True by tree, removed and count reduced
          count -= 1
        elif siblinghood(pair, families) == None: # removed if False determined by tree
          pairs.append(pair)
      temp_pairs = pairs
      for pair in pairs: # removes pairs with token count greater than true count
        if pairs.count(pair) > count:
          for i in range(pairs.count(pair)):
            temp_pairs.remove(pair)
          token_pairs.append(pair)
      pairs = temp_pairs
      self.batches.append([count, pairs])
      reduction_grades.remove(temp_grade)
    pairs = []
    for grade in reduction_grades: # gen false pairs
      pairs += [pair for pair in gen_pairs(family, grade, families) if siblinghood(pair, families) == None] # only adds pairs indeterminable by tree alone
    pairs += token_pairs # adds pairs rendered false by token method to reduction batch
    self.reduction_batch = [0, pairs] # reduction batch is multiplicity blind
  def pretty_print(self):
    # print(self.batches)
    for batch in self.batches:
      print([batch[0], len(batch[1])])
    print([self.reduction_batch[0], self.reduction_batch[1]])


def fetch_ancestors(root_PID, gens, families): # fetch ancestors specified gens up tree
  old_gen = [root_PID]
  for i in range(gens):
    new_gen = []
    for PID in old_gen:
      parents = [PID+"+0", PID+"+1"] # create extensions if parents unknown
      for family in families:
        if PID in family.children:
          parents[0] = family.wife if family.wife != None else parents[0]
          parents[1] = family.husband if family.husband != None else parents[1]
      new_gen += parents
    old_gen = new_gen
  return old_gen

def cross(list1, list2): # generates list of sets of two unique PIDs from two lists
  pairs = []
  for PID1 in list1:
    for PID2 in list2:
      if PID1 != PID2:
        pairs.append({PID1, PID2})
  return pairs

def gen_pairs(family, grade, families): # grade is a string, gens pairs from grade
  pairs = []
  if "c" in grade: # grades decremented by 1 to search for siblings
    temp_grade = grade.split("c")
    pairs += cross(fetch_ancestors(family.husband, int(temp_grade[0])-1, families), fetch_ancestors(family.wife, int(temp_grade[1])-1, families))
    pairs += cross(fetch_ancestors(family.husband, int(temp_grade[1])-1, families), fetch_ancestors(family.wife, int(temp_grade[0])-1, families)) # reverse
  else:
    pairs += cross(fetch_ancestors(family.husband, int(grade)-1, families), fetch_ancestors(family.wife, int(grade)-1, families))
  return pairs

def siblinghood(pair, families): # returns None if indeterminable
  list_pair = list(pair)
  ret = False
  father1 = None
  father2 = None
  mother1 = None
  mother2 = None
  for family in families:
    if list_pair[0] in family.children:
      father1 = family.husband
      mother1 = family.wife
    if list_pair[1] in family.children:
      father2 = family.husband
      mother2 = family.wife
  if (father1 == father2 and father1 != None) or (mother1 == mother2 and mother1 != None):
    ret = True
  elif (father1 == None or father2 == None) and (mother1 == None or mother2 == None):
    ret = None
  return ret

def batch_names(batch, tree): # converts atomic batch PIDs into names
  named_pairs = []
  for pair in batch[1]:
    list_pair = list(pair)
    for person in tree:
      if person.PID == list_pair[0]:
        list_pair[0] = person.name
      if person.PID == list_pair[1]:
        list_pair[1] = person.name
    named_pairs.append({list_pair[0], list_pair[1]})
  return [batch[0], named_pairs]
    

gedcom_file = open("Cintrón Family Tree.ged", "r")
gedcom = gedcom_file.read()

tree = []
families = []
for chunk in gedcom.split("\n0"):
  chunk = chunk.split("\n")
  PID = None
  name = None
  FAMC = None
  FAMS = []
  sex = None
  if "P" in chunk[0]:
    PID = chunk[0].split("@")[1]
    for line in chunk:
      if "NAME" in line:
        name = line.split(" NAME ")[1]
      if "FAMC" in line:
        FAMC = line.split("@")[-2]
      if "FAMS" in line:
        FAMS.append(line.split("@")[-2])
      if "SEX" in line:
        sex = line.split(" SEX ")[1]
    tree.append(Person(PID, name, FAMC, FAMS, sex))
  FID = None
  husband = None
  wife = None
  children = []
  dispensa = None
  if "F" in chunk[0]:
    FID = chunk[0].split("@")[1]
    for line in chunk:
      if "MARR" in line:
        dispensa = line.split(" MARR ")[1]
      if "HUSB" in line:
        husband = line.split("@")[-2]
      if "WIFE" in line:
        wife = line.split("@")[-2]
      if "CHIL" in line:
        children.append(line.split("@")[-2])
    families.append(Family(FID, husband, wife, children, dispensa))

# print(tree)

"""
for person in tree:
  person.pretty_print()

for family in families:
  family.pretty_print()
"""

# print(fetch_ancestors("P32", 3, families))
"""
test_batch = None
for family in families:
  if family.FID == "F19":
    test_batch = Batches(family, families)

test_batch.pretty_print()
"""

ignored_families = []

batches = []
master_reduction_batch = [0, []]
for family in families:
  if family.dispensa != None and family.dispensa != "" and family.FID not in ignored_families:
    new_batch = Batches(family, families)
    batches += new_batch.batches
    master_reduction_batch[1] += new_batch.reduction_batch[1]

def reduce_batches(batches, reduction_batch):
  reduced_batches = []
  for batch in batches:
    reduced_batches.append([batch[0], [pair for pair in batch[1] if pair not in reduction_batch[1]]])
  return reduced_batches

for batch in reduce_batches(batches, master_reduction_batch):
  print(batch_names(batch, tree))
# print(master_reduction_batch)
