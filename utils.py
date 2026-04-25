import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from fastapi import Depends
from typing import Any

load_dotenv() # This loads the variables from .env

# Get the connection string from .env
MONGODB_URL = os.getenv("MONGODB_CONECTION_STRING")

# Create the client and select the database
client = AsyncIOMotorClient(MONGODB_URL)
db = client.library_db
collection = db.books

async def get_db():
    # In MongoDB, we return the collection we want to work with
    return collection
    

# database = []

# def get_db():
#     return database

# def search_book(database: list[dict[str, any]], search_keyword: str | None = None, search_id: int | None = None):
#     if search_keyword:
#         for book in database:
#             if search_keyword in book["title"]:
#                 return book
#     if search_id:
#         for book in database:
#             if book["book_id"] == search_id:
#                 return book
#     return None


async def search_book(collection, search_keyword: str | None = None, search_id: int | None = None):
    if search_keyword:
        # We look for the keyword anywhere in the title, case-insensitive
        return await collection.find_one({"title": {"$regex": search_keyword, "$options": "i"}})
    
    if search_id:
        return await collection.find_one({"book_id": search_id})
    
    return None
