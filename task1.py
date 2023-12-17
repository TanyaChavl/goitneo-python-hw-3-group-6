# Add get_birthdays_per_week to the AddressBook

from datetime import datetime
import re
from collections import UserDict, defaultdict
import calendar

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

book = AddressBook()
john_record = Record("John", datetime(1990, 12, 19))
john_record.add_phone("1234567890")
book.add_record(john_record)

birthdays_next_week = book.get_birthdays_per_week()
for day, names in birthdays_next_week.items():
    print(f"{day}: {', '.join(names)}")
