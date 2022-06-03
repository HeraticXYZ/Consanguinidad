import os
import re
import pickle
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from gedcom_functions import *

"""Root Window"""

root = Tk()
root.title('Consanguinidad Analyser')
root.geometry('600x400')

"""Menu Bar"""

class FileMenu(Menu):

  def __init__(self, parent):
    super().__init__(parent, tearoff=False)
    self.add_command(
      label='Import GEDCOM...', 
      command=self.open_gedcom,
    )
    self.add_command(
      label='Open workspace...',
      command=self.open_workspace,
    )
    self.add_separator()
    self.add_command(
      label='Save workspace',
      command=self.save_workspace,
    )
    self.add_separator()
    self.add_command(
      label='Exit',
      command=root.destroy,
    )

  def open_gedcom(self):
    file_name = filedialog.askopenfilename(initialdir=__file__)
    if len(file_name) == 0:
      return
    global gedcom
    global gedcom_name
    gedcom = GEDCOM(file_name)
    gedcom_name = os.path.split(file_name)[1]
    gedcom_label_text.set('GEDCOM: ' + gedcom_name)
    print('GEDCOM imported successfully!')
    left_frame.pack(fill='x', expand=True, side='left', padx=5)
    right_frame.pack(fill='x', expand=True, side='right', padx=5)

  def open_workspace(self):
    global gedcom
    global gedcom_name
    with filedialog.askopenfile(mode='rb') as load_file:
      gedcom = pickle.load(load_file)
      gedcom_name = pickle.load(load_file)
      libraries_frame.libraries = pickle.load(load_file)
    gedcom_label_text.set('GEDCOM: ' + gedcom_name)
    libraries_frame.libraries_list = list(libraries_frame.libraries.keys())
    libraries_frame.libraries_field.set(libraries_frame.libraries_list)
    left_frame.pack(fill='x', expand=True, side='left', padx=5)
    right_frame.pack(fill='x', expand=True, side='right', padx=5)

  def save_workspace(self):
    with filedialog.asksaveasfile(mode='wb') as save_file:
      pickle.dump(gedcom, save_file)
      pickle.dump(gedcom_name, save_file)
      pickle.dump(libraries_frame.libraries, save_file)

menubar = Menu(root)
file_menu = FileMenu(menubar)
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

"""GEDCOM Label"""

gedcom_label_text = StringVar(value='Import a GEDCOM or save file to get started.\n')

gedcom_label = ttk.Label(root, textvariable=gedcom_label_text)
gedcom_label.pack(expand=True)

"""Main Frames"""

left_frame = ttk.Frame(root)
right_frame = ttk.Frame(root)

"""Libraries LabelFrame"""

def get_reduced_batches(library):
  batches = {}
  for family, family_batches in library.reduced_batches.items():
    family_batch_index = ord('a')
    for batch in family_batches:
      batch_name = family + chr(family_batch_index)
      batches[batch_name] = batch
      family_batch_index += 1
  return batches

class LibrariesFrame(ttk.LabelFrame):
  
  def __init__(self, parent, text):
    super().__init__(parent, text=text)
    self.cur_library = None
    self.libraries_list = []
    self.libraries_field = StringVar(value=[])
    self.libraries = {} # maps name of library to library object

    self.listbox = Listbox(self, listvariable=self.libraries_field, height=5)
    self.listbox.pack(fill='x')

    self.buttons_frame1 = ttk.Frame(self)
    self.buttons_frame1.pack(fill='x')

    self.buttons_frame2 = ttk.Frame(self)
    self.buttons_frame2.pack(fill='x')
    
    self.create_button = ttk.Button(self.buttons_frame1, text='Create', command=lambda:self.name_library(self.create_library))
    self.create_button.pack(expand=True, side='left')

    self.delete_button = ttk.Button(self.buttons_frame1, text='Delete', command=self.delete_library)
    self.delete_button.pack(expand=True, side='right')

    self.rename_button = ttk.Button(self.buttons_frame2, text='Rename', command=lambda:self.name_library(self.rename_library))
    self.rename_button.pack(expand=True, side='left')

    self.open_button = ttk.Button(self.buttons_frame2, text='Open', command=self.open_library)
    self.open_button.pack(expand=True, side='right')
  
  def name_library(self, action):
    if action == self.rename_library:
      if len(self.listbox.curselection()) == 0:
        print('No library selected!')
        return
    self.name_window = Toplevel()
    self.name_window.title('Create Library')
  
    self.new_name_frame = ttk.LabelFrame(self.name_window, text='Name')
    self.new_name_frame.pack()
    self.new_name_entry = ttk.Entry(self.new_name_frame)
    self.new_name_entry.pack()

    self.accept_button = ttk.Button(self.name_window, text='Accept', command=action)
    self.accept_button.pack(side='left')

    self.cancel_button = ttk.Button(self.name_window, text='Cancel', command=self.name_window.destroy)
    self.cancel_button.pack(side='right')

    self.name_window.wait_visibility()
    self.name_window.grab_set_global()

  def create_library(self):
    new_name = self.new_name_entry.get()
    if new_name == '':
      print('Type a name!')
      return
    self.libraries[new_name] = CandidatesLibrary()
    self.libraries_list.append(new_name)
    self.libraries_field.set(self.libraries_list)
    self.name_window.destroy()

  def rename_library(self):
    new_name = self.new_name_entry.get()
    if new_name == '':
      print('Type a name!')
      return
    cur_library_index = self.listbox.curselection()[0]
    library_name = self.libraries_list[cur_library_index]
    self.libraries[new_name] = self.libraries[library_name]
    self.libraries.pop(library_name)
    self.libraries_list.pop(cur_library_index)
    self.libraries_list.insert(cur_library_index, new_name)
    self.libraries_field.set(self.libraries_list)
    self.name_window.destroy()

  def delete_library(self):
    if len(self.listbox.curselection()) == 0:
      print('No library selected!')
      return
    self.cur_library = None
    cur_library_index = self.listbox.curselection()[0]
    del self.libraries[self.libraries_list[cur_library_index]]
    self.libraries_list.pop(cur_library_index)
    self.libraries_field.set(self.libraries_list)
    batches_frame.clear()
    candidates_frame.clear()

  def open_library(self):
    if len(self.listbox.curselection()) == 0:
      print('No library selected!')
      return
    cur_library_index = self.listbox.curselection()[0]
    cur_library_name = self.libraries_list[cur_library_index]
    cur_library = self.libraries[cur_library_name]
    self.cur_library = cur_library
    batches = get_reduced_batches(cur_library)
    batches_frame.library_name.set(cur_library_name)
    batches_frame.set_batches(batches)

libraries_frame = LibrariesFrame(left_frame, text='Libraries')
libraries_frame.pack(fill='x')

"""Search LabelFrame"""

class SearchFrame(ttk.LabelFrame):

  def __init__(self, parent, text):
    super().__init__(parent, text=text)
    self.cur_family = None
    self.entry_field = StringVar()
    self.families = [] # [ (FID, names), (FID, names), ... ]
    self.results_field = StringVar(value=[])

    self.entry = ttk.Entry(self, textvariable=self.entry_field)
    self.entry.bind('<Return>', self.family_search)
    self.entry.pack(fill='x')

    self.listbox = Listbox(self, listvariable=self.results_field, height=8)
    self.listbox.pack(fill='x')

    self.add_button = ttk.Button(self, text='Add Family', command=self.select_grades)
    self.add_button.pack(expand=True, side='left')

    self.remove_button = ttk.Button(self, text='Remove Family', command=self.remove_family)
    self.remove_button.pack(expand=True, side='right')

  def family_search(self, event):
    self.families = []
    text = self.entry_field.get()
    for family, values in gedcom.FID_dict.items():
      if (text in family) or (text in values['names']):
        self.families.append((family, values['names']))
    self.results_field.set(self.families)

  def select_grades(self):
    if len(self.listbox.curselection()) == 0:
      print('No family selected!')
      return
    if libraries_frame.cur_library is None:
      print('No library open!')
      return
    self.add_window = Toplevel()
    self.add_window.title('Select grades')

    self.cur_family = self.families[self.listbox.curselection()[0]][0]
    marriage_text = gedcom.FID_dict[self.cur_family]['marriage']
    self.marriage_text_frame = ttk.LabelFrame(self.add_window, text='Marriage description')
    self.marriage_text_frame.pack()
    self.marriage_text_label = ttk.Label(self.marriage_text_frame, text=marriage_text)
    self.marriage_text_label.pack()
    
    self.grade_entry_frame = ttk.Frame(self.add_window)
    self.grade_entry_frame.pack()
    self.buttons_frame = ttk.Frame(self.add_window)
    self.buttons_frame.pack()
    
    self.grades_label = ttk.Label(self.grade_entry_frame, text='Grades')
    self.grades_label.grid(column=0, row=0, ipadx=7)
    self.grade_label_2 = ttk.Label(self.grade_entry_frame, text='2°')
    self.grade_label_2.grid(column=0, row=1, ipadx=5)
    self.grade_label_2c3 = ttk.Label(self.grade_entry_frame, text='2° con 3°')
    self.grade_label_2c3.grid(column=0, row=2, ipadx=5)
    self.grade_label_3 = ttk.Label(self.grade_entry_frame, text='3°')
    self.grade_label_3.grid(column=0, row=3, ipadx=5)
    self.grade_label_3c4 = ttk.Label(self.grade_entry_frame, text='3° con 4°')
    self.grade_label_3c4.grid(column=0, row=4, ipadx=5)
    self.grade_label_4 = ttk.Label(self.grade_entry_frame, text='4°')
    self.grade_label_4.grid(column=0, row=5, ipadx=5)

    self.quantity_label = ttk.Label(self.grade_entry_frame, text='Quantity')
    self.quantity_label.grid(column=1, row=0, sticky=EW)
    self.grade_quantity_2 = StringVar(value='0')
    self.grade_entry_2 = ttk.Entry(self.grade_entry_frame, textvariable=self.grade_quantity_2, width=5)
    self.grade_entry_2.grid(column=1, row=1, sticky=EW)
    self.grade_quantity_2c3 = StringVar(value='0')
    self.grade_entry_2c3 = ttk.Entry(self.grade_entry_frame, textvariable=self.grade_quantity_2c3, width=5)
    self.grade_entry_2c3.grid(column=1, row=2, sticky=EW)
    self.grade_quantity_3 = StringVar(value='0')
    self.grade_entry_3 = ttk.Entry(self.grade_entry_frame, textvariable=self.grade_quantity_3, width=5)
    self.grade_entry_3.grid(column=1, row=3, sticky=EW)
    self.grade_quantity_3c4 = StringVar(value='0')
    self.grade_entry_3c4 = ttk.Entry(self.grade_entry_frame, textvariable=self.grade_quantity_3c4, width=5)
    self.grade_entry_3c4.grid(column=1, row=4, sticky=EW)
    self.grade_quantity_4 = StringVar(value='0')
    self.grade_entry_4 = ttk.Entry(self.grade_entry_frame, textvariable=self.grade_quantity_4, width=5)
    self.grade_entry_4.grid(column=1, row=5, sticky=EW)
    
    self.accept_button = ttk.Button(self.buttons_frame, text='Accept', command=self.add_family)
    self.accept_button.pack(side='left')

    self.cancel_button = ttk.Button(self.buttons_frame, text='Cancel', command=self.add_window.destroy)
    self.cancel_button.pack(side='right')
    
    self.add_window.wait_visibility()
    self.add_window.grab_set_global()

  def add_family(self):
    grades = []
    try:
      for i in range(int(self.grade_quantity_2.get())):
        grades.append((2,2))
      for i in range(int(self.grade_quantity_2c3.get())):
        grades.append((2,3))
      for i in range(int(self.grade_quantity_3.get())):
        grades.append((3,3))
      for i in range(int(self.grade_quantity_3c4.get())):
        grades.append((3,4))
      for i in range(int(self.grade_quantity_4.get())):
        grades.append((4,4))
    except:
      print('Grade quantities must be positive integers!')
      return
    grade_field = gedcom.get_grade_field(self.cur_family)
    known_grades = gedcom.get_known_grades(grade_field)
    libraries_frame.cur_library.add_dispensa(self.cur_family, grade_field, known_grades, grades)
    batches_frame.set_batches(get_reduced_batches(libraries_frame.cur_library))
    self.add_window.destroy()

  def remove_family(self):
    search_selection = self.listbox.curselection()
    if len(search_selection) == 0:
      print('No family selected!')
      return
    if libraries_frame.cur_library is None:
      print('No library open!')
      return
    family = self.families[search_selection[0]][0]
    libraries_frame.cur_library.remove_dispensa(family)
    batches_frame.set_batches(get_reduced_batches(libraries_frame.cur_library))

search_frame = SearchFrame(left_frame, text='Search for family to add to library')
search_frame.pack(fill='x', pady=5)

"""Batches LabelFrame"""

class BatchesFrame(ttk.LabelFrame):

  def __init__(self, parent, text):
    super().__init__(parent, text=text)
    self.batches = {}
    self.batch_names = []
    self.batch_names_field = StringVar(value=[])
    
    self.library_name = StringVar(value='No library open.')
    self.library_label = ttk.Label(self, textvariable=self.library_name)
    self.library_label.pack()

    self.listbox = Listbox(self, listvariable=self.batch_names_field, height=18)
    self.listbox.pack()

    self.view_button = ttk.Button(self, text='View', command=self.view_batch)
    self.view_button.pack()

  def set_batches(self, batches):
    self.batches = batches
    self.batch_names = list(batches.keys())
    self.batch_names_field.set(self.batch_names)
    batch_selection = self.listbox.curselection()
    if len(batch_selection) != 0:
      batch_name = self.batch_names[batch_selection[0]]
      batch = self.batches[batch_name]
      candidates_frame.set_batch(batch)
  
  def view_batch(self):
    batch_selection = self.listbox.curselection()
    if len(batch_selection) == 0:
      print('No batch selected!')
      return
    batch_name = self.batch_names[batch_selection[0]]
    batch = self.batches[batch_name]
    candidates_frame.set_batch(batch)

  def clear(self):
    self.batches = {}
    self.batch_names = []
    self.batch_names_field.set([])
    self.library_name.set('No library open.')

batches_frame = BatchesFrame(right_frame, text='Batches')
batches_frame.pack(side='left')

"""Candidates LabelFrame"""

def name_candidate(candidate):
  info = gedcom.PID_dict[candidate[0][0]]
  male_side_name = info['GIVN'] + ' ' + info['SURN']
  info = gedcom.PID_dict[candidate[1][0]]
  female_side_name = info['GIVN'] + ' ' + info['SURN']
  return ((male_side_name, candidate[0][1]), (female_side_name, candidate[1][1]))

class CandidatesFrame(ttk.LabelFrame):

  def __init__(self, parent, text):
    super().__init__(parent, text=text)
    self.candidates = []
    self.elim_candidates = {}
    self.candidates_field = StringVar(value=[])
    self.elim_candidates_field = StringVar(value=[])

    self.tokens_field = StringVar(value='Tokens: ')
    self.tokens_label = ttk.Label(self, textvariable=self.tokens_field)
    self.tokens_label.pack()

    self.listbox = Listbox(self, listvariable=self.candidates_field, height=8)
    self.listbox.pack()

    self.elim_families_label_field = StringVar(value='Elim. families: ')
    self.elim_families_label = ttk.Label(self, textvariable=self.elim_families_label_field)
    self.elim_families_label.pack()

    self.elim_listbox = Listbox(self, listvariable=self.elim_candidates_field, height=8)
    self.elim_listbox.bind('<<ListboxSelect>>', self.display_elim_families)
    self.elim_listbox.pack()

  def set_batch(self, batch):
    reduced_candidates, tokens, elim_families = batch
    named_reduced_candidates = [name_candidate(candidate) for candidate in reduced_candidates]
    self.candidates = reduced_candidates
    self.candidates_field.set(named_reduced_candidates)
    self.tokens_field.set('Tokens: '+str(tokens))
    for elim_family, elim_candidates in elim_families.items():
      for elim_candidate in elim_candidates:
        if elim_candidate in self.elim_candidates:
          self.elim_candidates[elim_candidate].append(elim_family)
        else:
          self.elim_candidates[elim_candidate] = [elim_family]
    named_elim_candidates = [name_candidate(candidate) for candidate in list(self.elim_candidates.keys())]
    self.elim_candidates_field.set(named_elim_candidates)

  def display_elim_families(self, event):
    cur_candidate_index = self.elim_listbox.curselection()[0]
    cur_candidate = list(self.elim_candidates.keys())[cur_candidate_index]
    elim_families = self.elim_candidates[cur_candidate]
    self.elim_families_field.set('Elim. families: ' + str(elim_families))

  def clear(self):
    self.candidates = []
    self.elim_candidates = {}
    self.candidates_field.set([])
    self.elim_candidates_field.set([])
    self.tokens_field.set('Tokens: ')
    self.elim_families_label_field.set('Elim. families: ')

candidates_frame = CandidatesFrame(right_frame, text='Candidates')
candidates_frame.pack(side='right')

"""Main Loop"""

root.mainloop()
