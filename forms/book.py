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

    # this is a class for customer who will sell their book
    name  = State()
    phone =  State()
    location = State()
    address = State()
    
    username = State()
    status = State()

    # this is a class for customer who will buy or rent the book
    buyer_name  = State()
    buyer_phone =  State()
    buyer_address = State()
    service_type = State()
    buyer_book_title = State()

    #this is a states when customer want to order a new book
    new_order_title = State()
    new_order_author = State()
    new_order_phone = State()
    new_order_type = State()
    new_order_name = State()

