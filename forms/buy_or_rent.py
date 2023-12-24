"""
this module will hold book form"""
from aiogram.fsm.state import State, StatesGroup

class Book(StatesGroup):
    book_id = State()
    title = State()
    date  = State()
    overview = State()
    num_of_pages  = State()
    genre  = State()
    price = State()
    book_status = State()
    rating = State()
    amount = State()