from address_book import AddressBook, Record
from abc import ABC, abstractclassmethod

class Command(ABC):
    @abstractclassmethod
    def answer_greeting():
        pass
    @abstractclassmethod
    def answer_greeting(self):
        pass
    
    # Greetings (command: help)
    @abstractclassmethod
    def help_info(self):
        pass

    # Add contact to the data base (command: add)
    @abstractclassmethod    
    def set_contact(self, commands)->str:    
        pass
        
    #Adds birthday to the existent contact
    @abstractclassmethod
    def provide_birthday(self, commands)->str:
        pass        
    
    @abstractclassmethod
    def update_phone(self, commands)->str:    
        pass

    # Get contact phone by name (command: phone)
    @abstractclassmethod
    def get_phone(self, commands)->str:
        pass
    
    @abstractclassmethod
    def remove(self, commands)->str:
        pass
    
    # Filter by phone or phone number
    @abstractclassmethod
    def filter_contacts(self, commands)->str:
        pass

    # Filter contacts that have birthday in specified amount of days
    @abstractclassmethod
    def show_birthdays(self, commands):
        pass
    
    # Print all contacts in the data base (command: show all)
    @abstractclassmethod
    def display(self):
        pass

    # Save the data to file and stop working with bot
    @abstractclassmethod
    def quit_bot(self):
        pass

    @abstractclassmethod
    def add_note(self, commands):
        pass

    def edit_note(self, commands):
        pass

    @abstractclassmethod
    def delete_note(self, commands):
        pass

    @abstractclassmethod
    def update_tag(self, commands):
        pass
    



class BotCLI(Command):
    def __init__(self):    
        self.phone_book = AddressBook()    
        self.phone_book = self.phone_book.recover_address_book()

    # Handling errors (Decorator implementation)
    def input_error(func):
        def inner(*args):
            try:
                return func(*args)
            except KeyError as e:
                if str(e)=='':
                    return "Provide a usernmae"
                else:
                    return f"No contact with name = {str(e)}"
            except ValueError as e:
                if str(e)=="Invalid parameters":
                    return "Unable to update. Incorrect usename. Use add <name> <phone> to add a new user"
                else:
                    return str(e)
            except IndexError as e:
                if str(e)=='list index out of range':
                    return "Provide name and phone"
                else:
                    return str(e)        
        return inner

    # Handlers
    # Greetings (command: hello)
    def answer_greeting(self):
        return "How can I help you?"
    
    # Greetings (command: help)
    def help_info(self):
        return """Commands list:\n
        hello - prints greeting \n
        add <contact name> <phone number>- adds record if contact name is not present, adds phone if contact name is present and phone number differs from other \n
        change <contact name> <old phone> <new phone>- changes contact phone by name \n
        delete <contact name> - delete contact or delete <contact name> <phone> - delete specified phone for the contact \n
        set_birthday <contact name> <birthday date> - adds birthday to specified contact \n
        days_to_birthday <number of days> - shows all contacts that have birthday in specified number of days \n
        set_note <contact name> <note> <tag (optional)>  - adds note for the contact (if exists overwrite) \n
        update_note <contact name> <note> - updates note or adds new one if not present (if updated, tag ramains the same) \n
        delete_note <contact_name> <note> - removes note for specified contact \n
        update_tag <contact_name> <note> <new_tag> updates tag for the specified note \n
        phone <contact name> - get contact phones by name \n
        show all - prints contact book \n
        search <substring> - filter by name letters or phone number sequence \n
        exit, good bye, close - saves changes to database and exit \n
        """

    # Add contact to the data base (command: add)
    @input_error
    def set_contact(self, commands)->str:    
        if commands[1] in self.phone_book:
            phonelist = [str(phone) for phone in self.phone_book.find(commands[1]).phones]
            #TODO check false case   
            if commands[2] in phonelist:
                raise ValueError(f"Contact with such name ({commands[1]}) and phone ({commands[2]})already exists.")
            else:
                self.phone_book[commands[1]].add_phone(commands[2])
                return f"Contact's {commands[1]} another phone {commands[2]} is added to DBMS"
        else:
            record = Record(commands[1])
            record.add_phone(commands[2])
            self.phone_book.add_record(record)            
            return f"Contact {commands[1]} {commands[2]} is added to DBMS"
        
    #Adds birthday to the existent contact
    @input_error
    def provide_birthday(self, commands)->str:
        if commands[1] in self.phone_book:
            self.phone_book[commands[1]].add_birthday(commands[2])
            return f'Birthday date {commands[2]} was added(changed) for contact {commands[1]}'

    # Update phone for existing contact by its name (command: change)
    @input_error
    def update_phone(self, commands)->str:    
        if commands[1] in self.phone_book:
            phonelist = [str(phone) for phone in self.phone_book.find(commands[1]).phones]
            if (commands[2] not in phonelist) and (commands[3] in phonelist):
                raise ValueError(f"Check command values. Phone {commands[2]} is not found! or phone {commands[3]} is present in contact phones")
            else:
                self.phone_book[commands[1]].edit_phone(commands[2], commands[3])
            
            return f"Contact {commands[1]} phone number {commands[2]} is changed to {commands[3]}"
        else:
            raise ValueError(f"Contact {commands[1]} is not found!")

    # Get contact phone by name (command: phone)
    @input_error
    def get_phone(self, commands)->str:
        if commands[1] not in self.phone_book:
            raise ValueError(f"Contact with such name ({commands[1]}) not present in Address Book.")
        return f" The contact {commands[1]} has phone numbers: {[str(phone) for phone in self.phone_book.find(commands[1]).phones]}"
    # Delete phone from contact's phone list

    @input_error
    def remove(self, commands)->str:
        if commands[1] in self.phone_book:
            record = self.phone_book.find(commands[1])
            if len(record.phones) > 1:
                for phone in record.phones:
                    if str(phone)==commands[2]:
                        record.phones.remove(phone)
            else:
                raise ValueError("Unable to delete last phone from phone list")
        else:
            raise ValueError(f"Contact with such name ({commands[1]}) not present in Address Book.")

        return f" The phone {commands[2]} has been removed from phone numbers of {commands[1]}"
    
    # Filter by name or phone number 
    @input_error
    def filter_contacts(self, commands)->str:
        # TODO add search by note
        address_book =  self.phone_book.search_records(commands[1])
        if not address_book:
            print(f"No contacts found that match criteria {commands[1]}")
        else:
            address_book.print_book()

    # Filter contacts that have birthday in specified amount of days
    @input_error
    def show_birthdays(self, commands):
        contact_birthdays = self.phone_book.show_birthday(commands[1])
        if not contact_birthdays:
            print(f"No contacts with birthdays in {commands[1]} days")
        else:
            contact_birthdays.print_book()
    
    # Print all contacts in the data base (command: show all)
    def display(self):
        if not self.phone_book:
            print("No contacts found.")
        else:
            self.phone_book.print_book()

    # Quit the program ( command: good buy, close, exit)
    def quit_bot(self):
        self.phone_book.save_address_book()
        quit()


    @input_error
    def add_note(self, commands):
        if commands[1] in self.phone_book:
            if len(commands) > 2:
                self.phone_book[commands[1]].add_note(commands[2], tag=commands[3])
                return f'Note {commands[2]} with tag {commands[3]} was added(changed) for contact {commands[1]}'
            elif len(commands) > 1:
                self.phone_book[commands[1]].add_note(commands[2])
                return f'Note {commands[2]} with empty tag was added(changed) for contact {commands[1]}'

    @input_error
    def edit_note(self, commands):
        if commands[1] in self.phone_book:
            self.phone_book[commands[1]].edit_note(commands[2], commands[3])
            return f'Updated tag {commands[2]} with tag {commands[3]} for contact {commands[1]}'

    @input_error
    def delete_note(self, commands):
        if commands[1] in self.phone_book:
            self.phone_book[commands[1]].delete_note(commands[2])
            return f'Deleted note {commands[2]}  for contact {commands[1]}'

    @input_error
    def update_tag(self, commands):
        if commands[1] in self.phone_book:
            self.phone_book[commands[1]].edit_tag(commands[2], commands[3])
            return f'Updated tag {commands[3]} for  note {commands[3]} for contact {commands[1]}'
    


    # Handler function
    def get_handler(self, command):    
        return self.COMMANDS[command]   
    
    COMMANDS = {
            'hello': answer_greeting,
            'add': set_contact,
            'change': update_phone,
            'phone' : get_phone,
            'set_birthday' : provide_birthday,
            'set_note' : add_note,
            'update_note' : edit_note,
            'delete_note' : delete_note,
            'update_tag' : update_tag,
            'days_to_birthday': show_birthdays,
            'delete' : remove,
            'show all': display,
            'search': filter_contacts,
            'help': help_info,
            'exit' : quit_bot
        }
    
    def start_bot(self):
        exit_cmds = ["good bye", "close", "exit"]
        while True:
            commands = list()
            prop = input("Enter a command( or 'help' for list of available commands: ")
            if prop.lower() in exit_cmds:
                prop = 'exit'
            commands = prop.split(' ')
            if len(commands)>0: 
                commands[0]=commands[0].lower()
            match commands[0]:
                case 'exit':
                    print("Good bye!")
                    self.get_handler(commands[0])(self)
                case 'hello' | 'help':
                    print(self.get_handler(commands[0])(self))                
                case 'add' | 'change' | 'phone' | 'set_birthday' | 'set_note' | 'update_note' | 'delete_note' | 'update_tag':
                    print(self.get_handler(commands[0])(self, commands))            
                case 'show':
                    show_all = " ".join(commands).lower()
                    if show_all == 'show all':
                        self.get_handler(f"{show_all}")(self)
                    else:
                        print("Incorrect <show all> command. Please, re-enter.")
                case 'delete':
                    print(self.get_handler(commands[0])(self, commands))
                case 'search' | 'days_to_birthday':
                    self.get_handler(commands[0])(self, commands)
                case _:
                    print("Incorrect command, please provide the command from the list in command prompt") 