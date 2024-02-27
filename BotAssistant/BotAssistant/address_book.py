from collections import UserDict
from datetime import datetime
from dateutil.parser import parse
import pickle
import re
import os.path

# If no filename for saving address book data provided 
FILENAME = "./BotAssistant/res/phone_book.dat"
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
        #check if it is possible to convert exact string (fuzzy = False) to date
        try:
            birthday_date = parse(birthday, fuzzy=False)
            print(birthday_date)
            return True
        except ValueError:
            return False


class Name(Field):
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

    def add_phone(self, phone):
        phone = Phone(phone)        
        self.phones.append(phone)

    # days_to_birthday
    def days_to_birthday(self)->int:
        birthday = self.birthday.value
        current_date = datetime.now().date()
        birthday_date_this_year = parse(birthday, fuzzy=False).replace(year = datetime.now().year).date()
        delta = birthday_date_this_year - current_date
        # if birthdate in future current year
        if delta.days>0:
            return delta.days
        else: 
            # if birthdate in current year has passed (calculate days to next year's date)
            return (birthday_date_this_year.replace(year=current_date.year+1) - current_date).days
                
    
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
        #getting rows_per_page
        for rows in self:
            print(f"page {cnt}")
            #pages count
            cnt+=1
            for row in rows:
                #print rows on the page
                print(row)

    def save_address_book(self, filename = FILENAME):
        with open (filename, "wb") as file:
            pickle.dump(self, file)

    def recover_address_book(self, filename = FILENAME):
        if os.path.isfile(filename):
            with open(filename, 'rb') as file:            
                content = pickle.load(file)
            return content
        else:
            return AddressBook()
        return content

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