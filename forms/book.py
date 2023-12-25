"""
this module will hold book form"""
from aiogram.fsm.state import State, StatesGroup

class Book(StatesGroup):
    """
    book class that is related to"""
    book_id = State()
    title = State()
    author = State()
    image  = State()
    date  = State()
    overview = State()
    num_of_pages  = State()
    genre  = State()
    price = State()
    book_status = State()
    rating = State()
    amount = State()
    finish = State()
    buy = State()
    rent = State()

    # this is a class for customer who will buy or rent the book
    name  = State()
    phone =  State()
    location = State()
    address = State()
    service_type = State()