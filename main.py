"""
this is out main.py file"""
import os
import asyncio
import logging
import sys
import sqlite3
import firebase_admin

from firebase_admin import credentials, firestore
from aiogram.filters import  CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F, Router

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

from aiogram.types import CallbackQuery
from dotenv import load_dotenv
from callbacks.my_callback import MyCallback
from forms.book import Book

# this is firebase configuration
cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

load_dotenv()
form_router = Router()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()

@form_router.message(CommandStart())
async def start(message: Message) -> None:
    """
    This function handles the /start command.
    """
  
    user = " not admin"
    menu =InlineKeyboardMarkup (
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Buy Book", callback_data=MyCallback(name="buy_book", id="1").pack()),
                InlineKeyboardButton(text="Rent Book", callback_data=MyCallback(name="rent_book", id="2").pack()),
            ],
            [
                InlineKeyboardButton(text="Sell Book", callback_data=MyCallback(name="sell_book", id="3").pack()),
                InlineKeyboardButton(text="Order new", callback_data=MyCallback(name="order_book", id="4").pack()),
            ]
            ], resize_keyboard=True
    )
    if user == "admin":
        menu.inline_keyboard.append([
          InlineKeyboardButton(text="orders", callback_data=MyCallback(name="orders", id="4").pack()),  
        ])
    await message.answer("welcome to ብርሀን መፅሐፍ ማከፋፈያ", reply_markup=menu)

@form_router.message(Command("Cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def command_cancel(message: Message, state: FSMContext) -> None:
    """
    allow the user to cancel
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    
    logging.info("canceling info from %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    
    )

@form_router.callback_query(MyCallback.filter(F.name == "order_book"))
async def order_new(query: CallbackQuery, state : FSMContext) -> None:
    """
    this function will handle the order new button
    """
    await state.set_state(Book.new_order_title)
    await query.message.delete()

    await query.message.answer("Enter the title of the book", reply_markup=ReplyKeyboardRemove())

@form_router.message(Book.new_order_title)
async def new_order_title(message: Message, state: FSMContext) -> None:
    """
    this function will prcoess title of the new order"""

    await state.set_state(Book.new_order_author)
    await state.update_data(new_order_title = message.text)
    await message.answer("Enter the author of the book please")

@form_router.message(Book.new_order_author)
async def new_order_author(message: Message, state: FSMContext) -> None:
    """
    this function will process name of the person who ordered new book"""
    await state.set_state(Book.new_order_name)
    await state.update_data(new_order_author = message.text)
    await message.answer("Enter your fullname please", reply_markup=ReplyKeyboardRemove())

@form_router.message(Book.new_order_name)
async def new_order_name(message: Message, state: FSMContext) -> None:
    """
    this function will process name of the person who ordered new book"""
    await state.set_state(Book.new_order_phone)
    await state.update_data(new_order_name = message.text)
    await message.answer("share your number please", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="share your phone", request_contact=True)
            ]
        ], resize_keyboard=True
    ))

@form_router.message(Book.new_order_phone)
async def new_order_phone(message: Message, state: FSMContext) -> None:
    """
    this function will process phone number of the person who ordered new book"""
    await state.set_state(Book.finish)
    await state.update_data(new_order_phone = message.contact.phone_number)
    data = await state.get_data()

    new_order = {
        'name': data["new_order_name"],
        'phone_number': data["new_order_phone"],
        'location': "Addis Ababa",
        'address': "Addis Ababa",
        'book_title': data["new_order_title"],
        'author': data["new_order_author"],
        'type': "new"  # Set the 'type' field to "new"
    }

    # Add the new order to the 'orders' collection
    db.collection('orders').add(new_order)
    
    await message.answer("Order added successfully", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Back", callback_data=MyCallback(name="back", id="1").pack()),
            ]
        ]
    ))

@form_router.callback_query(MyCallback.filter(F.name == "back"))
async def mainmenu(query: CallbackQuery) -> None:
    """
    this function will be called when the back button is entered
    """

    menu =InlineKeyboardMarkup (
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Buy Book", callback_data=MyCallback(name="buy_book", id="1").pack()),
                InlineKeyboardButton(text="Rent Book", callback_data=MyCallback(name="rent_book", id="2").pack()),
            ],
            [
                InlineKeyboardButton(text="Sell Book", callback_data=MyCallback(name="sell_book", id="3").pack()),
                InlineKeyboardButton(text="Order new", callback_data=MyCallback(name="order_book", id="4").pack()),
            ]
            ], resize_keyboard=True
    )
  

    await query.message.delete()
    await query.message.answer("welcome to ብርሀን መፅሐፍ ማከፋፈያ", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.name == "orders"))
async def order(query: CallbackQuery) -> None:
    """
    This function will be handled when the order is entered
    """
    await query.message.delete()
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM orders
        """
    )

    orders = cursor.fetchall()
    conn.close()
    
    menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text="sells", callback_data=MyCallback(name="sold_order", id='12').pack()),
            InlineKeyboardButton(text="orders", callback_data=MyCallback(name="buy_order", id='13').pack())
            ],
            [
            InlineKeyboardButton(text="Back", callback_data=MyCallback(name="back", id="1").pack()),
            ]
        ]
    )
    await query.message.answer("Select the type of order please!", reply_markup=menu)
@form_router.callback_query(MyCallback.filter(F.name == "view_order"))
async def view_order(query: CallbackQuery, callback_data: MyCallback) -> None:
    """
    This function will be handled when the view order is entered
    """
    await query.message.delete()
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM orders WHERE order_id = ?
        """,
        (callback_data.id,)
    )

    another_order = cursor.fetchone()

    cursor.execute(
        """
        SELECT * FROM books WHERE book_id = ?
        """,
        (another_order[1],)
    )
    
    the_book = cursor.fetchone()
    conn.close()

    text = f"username: @{another_order[2]}\nName: {another_order[3]}\nPhone: +{another_order[4]}\nLocation: {another_order[5]}\nSpecific address: {another_order[6]}\nType: {another_order[7]}\n\nTitle: {the_book[1]}"
    await query.message.answer_photo(photo=the_book[3], caption=text)

@form_router.callback_query(MyCallback.filter(F.name == "rent_book"))
async def rent_book(query: CallbackQuery, state: FSMContext) -> None:
    """
    This function will be handled when the rent book is entered
    """  
    await state.update_data(service_type="rent")
    await query.message.delete()
    menu = InlineKeyboardMarkup(
        inline_keyboard= [
            [
                InlineKeyboardButton(text="Fiction", callback_data=MyCallback(name="Romantic", id="10").pack()),
                InlineKeyboardButton(text="Educational", callback_data=MyCallback(name="novel", id="10").pack()),
                
            ],
            [
                InlineKeyboardButton(text="spiritual", callback_data=MyCallback(name="biography", id="10").pack()),
                InlineKeyboardButton(text="philosophy", callback_data=MyCallback(name="comedy", id="10").pack()),
                
            ],
            [
                InlineKeyboardButton(text="Business", callback_data=MyCallback(name="fantasy", id="10").pack()),
                InlineKeyboardButton(text="others", callback_data=MyCallback(name="family", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="view all book", callback_data=MyCallback(name="all_book", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="Back", callback_data=MyCallback(name="back", id="1").pack()),
            ]
        ]
    )
    await query.message.answer("select catagory of the book you want to rent", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.name == "buy_book"))
async def buy_book(query: CallbackQuery, state: FSMContext) -> None:
    """
    This function will be handled when the buy book is entered
    """
    await query.message.delete()
    await state.update_data(service_type="buy")
    menu = InlineKeyboardMarkup(
        inline_keyboard= [
            [
                InlineKeyboardButton(text="Fiction", callback_data=MyCallback(name="Romantic", id="10").pack()),
                InlineKeyboardButton(text="Educational", callback_data=MyCallback(name="novel", id="10").pack()),
                
            ],
            [
                InlineKeyboardButton(text="spiritual", callback_data=MyCallback(name="biography", id="10").pack()),
                InlineKeyboardButton(text="philosophy", callback_data=MyCallback(name="comedy", id="10").pack()),
                
            ],
            [
                InlineKeyboardButton(text="Business", callback_data=MyCallback(name="fantasy", id="10").pack()),
                InlineKeyboardButton(text="others", callback_data=MyCallback(name="family", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="view all book", callback_data=MyCallback(name="all_book", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="Back", callback_data=MyCallback(name="back", id="1").pack()),
            ]
        ]
    )
    await query.message.answer("select catagory of the book you want to buy", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.id == "10"))
async def process_catagory(query: CallbackQuery, callback_data: MyCallback, state: FSMContext) -> None:
    """
    This function will be handled when the catagory is entered
    """
    await query.message.delete()
    # Get the genre from the callback data
    genre = callback_data.name
    # If the genre is not "all_book", add a condition to the query
    if genre != "all_book":
        books_collection_ref = db.collection('books').where('genre', '==', genre)
    else:
        books_collection_ref = db.collection('books')

    docs = books_collection_ref.stream()

    menu = InlineKeyboardMarkup(
        
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'{doc.to_dict()["title"]}', callback_data=MyCallback(name="book", id=doc.id).pack()),
            ] for doc in docs
        ]
    )
    data = await state.get_data()
    if not data:
        await query.message.answer("no book found")
        return
    await query.message.answer(f"select the book you want to {data['service_type']}", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.name == "book"))
async def process_book(query: CallbackQuery, callback_data: MyCallback, state: FSMContext) -> None:
    """
    this function will be handled when the book is entered
    """
    await query.message.delete()
    book_id = callback_data.id

    # Get a reference to the book document
    book_ref = db.collection('books').document(book_id)

    # Get the book document
    book = book_ref.get()
  
    
    if not book:
        await query.message.answer("book not found")
        return
    book = book.to_dict()
    text = f'title: {book["title"]}\nauthor: {book["author"]}\nedition: {book["date"]}\nprice: {book["price"]}\nstatus: {book["book_status"]}\noverview: {book["overview"]} \ncontact: @SilentERr\ncall : +251953933492'

    data = await state.get_data()

    await query.message.answer(f'{text}',reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                InlineKeyboardButton(text="buy this book", callback_data=MyCallback(name="buy_this_book", id=callback_data.id).pack()) if data['service_type'] == "buy" else InlineKeyboardButton(text="rent this book", callback_data=MyCallback(name="buy_this_book", id=callback_data.id).pack()),    
                InlineKeyboardButton(text="back", callback_data=MyCallback(name="back", id=callback_data.id).pack())
                ]
            ]
        )
    )

@form_router.callback_query(MyCallback.filter(F.name == "buy_this_book"))
async def buy_this_book(query: CallbackQuery, state: FSMContext, callback_data: MyCallback) -> None:
    """
    this function will be handled when the buy is entered"""
    await query.message.delete()
    await state.update_data(book_id=callback_data.id)
    await state.set_state(Book.buyer_name)

    # Get a reference to the book document
    book_ref = db.collection('books').document(callback_data.id)

    # Get the book document
    book = book_ref.get()
    book = book.to_dict()
    await state.update_data(buyer_book_title=book["title"])

    await query.message.answer("Enter your full name please?")

@form_router.message(Book.buyer_name)
async def customer_name(message: Message, state: FSMContext) -> None:
    """
    this function will handle the name of the customer"""
    await state.update_data(buyer_name=message.text)
    await state.set_state(Book.buyer_phone)
    await message.answer("enter your phone number", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="share your phone", request_contact=True)
            ]
        ], resize_keyboard=True, one_time_keyboard=True
    ))

@form_router.message(Book.buyer_phone)
async def customer_phone(message: Message, state: FSMContext) -> None:
    """
    this function will handle the phone of the customer"""
    await state.update_data(buyer_phone=message.contact.phone_number)
    await state.set_state(Book.buyer_address)
    await message.answer("enter your location or share your location", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="share your location", request_location=True)
            ]
        ],resize_keyboard=True, one_time_keyboard=True
    ))
    
# @form_router.message(Book.username)
# async def customer_username(message: Message, state: FSMContext) -> None:
#     """
#     this function will handle the username of the customer"""
#     await state.update_data(username=message.text)
#     await state.set_state(Book.location)
#     await message.answer("enter or share your location please!")

@form_router.message(Book.buyer_address)
async def customer_address(message: Message, state: FSMContext) -> None:
    """
    this function will handle the address of the customer"""
    await state.update_data(buyer_address=message.text)
    await state.set_state(Book.finish)
    buyer_data = await state.get_data()
    
    new_order = {   
        'book_id': buyer_data['buyer_book_title'],
        'username': message.from_user.username,
        'name': buyer_data['buyer_name'],
        'phone_number': buyer_data['buyer_phone'],
        'location': buyer_data['buyer_address'],
        'address': buyer_data['buyer_address'],
        'type': buyer_data['service_type']
    }

    db.collection('orders').add(new_order)

    await message.answer("order added successfully", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="back", callback_data=MyCallback(name="back", id="1").pack())
            ]
        ]
    ))

@form_router.callback_query(MyCallback.filter(F.name == "sell_book"))
async def sell_book(query: CallbackQuery, state: FSMContext) -> None:
    """
    this function will be handled when the sell is enterd"""
    await query.message.delete()
    await state.set_state(Book.title)
    await query.message.answer("enter the title of the book")
 
@form_router.message(Book.title)
async def book_title(message: Message, state: FSMContext) -> None:
    """
    this function will handle the title of the book"""
    await state.update_data(title=message.text)
    await state.set_state(Book.image)
    await message.answer("upload image please")

@form_router.message(Book.image)
async def book_image(message: Message, state: FSMContext) -> None:
    """
    this function will handle the image of the book"""
    if message.photo is None:
        await message.answer("Invalid input upload image please")
        await state.set_state(Book.image)
        return
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(Book.phone)
    await message.answer("share your number please", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="share your phone", request_contact=True)
            ]
        ], resize_keyboard=True
    ))
    
@form_router.message(Book.phone)
async def book_author(message: Message, state: FSMContext) -> None:
    """
    this function will handle the author of the book"""
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(Book.price)
    await message.answer("enter the price of the book")

@form_router.message(Book.price)
async def book_price(message: Message, state: FSMContext) -> None:
    """
    this function will handle the price of the book"""
    await state.update_data(price=message.text)
    await state.set_state(Book.status)
    await message.answer("Enter the status of the book")

@form_router.message(Book.status)
async def book_date(message: Message, state: FSMContext) -> None:
    """
    this function will handle the date of the book"""
    await state.set_state(Book.finish)
    await state.update_data(date=message.text)
    book_data = await state.get_data()

    
        # Create a new sell
    new_sell = {
        'title': book_data['title'],
        'author': "unknown",
        'image': book_data["image"],
        'status': book_data["date"],
        'price': book_data["price"],
        'phone': book_data["phone"],
    }

    # Add the new sell to the 'sells' collection
    db.collection('sells').add(new_sell)


    await message.answer("book added successfully, the admin will contact you", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="back", callback_data=MyCallback(name="back", id="1").pack())
            ]
        ]
    ))

@form_router.callback_query(MyCallback.filter(F.id == 111))
@form_router.message(Book.genre)
async def book_genre(query: CallbackQuery, state: FSMContext, callback_data: MyCallback) -> None:
    """
    this function will handle the genre of the book"""
    await query.message.delete()
    await state.update_data(genre=query.message.text if query.message.text else callback_data.name)
    await state.set_state(Book.price)
    await query.message.answer("enter the price of the book")

# @form_router.message(Book.price)
# async def book_price(message: Message, state: FSMContext) -> None:
#     """
#     this function will handle the price of the book"""
#     await state.update_data(price=message.text)
#     await state.set_state(Book.book_status)
#     await message.answer("enter the status of the book")

@form_router.message(Book.book_status)
async def book_book_status(message: Message, state: FSMContext) -> None:
    """
    this function will handle the status of the book"""
    await state.update_data(book_status=message.text)
    book_data = await state.get_data()
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO books (title, author, image, date, overview, num_of_pages, genre, price, book_status, rating, amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            book_data['title'],
            book_data['author'],
            book_data["image"] ,
            book_data["date"] ,
            book_data["overview"] ,
            book_data["num_of_pages"] ,
            book_data["genre"] ,
            book_data["price"] ,
            book_data["book_status"] ,
            0 ,
            1,
            )
    )
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer("book added successfully", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="back", callback_data=MyCallback(name="back", id="1").pack())
            ]
        ]
    )
    )
@form_router.message(Book.finish)
async def finish(message: Message, state: FSMContext) -> None:
    """
    this function will be handled when the finish is entered"""
    await message.delete()
  
    menu =InlineKeyboardMarkup (
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Buy Book", callback_data=MyCallback(name="buy_book", id="1").pack()),
                InlineKeyboardButton(text="Rent Book", callback_data=MyCallback(name="rent_book", id="2").pack()),
            ],
            [
                InlineKeyboardButton(text="Sell Book", callback_data=MyCallback(name="sell_book", id="3").pack()),
                InlineKeyboardButton(text="Order new", callback_data=MyCallback(name="order_book", id="4").pack()),
            ]
            ], resize_keyboard=True
    )
   
    await message.answer("Invalid input please select from the menu", reply_markup=menu)

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())