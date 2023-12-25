"""
this module will hold book form"""
from aiogram.fsm.state import State, StatesGroup

class Customer(StatesGroup):
    """
    this is a class for customer who will buy or rent the book"""

    book_id = State()
    name  = State(),
    phone =  State(),
    location = State(),
    address = State(),