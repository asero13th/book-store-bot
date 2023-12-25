"""
this is out main.py file"""
import os
import asyncio
import logging
import sys
import sqlite3
from aiogram.filters import  CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F, Router

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from aiogram.types import CallbackQuery
from dotenv import load_dotenv
from callbacks.my_callback import MyCallback
from forms.book import Book
from forms.customer import Customer

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
    user = "adminfhf"
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
          InlineKeyboardButton(text="orders", callback_data=MyCallback(name="order", id="4").pack()),  
        ])
    await message.answer("welcome to ብርሀን መፅሐፍ ማከፋፈያ", reply_markup=menu)
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
                InlineKeyboardButton(text="Romantic", callback_data=MyCallback(name="Romantic", id="10").pack()),
                InlineKeyboardButton(text="novel", callback_data=MyCallback(name="novel", id="10").pack()),
                InlineKeyboardButton(text="Fantasy", callback_data=MyCallback(name="fantasy", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="Biography", callback_data=MyCallback(name="biography", id="10").pack()),
                InlineKeyboardButton(text="comedy", callback_data=MyCallback(name="comedy", id="10").pack()),
                InlineKeyboardButton(text="family", callback_data=MyCallback(name="family", id="10").pack())
            ],
             [
                InlineKeyboardButton(text="spritual", callback_data=MyCallback(name="spritual", id="10").pack()),
                InlineKeyboardButton(text="reality", callback_data=MyCallback(name="reality", id="10").pack()),
                InlineKeyboardButton(text="thriller", callback_data=MyCallback(name="thriller", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="western", callback_data=MyCallback(name="western", id="10").pack()),
                InlineKeyboardButton(text="science fiction", callback_data=MyCallback(name="science_fiction", id="10").pack()),
                InlineKeyboardButton(text="mystry", callback_data=MyCallback(name="mystry", id="10").pack())
            ]
        ]
    )
    await query.message.answer("choose the genre", reply_markup=menu)


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
                InlineKeyboardButton(text="Romantic", callback_data=MyCallback(name="Romantic", id="10").pack()),
                InlineKeyboardButton(text="novel", callback_data=MyCallback(name="novel", id="10").pack()),
                InlineKeyboardButton(text="Fantasy", callback_data=MyCallback(name="fantasy", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="Biography", callback_data=MyCallback(name="biography", id="10").pack()),
                InlineKeyboardButton(text="comedy", callback_data=MyCallback(name="comedy", id="10").pack()),
                InlineKeyboardButton(text="family", callback_data=MyCallback(name="family", id="10").pack())
            ],
             [
                InlineKeyboardButton(text="spritual", callback_data=MyCallback(name="spritual", id="10").pack()),
                InlineKeyboardButton(text="reality", callback_data=MyCallback(name="reality", id="10").pack()),
                InlineKeyboardButton(text="thriller", callback_data=MyCallback(name="thriller", id="10").pack())
            ],
            [
                InlineKeyboardButton(text="western", callback_data=MyCallback(name="western", id="10").pack()),
                InlineKeyboardButton(text="science fiction", callback_data=MyCallback(name="science_fiction", id="10").pack()),
                InlineKeyboardButton(text="mystry", callback_data=MyCallback(name="mystry", id="10").pack())
            ]
        ]
    )
    await state.set_state(Book.buy)
    await query.message.answer("choose the genre of the book", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.id == 10))
async def process_catagory(query: CallbackQuery, callback_data: MyCallback) -> None:
    """
    This function will be handled when the catagory is entered
    """
    await query.message.delete()
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM books WHERE genre = ?
        """,
        (callback_data.name,)
    )

    books = cursor.fetchall()
    conn.close()

    menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=book[1], callback_data=MyCallback(name="book", id=book[0]).pack()) for book in books
            ]
        ]
    )
    if not books:
        await query.message.answer("no books found with this category")
    else:
        await query.message.answer("choose the book", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.name == "book"))
async def process_book(query: CallbackQuery, callback_data: MyCallback) -> None:
    """
    this function will be handled when the book is entered"""
    await query.message.delete()
    book_id = callback_data.id

    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM books WHERE book_id = ?
        """,
        (book_id,)
    )
    
    book = cursor.fetchone()
    conn.close()

    text = f'title: {book[1]}\nauthor: {book[2]}\ndate: {book[4]}\nprice: {book[8]}\nstatus: {book[9]}\noverview: {book[5]} \ncontact: @SilentERr\ncall : +251953933492'
    await query.message.answer_photo(
        photo=book[3],caption=f'{text}',reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                InlineKeyboardButton(text="buy this book", callback_data=MyCallback(name="buy_this_book", id=book[0]).pack()),
                InlineKeyboardButton(text="back", callback_data=MyCallback(name="back", id=book[0]).pack())
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
    await state.set_state(Book.name)
    await query.message.answer("Enter your full name please?")

@form_router.message(Book.name)
async def customer_name(message: Message, state: FSMContext) -> None:
    """
    this function will handle the name of the customer"""
    await state.update_data(name=message.text)
    await state.set_state(Book.phone)
    await message.answer("enter your phone number", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="share your phone", request_contact=True)
            ]
        ], resize_keyboard=True, one_time_keyboard=True
    ))

@form_router.message(Book.phone)
async def customer_phone(message: Message, state: FSMContext) -> None:
    """
    this function will handle the phone of the customer"""
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(Book.location)
    await message.answer("enter your location or share your location", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="share your location", request_location=True)
            ]
        ],resize_keyboard=True, one_time_keyboard=True
    ))

@form_router.message(Book.location)
async def customer_location(message: Message, state: FSMContext) -> None:
    """
    this function will handle the location of the customer"""
    await state.update_data(location=message.text)
    await state.set_state(Book.address)
    await message.answer("enter your specific address")

@form_router.message(Book.address)
async def customer_address(message: Message, state: FSMContext) -> None:
    """
    this function will handle the address of the customer"""
    await state.update_data(address=message.text)
    buyer_data = await state.get_data()
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()

    cursor.execute(
     # i want to insert the order in orders database
        """
        INSERT INTO orders (book_id, name, phone, location, address,type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            buyer_data['book_id'],
            buyer_data['name'],
            buyer_data['phone'],
            buyer_data['location'],
            buyer_data['address'],
            buyer_data['service_type']
        )
    )
    
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
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(Book.author)
    await message.answer("enter the auther of the book")
    
@form_router.message(Book.author)
async def book_author(message: Message, state: FSMContext) -> None:
    """
    this function will handle the author of the book"""
    await state.update_data(author=message.text)
    await state.set_state(Book.date)
    await message.answer("enter the date of the book")

@form_router.message(Book.date)
async def book_date(message: Message, state: FSMContext) -> None:
    """
    this function will handle the date of the book"""
    await state.update_data(date=message.text)
    await state.set_state(Book.overview)
    await message.answer("enter the overview of the book")

@form_router.message(Book.overview)
async def book_overview(message: Message, state: FSMContext) -> None:
    """
    this function will handle the overview of the book"""
    await state.update_data(overview=message.text)
    await state.set_state(Book.num_of_pages)
    await message.answer("enter the number of pages of the book")

@form_router.message(Book.num_of_pages)
async def book_num_of_pages(message: Message, state: FSMContext) -> None:
    """
    this function will handle the number of pages of the book"""
    await state.update_data(num_of_pages=message.text)
    await state.set_state(Book.genre)
    await message.answer("enter the genre of the book")

@form_router.message(Book.genre)
async def book_genre(message: Message, state: FSMContext) -> None:
    """
    this function will handle the genre of the book"""
    await state.update_data(genre=message.text)
    await state.set_state(Book.price)
    await message.answer("enter the price of the book")

@form_router.message(Book.price)
async def book_price(message: Message, state: FSMContext) -> None:
    """
    this function will handle the price of the book"""
    await state.update_data(price=message.text)
    await state.set_state(Book.book_status)
    await message.answer("enter the status of the book")

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

    await state.set_state(Book.finish)
    await message.answer("book added successfully")

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())