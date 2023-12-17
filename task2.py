from datetime import datetime
import re
from collections import UserDict, defaultdict
import calendar

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, ValueError, KeyError) as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    return inner

def parse_input(user_input):
    if not user_input.strip():
        return None, []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    if len(args) != 2:
        raise ValueError("Invalid input. Please provide both name and phone number.")
    name, phone = args
    lower_case_name = name.lower()
    record = Record(lower_case_name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_phone(args, book):
    if len(args) != 2:
        raise ValueError("Invalid input. Please provide both name and phone number.")
    name, new_phone = args
    lower_case_name = name.lower()
    record = book.find(lower_case_name)
    if record:
        old_phone = record.phones[0].value if record.phones else None
        record.edit_phone(old_phone, new_phone)
        return f"Contact for {name} updated."
    else:
        return "Contact not found."

@input_error
def get_phone(args, book):
    if len(args) < 1:
        raise ValueError("Please provide a contact name.")
    name = args[0]
    lower_case_name = name.lower()
    record = book.find(lower_case_name)
    if record and record.phones:
        return record.phones[0].value
    else:
        return "Contact not found."

@input_error
def show_all_contacts(book):
    if book:
        return "\n".join([str(record) for record in book.data.values()])
    else:
        return "No contacts saved."
    
@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Please provide both the contact name and birthday in the format 'DD.MM.YYYY'.")
    name, birthday_str = args
    lower_case_name = name.lower()
    record = book.find(lower_case_name)
    if not record:
        return "Contact not found."
    try:
        birthday = datetime.strptime(birthday_str, "%d.%m.%Y")
        record.add_birthday(birthday)
        return "Birthday added."
    except ValueError:
        return "Invalid date format. Use DD.MM.YYYY."

@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise ValueError("Please provide a contact name.")
    name = args[0]
    lower_case_name = name.lower()
    record = book.find(lower_case_name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    else:
        return "Birthday not found for this contact."

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not re.match(r"^\d{10}$", value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        if not isinstance(value, datetime):
            raise TypeError("Birthday must be a date.")
        super().__init__(value)

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if birthday:
            self.add_birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = None
        for p in self.phones:
            if p.value == phone:
                phone_to_remove = p
                break
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = ', '.join([str(p.value) for p in self.phones])
        birthday_str = f", birthday: {self.birthday.value.strftime('%Y-%m-%d')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"
    
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        birthdays = defaultdict(list)
        today = datetime.now().date()

        for record in self.data.values():
            if record.birthday:
                name = record.name.value
                birthday = record.birthday.value.date()
                birthday_this_year = birthday.replace(year=today.year)

                delta_days = (birthday_this_year - today).days
                if delta_days < 0:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                    delta_days = (birthday_this_year - today).days

                if 0 <= delta_days < 7:
                    day_of_week = calendar.day_name[birthday_this_year.weekday()]
                    if day_of_week in ["Saturday", "Sunday"]:
                        day_of_week = "Monday"
                    birthdays[day_of_week].append(name)

        return birthdays

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command is None:
            continue

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_phone(args, book))
        elif command == "phone":
            print(get_phone(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            birthdays_next_week = book.get_birthdays_per_week()
            if birthdays_next_week:
                for day, names in birthdays_next_week.items():
                    print(f"{day}: {', '.join(names)}")
            else:
                print("No birthdays next week.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()