from collections import UserDict
from datetime import datetime, timedelta
from functools import wraps
import pickle
from abc import ABC, abstractmethod

# Classes for fields
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if len(self.value) != 10 or not self.value.isdigit():
            raise ValueError("The number must be 10 digits long")

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime('%d.%m.%Y')

# Class for records
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError(f"'{phone}' not found")

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError(f"'{old_phone}' not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

# Class for address book
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        current_date = datetime.today().date()
        congratulation_period = timedelta(days)
        result = []

        for item in self.data:
            contact = self.data.get(item)
            if contact.birthday is None:
                continue
            birthday_dt = contact.birthday.value
            birthday_this_year = datetime(year=current_date.year, month=birthday_dt.month, day=birthday_dt.day).date()

            if current_date > birthday_this_year:
                birthday_this_year = datetime(year=current_date.year + 1, month=birthday_dt.month, day=birthday_dt.day).date()

            if current_date <= birthday_this_year <= current_date + congratulation_period:
                if birthday_this_year.weekday() == 5:  # Saturday
                    birthday_this_year += timedelta(days=2)
                elif birthday_this_year.weekday() == 6:  # Sunday
                    birthday_this_year += timedelta(days=1)
                result.append(f"Contact name: {contact.name.value}, birthday: {birthday_this_year.strftime('%d.%m.%Y')}")

        return result

# Abstract class for user views
class UserView(ABC):
    @abstractmethod
    def show(self, message: str):
        pass

# Concrete class for console view
class ConsoleView(UserView):
    def show(self, message: str):
        print(message)

# Decorator for handling input errors
def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found. Give correct name, Please."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Contact not found."
    return inner

# Function to parse user input
def parse_input(user_input):
    return user_input.lower().split()

# Functions for handling commands
@input_error
def add_contact(args, book: AddressBook, view: UserView):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    view.show(message)

@input_error
def change_contact(args, book: AddressBook, view: UserView):
    name, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.phones = []
        record.add_phone(new_phone)
        view.show("Contact changed.")
    else:
        view.show("Contact not found.")

@input_error
def show_phone(args, book: AddressBook, view: UserView):
    name = args[0]
    record = book.find(name)
    if record:
        view.show(str(record))
    else:
        view.show("Contact not found.")

@input_error
def add_birthday(args, book: AddressBook, view: UserView):
    if len(args) >= 2:
        name, birthday = args[:2]
        record = book.find(name)
        if record:
            record.add_birthday(birthday)
            view.show("Birthday added.")
        else:
            view.show("Contact not found.")
    else:
        view.show("Please provide both name and birthday.")

@input_error
def show_birthday(args, book: AddressBook, view: UserView):
    name = args[0]
    record = book.find(name)
    if record:
        view.show(f"Contact name: {name}, birthday: {record.birthday}")
    else:
        view.show("Contact not found.")

@input_error
def birthdays(args, book: AddressBook, view: UserView):
    try:
        days = int(args[0]) if args else 7
        birthdays_next_week = book.get_upcoming_birthdays(days)
        if len(birthdays_next_week) == 0:
            view.show("No birthdays next week")
        else:
            view.show("\n".join(birthdays_next_week))
    except (AttributeError, ValueError, IndexError):
        view.show("Error in fetching birthdays")

# Functions for saving and loading data
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return new address book if file not found

# Main function
def main():
    book = load_data()
    view = ConsoleView()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            view.show("Good bye!")
            save_data(book)  # Save data before exiting
            break
        
        elif command == "hello":
            view.show("How can I help you?")
            
        elif command == "add":
            add_contact(args, book, view)
            
        elif command == "change":
            change_contact(args, book, view)
            
        elif command == "phone":
            show_phone(args, book, view)
            
        elif command == "all":
            for item in book:
                view.show(str(book.find(item)))
                
        elif command == "add-birthday":
            add_birthday(args, book, view)
            
        elif command == "show-birthday":
            show_birthday(args, book, view)
            
        elif command == "birthdays":
            birthdays(args, book, view)
            
        else:
            view.show("Invalid command.")

if __name__ == "__main__":
    main()

