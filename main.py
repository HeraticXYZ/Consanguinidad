import os
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
      label='Open workspace...'
    )
    self.add_separator()
    self.add_command(
      label='Save workspace'
    )
    self.add_separator()
    self.add_command(
      label='Exit',
      command=root.destroy
    )

  def open_gedcom(self):
    file_name = filedialog.askopenfilename(initialdir=__file__)
    if len(file_name) == 0:
      return
    global gedcom
    gedcom = GEDCOM(file_name)
    gedcom_label_text.set('GEDCOM: '+os.path.split(file_name)[1])
    print('GEDCOM imported successfully!')
    left_frame.pack(fill='x', expand=True, side='left', padx=5)
    right_frame.pack(fill='x', expand=True, side='right', padx=5)

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

class LibrariesFrame(ttk.LabelFrame):
  
  def __init__(self, parent, text):
    super().__init__(parent, text=text)
    self.lib_list = []
    self.libraries_field = StringVar(value=self.lib_list)
    self.libraries = {} # maps name of library to library object

    self.libraries_listbox = Listbox(self, listvariable=self.libraries_field, height=5)
    self.libraries_listbox.pack(fill='x')

    self.libraries_create_button = ttk.Button(self, text='Create Library', command=self.name_library)
    self.libraries_create_button.pack(expand=True, side='left')

    self.libraries_delete_button = ttk.Button(self, text='Delete Library', command=self.delete_library)
    self.libraries_delete_button.pack(expand=True, side='right')

  def create_library(self, new_name):
    if new_name != '':
      self.libraries[new_name] = CandidatesLibrary()
      self.lib_list.append(new_name)
      self.libraries_field.set(self.lib_list)

  def name_library(self):
    create_window = Toplevel()
    create_window.title('Create Library')
    
  
    new_name_frame = ttk.LabelFrame(create_window, text='Name')
    new_name_frame.pack()
    new_name_entry = ttk.Entry(new_name_frame)
    new_name_entry.pack()

    accept_button = ttk.Button(create_window, text='Accept', command=lambda:[self.create_library(new_name_entry.get()), create_window.destroy()])
    accept_button.pack(side='left')

    cancel_button = ttk.Button(create_window, text='Cancel', command=create_window.destroy)
    cancel_button.pack(side='right')

    create_window.wait_visibility()
    create_window.grab_set_global()

  def delete_library(self):
    if self.lib_list != []:
      cur_library_index = self.libraries_listbox.curselection()[0]
      del self.libraries[self.lib_list[cur_library_index]]
      self.lib_list.pop(cur_library_index)
      self.libraries_field.set(self.lib_list)

libraries_frame = LibrariesFrame(left_frame, text='Libraries')
libraries_frame.pack(fill='x')

"""Search LabelFrame"""

class SearchFrame(ttk.LabelFrame):

  def __init__(self, parent, text):
    super().__init__(parent, text=text)
    self.search_field = StringVar()
    self.families = [] # [ (FID, names), (FID, names), ... ]
    self.search_results_field = StringVar(value=self.families)

    self.search_entry = ttk.Entry(self, textvariable=self.search_field)
    self.search_entry.bind('<Return>', self.family_search)
    self.search_entry.pack(fill='x')

    self.search_listbox = Listbox(self, listvariable=self.search_results_field, height=10)
    self.search_listbox.pack(fill='x')

    self.search_add_button = ttk.Button(self, text='Add Family', command=self.select_grades)
    self.search_add_button.pack(expand=True, side='left')

    self.search_remove_button = ttk.Button(self, text='Remove Family', command=self.remove_family)
    self.search_remove_button.pack(expand=True, side='right')

  def family_search(self, event):
    text = self.search_field.get()
    for family, values in gedcom.FID_dict.items():
      if text in values['names']:
        self.families.append((family, values['names']))
    self.search_results_field.set(self.families)

  def add_family(self, grade_quantities):
    search_selection = self.search_listbox.curselection()
    library_selection = libraries_frame.libraries_listbox.curselection()
    if len(search_selection) == 0:
      print('No family selected!')
      return
    if len(library_selection) == 0:
      print('No library selected!')
      return
    grades = []
    try:
      for i in range(int(grade_quantities[0])):
        grades.append((2,2))
      for i in range(int(grade_quantities[1])):
        grades.append((2,3))
      for i in range(int(grade_quantities[2])):
        grades.append((3,3))
      for i in range(int(grade_quantities[3])):
        grades.append((3,4))
      for i in range(int(grade_quantities[4])):
        grades.append((4,4))
    except:
      print('Grade quantities must be positive integers!')
      return
    family = self.families[search_selection[0]][0]
    grade_field = gedcom.get_grade_field(family)
    known_grades = gedcom.get_known_grades(grade_field)
    cur_library_name = libraries_frame.lib_list[library_selection[0]]
    cur_library = libraries_frame.libraries[cur_library_name]
    cur_library.add_dispensa(family, grade_field, known_grades, grades)

  def select_grades(self):
    add_window = Toplevel()
    add_window.title('Select grades')
    
    entry_frame = ttk.Frame(add_window)
    entry_frame.pack(expand=True)
    buttons_frame = ttk.Frame(add_window)
    buttons_frame.pack()
    
    grades_label = ttk.Label(entry_frame, text='Grades')
    grades_label.grid(column=0, row=0, ipadx=7)
    grade_label_2 = ttk.Label(entry_frame, text='2°')
    grade_label_2.grid(column=0, row=1, ipadx=5)
    grade_label_2c3 = ttk.Label(entry_frame, text='2° con 3°')
    grade_label_2c3.grid(column=0, row=2, ipadx=5)
    grade_label_3 = ttk.Label(entry_frame, text='3°')
    grade_label_3.grid(column=0, row=3, ipadx=5)
    grade_label_3c4 = ttk.Label(entry_frame, text='3° con 4°')
    grade_label_3c4.grid(column=0, row=4, ipadx=5)
    grade_label_4 = ttk.Label(entry_frame, text='4°')
    grade_label_4.grid(column=0, row=5, ipadx=5)

    quantity_label = ttk.Label(entry_frame, text='Quantity')
    quantity_label.grid(column=1, row=0, sticky=EW)
    grade_quantity_2 = StringVar()
    grade_entry_2 = ttk.Entry(entry_frame, textvariable=grade_quantity_2, width=5)
    grade_entry_2.grid(column=1, row=1, sticky=EW)
    grade_quantity_2c3 = StringVar()
    grade_entry_2c3 = ttk.Entry(entry_frame, textvariable=grade_quantity_2c3, width=5)
    grade_entry_2c3.grid(column=1, row=2, sticky=EW)
    grade_quantity_3 = StringVar()
    grade_entry_3 = ttk.Entry(entry_frame, textvariable=grade_quantity_3, width=5)
    grade_entry_3.grid(column=1, row=3, sticky=EW)
    grade_quantity_3c4 = StringVar()
    grade_entry_3c4 = ttk.Entry(entry_frame, textvariable=grade_quantity_3c4, width=5)
    grade_entry_3c4.grid(column=1, row=4, sticky=EW)
    grade_quantity_4 = StringVar()
    grade_entry_4 = ttk.Entry(entry_frame, textvariable=grade_quantity_4, width=5)
    grade_entry_4.grid(column=1, row=5, sticky=EW)

    def get_grade_quantities():
      return [grade_quantity_2.get(), 
              grade_quantity_2c3.get(), 
              grade_quantity_3.get(), 
              grade_quantity_3c4.get(), 
              grade_quantity_4.get(), ]
    
    accept_button = ttk.Button(buttons_frame, text='Accept', command=lambda:[self.add_family(get_grade_quantities()), add_window.destroy()])
    accept_button.pack(side='left')

    cancel_button = ttk.Button(buttons_frame, text='Cancel', command=add_window.destroy)
    cancel_button.pack(side='right')
    
    add_window.wait_visibility()
    add_window.grab_set_global()

  def remove_family(self):
    pass

search_frame = SearchFrame(left_frame, text='Search for family to add to library')
search_frame.pack(fill='x', pady=5)

"""Batches LabelFrame"""

batches = StringVar(value=[])

batches_frame = ttk.LabelFrame(right_frame, text='Batches')
batches_frame.pack(side='left')

batches_listbox = Listbox(batches_frame, listvariable=batches, height=20)
batches_listbox.pack()

"""Candidates LabelFrame"""

candidates = StringVar(value=[])

candidates_frame = ttk.LabelFrame(right_frame, text='Candidates')
candidates_frame.pack(side='right')

candidates_listbox = Listbox(candidates_frame, listvariable=candidates, height=20)
candidates_listbox.pack()

"""Main Loop"""

root.mainloop()
