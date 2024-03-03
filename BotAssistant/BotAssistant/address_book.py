from collections import UserDict
from datetime import datetime
from db_connector import FileConnectorFactory
from dateutil.parser import parse
import re


# Rows per page for printing pages
ROWS_PER_PAGE = 10

class Field:
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError(f"Value {type(self).__name__} is not valid")
        self.__value = value

    # Value getter (per requirements)
    @property
    def value(self):
        return self.__value
    # Value setter (per requirements)
    @value.setter
    def value(self, value):
        if not self.is_valid(value):
            raise ValueError(f"Value {type(self).__name__} is not valid")
        self.__value = value

    def __str__(self):
        return str(self.value)
    
    def __repr__(self) -> str:
        return str(self.value)
    
    # Validation of fields
    def is_valid(self, value)->bool:
        return bool(value)
   
class Birthday(Field):
    def is_valid(self, birthday)->bool:
        # Check if it is possible to convert exact string (fuzzy = False) to date
        try:
            birthday_date = parse(birthday, fuzzy=False)
            print(birthday_date)
            return True
        except ValueError:
            return False


class Name(Field):
    pass

class Notes(Field):
    pass    

class Phone(Field):
    
    def is_valid(self, phone)->bool:
        return bool(re.match(r'^\d{10}$', phone))

   
class Record:
    def __init__(self, name, birthday:Birthday=""):
        self.name = Name(name)       
        if birthday:
            self.birthday = Birthday(birthday)
        else: 
            self.birthday = None
        self.phones = []
        self.notes = {}

    def add_phone(self, phone):
        phone = Phone(phone)        
        self.phones.append(phone)

    def add_note(self, note, tag=""):
        if note not in self.notes:
            self.notes[note] = tag

    def edit_note(self, note_old, note_new):        
        if note_old in self.notes:
            self.notes[note_new] = self.notes[note_old]
            self.notes.pop(note_old)
        else: 
            raise ValueError(f"Note {note_old} not found")

    def edit_tag(self, note, tag):
        if (note in self.notes) and (self.notes[tag] != tag):
            self.notes[note] = tag
        else:
            raise ValueError(f"Note {note} not found")

    def delete_note(self, note):
        self.notes.pop(note)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)        

    # Calculate days to birthday
    def days_to_birthday(self)->int:
        if self.birthday:
            birthday = self.birthday.value
        else: 
            birthday = None
        if birthday:        
            current_date = datetime.now().date()
            birthday_date_this_year = parse(birthday, fuzzy=False).replace(year = datetime.now().year).date()
            delta = birthday_date_this_year - current_date
            # If birthdate in future current year
            if delta.days>0:
                return delta.days
            else: 
                # If birthdate in current year has passed (calculate days to next year's date)
                return (birthday_date_this_year.replace(year=current_date.year+1) - current_date).days
        else:
            return None
    
                
    
    def edit_phone(self, phone_old, phone_new):
        phone_new = Phone(phone_new)
        for i, phone in enumerate(self.phones):
            if phone.value == phone_old:
                self.phones[i] = phone_new                
                return
        raise ValueError("Phone not found")
    
    def find_phone(self, phone):        
        for phone_item in self.phones:
            if phone_item.value == phone:
                return phone_item
        return None    
    
    
    def remove_phone(self, phone):
        for phone_item in self.phones:
            if phone_item.value == phone:
                self.phones.remove(phone_item)

    def __str__(self):
        birthday_txt=""        
        if self.birthday:
            birthday_txt = f"birthday: {self.birthday}, "
        return f"Contact name: {self.name}, {birthday_txt}phones: {'; '.join(p.value for p in self.phones)}"
    

class AddressBook(UserDict):
    def add_record(self, record: Record):
        if not record.name:
            return
        self.data[record.name.value] = record

    def find(self, name:str):
        return  self.data.get(name, None)
    
    def delete(self, name:str):        
            self.pop(name, None)
    # print AddressBook using pagination
    def print_book(self):
        cnt = 1
        # Getting rows_per_page
        for rows in self:
            print(f"page {cnt}")
            # Pages count
            cnt+=1
            for row in rows:
                # Print rows on the page
                print(row)

    def save_address_book(self):
        # can be rewriten by adding needed file type to FileConnectorFactory
        serialization_type = FileConnectorFactory().get_connector('binary')
        
        # Can be specified parameter for file storate
        serialization_type.save_data(self)

    def recover_address_book(self):
        deserialization_type = FileConnectorFactory().get_connector('binary')
        
        # Can be specified parameter for file storate
        data = deserialization_type.retreive_data()
        print(type(data))
        if data:
            return data
        else:
            return AddressBook()
        
    # Get address book with all contacts, that have birthdays in <days> days
    def show_birthday(self, days:int):        
        contacts = AddressBook()
        for name, record in self.data.items():
            if record.days_to_birthday():
                if record.days_to_birthday() - int(days) == 0:
                    contacts[name] = record

        return contacts

    def search_records(self, text: str) -> dict:
        search_results = {}
        for name, record in self.data.items():
            # Check if the text is a substring of the name
            if text.lower() in name.lower():
                search_results[name] = record
            else:
                # Check if the text is a substring of any phone number
                for phone in record.phones:
                    if text in phone.value:
                        search_results[name] = record
                        break  # Stop searching if a match is found in any phone number               

        return AddressBook(search_results)    
    
    def __iter__(self):        
        return Iterable(ROWS_PER_PAGE, self.data)

class Iterable:
    def __init__(self, n: int, book: AddressBook):
        self.n = n
        self.book = book
        # Total number of records
        self.number_of_records = len(book)
        # number of page
        self.page = 0    

    def __next__(self):
        # Define start and end records of the page
        start = self.page * self.n
        end = min((self.page + 1) * self.n, self.number_of_records)

        # If start record exceeds total number of records throw StopIteration exception to finish generation
        # The rest of the code won't be exectuted if the next starting record number exeeds the total number
        if start >= self.number_of_records:
            raise StopIteration

        # Convert to list and slice needed amount of the dict records (from start to end)
        page_records = list(self.book.values())[start:end]
        # Increment page count
        self.page += 1
        # Here we can return page_records and self.page as a tuple, to use it in print method, but IMHO it's a little bit overhead 
        # And it will make the code less readable
        return page_records