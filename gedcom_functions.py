"""Consanguinidad 8.0 functions derived from 7.0 functions 
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
                FAMC = None # child index
                FAMS = [] # spouse index
                GIVN = '' # given name
                SURN = '' # surname
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
                    NAME = GIVN + ' ' + SURN
                    self.PID_dict[PID] = {'FAMC': FAMC, 
                                          'FAMS': FAMS, 
                                          'GIVN': GIVN, 
                                          'SURN': SURN, 
                                          'NAME': NAME}
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
                    self.FID_dict[FID] = {'HUSB': husband, 
                                          'WIFE': wife, 
                                          'CHIL': children, 
                                          'MARR': marriage}
        for family in self.FID_dict:
            husband = self.FID_dict[family]['HUSB']
            husband_name = ''
            if husband != None:
                husband_name = (self.PID_dict[husband]['GIVN'] + ' ' 
                        + self.PID_dict[husband]['SURN'])
            wife = self.FID_dict[family]['WIFE']
            wife_name = ''
            if wife != None:
                wife_name = (self.PID_dict[wife]['GIVN'] + ' ' 
                     + self.PID_dict[wife]['SURN'])
            self.FID_dict[family]['NAME'] = husband_name + ' x ' + wife_name

    def get_parents(self, PID):
        famc = self.PID_dict[PID]['FAMC']
        if famc is None:
            husband = None
            wife = None
        else:
            fam = self.FID_dict[famc]
            husband = fam['HUSB']
            wife = fam['WIFE']
        return husband, wife

    def get_ancestors(self, PID, gens=4):
        # Need to implement a trail for unknown ancestors
        # Trail is a string where 0 represents male and 1 represents female
        ancestors = {0: [(PID, '')]}
        for gen in range(gens):
            ancestors[gen+1] = []
            for indi, trail in ancestors[gen]:
                if trail:
                    ancestors[gen+1].append((indi, trail+'0'))
                    ancestors[gen+1].append((indi, trail+'1'))
                else:
                    father, mother = self.get_parents(indi)
                    if father is None:
                        ancestors[gen+1].append((indi, trail+'0'))
                    else:
                        ancestors[gen+1].append((father, ''))
                    if mother is None:
                        ancestors[gen+1].append((indi, trail+'1'))
                    else:
                        ancestors[gen+1].append((mother, ''))
        return ancestors

    def get_grade_field(self, family):
        # siblinghoods means accessing one generation below shared ancestors
        male_side = self.get_ancestors(self.FID_dict[family]['HUSB'])
        female_side = self.get_ancestors(self.FID_dict[family]['WIFE'])
        grade_field = {
            (male_grade, female_grade):
                [
                    (ancestor1, ancestor2)
                    for ancestor1 in male_side[male_grade-1]
                    for ancestor2 in female_side[female_grade-1]
                ]
            for male_grade in range(2, 5)
            for female_grade in range(2, 5)
        }
        return grade_field

    def get_known_grades(self, grade_field):
        # Returns siblinghood relationships already established in the tree 
        if isinstance(grade_field, str):
            # in case we enter an FID
            grade_field = self.get_grade_field(grade_field)
        known_grades = []
        for grade in grade_field:
            for cand in grade_field[grade]:
                # PIDs not the same, and no trails 
                if (cand[0][0] != cand[1][0]) and not (cand[0][1] or cand[1][1]):
                    # check if the two indis are siblings
                    male_side_famc = self.PID_dict[cand[0][0]]['FAMC']
                    female_side_famc = self.PID_dict[cand[1][0]]['FAMC']
                    if male_side_famc and female_side_famc:
                        if male_side_famc == female_side_famc:
                            known_grades.append((grade, cand))
                        else:
                            # Siblings through only one parent do not share their FAMC
                            male_side_fam = self.FID_dict[male_side_famc]
                            male_side_father = male_side_fam['HUSB']
                            male_side_mother = male_side_fam['WIFE']
                            female_side_fam = self.FID_dict[female_side_famc]
                            female_side_father = female_side_fam['HUSB']
                            female_side_mother = female_side_fam['WIFE']
                            if (male_side_father and female_side_father):
                                if male_side_father == female_side_father:
                                    known_grades.append((grade, cand))
                            if (male_side_mother and female_side_mother):
                                if male_side_mother == female_side_mother:
                                    known_grades.append((grade, cand))
        return known_grades

    def pretty_print_known_grades(self, known_grades):
        new_grades = []
        for grade in known_grades:
            indi1 = grade[1][0][0]
            indi2 = grade[1][1][0]
            indi1_name = self.PID_dict[indi1]['NAME']
            indi2_name = self.PID_dict[indi2]['NAME']
            new_grade = (grade[0], ((indi1_name, grade[1][0][1]), (indi2_name, grade[1][1][1])))
            new_grades.append(new_grade)
        print(new_grades)
        return

    def pretty_print_candidates(self, candidates):
        new_cands = []
        for cand in candidates:
            name1 = self.PID_dict[cand[0][0]]['NAME']
            name2 = self.PID_dict[cand[1][0]]['NAME']
            trail1 = cand[0][1]
            trail2 = cand[1][1]
            new_cand = ((name1, trail1), (name2, trail2))
            new_cands.append(new_cand)
            print(new_cand)
        return

class DispensationLibrary:

    def __init__(self, gedcom):
        self.gedcom = gedcom
        self.batches = {}
        self.elim_batches = {}
        self.reduced_batches = {}

    def _reduce(self):
        # remove elimination candidates from batch candidates
        pass

    def add_dispensa(self, family, grades):
        # grades are in marital format, not exact format
        # 
        grade_field = self.gedcom.get_grade_field(family)
        known_grades = self.gedcom.get_known_grades(grade_field)
        short_grades = grades.copy()
        short_grade_field = grade_field.copy()
        for known_grade, candidate in known_grades:
            adj_known_grade = (known_grade[1], known_grade[0])
            if known_grade in grades:
                short_grades.remove(known_grade)
            elif adj_known_grade in grades:
                short_grades.remove(adj_known_grade)
            else:
                print('Known grades and given grades do not match. Recommended against adding to the library. ')
                return
            short_grade_field[known_grade].remove(candidate)
        batches = [] # format: [[[candidates], tokens], ...]
        elim_batch = [] # format: [candidates]
        for grade in set(short_grades):
            if grade[0] != grade[1]:
                adj_grade = (grade[1], grade[0])
                candidates = short_grade_field[grade] + short_grade_field[adj_grade]
            else:
                candidates = short_grade_field[grade]
            count = short_grades.count(grade)
            batches.append([candidates, count])
        # assemble elimination batch 
        for m in range(2, 5):
            for f in range(2, 5):
                if ((m, f) not in short_grades and (f, m) not in short_grades):
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
