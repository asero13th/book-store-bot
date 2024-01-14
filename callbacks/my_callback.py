"""
a module for call back functions"""
from aiogram.filters.callback_data import CallbackData
class MyCallback(CallbackData, prefix="my"):
    """
    my call back class 
    """
    name: str
    id:str