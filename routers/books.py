from fastapi import APIRouter, HTTPException, Query, Path, Depends
from models import OutputSchema, AllBooksOutputSchema, Book
from utils import search_book, get_db
from typing import Any
from pymongo import ReturnDocument

router = APIRouter(prefix="/books",tags=["Book Management"])


@router.put('/update_book/{book_id}', response_model=OutputSchema)
async def update_book(new_book: Book, book_id: int = Path(..., gt=0), collection: Any = Depends(get_db)):
    # book = search_book(database, search_id=book_id)
    updated_book = await collection.find_one_and_update(
    {"book_id": book_id},
    {"$set": new_book.model_dump()},
    return_document=ReturnDocument.AFTER  # This is the magic line!
    )

    if updated_book:
        # updated_book is now the dictionary of the book *after* the change
        return {
            "message": f"Updated book {book_id}",
            "book_id": updated_book["book_id"],
            "title": updated_book["title"],
            "chapter_no": updated_book["chapter_no"],
            "pg_no": updated_book["pg_no"]
        }
    else:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found in the database!")
    

@router.delete('/delete_book/{book_id}', response_model=OutputSchema)
async def delete_book(book_id: int = Path(..., gt=0), collection: Any = Depends(get_db)):
    # book = search_book(database, search_id=book_id)
    deleted_book = await collection.find_one_and_delete({"book_id": book_id})
    if deleted_book:
        # database.remove(book)
        return {
            "message": f"Deleted {book_id} with Topic: '{deleted_book["title"]}' from the database!",
            "book_id": book_id,
            "title": deleted_book["title"]
        }
    else:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found in the Database!")

@router.post('/save_book/{book_id}', response_model=OutputSchema)
async def save_book( book: Book, book_id: int = Path(..., gt=0), search_keyword: str | None = Query(default=None, min_length=3), collection: Any = Depends(get_db)):
    # Result Dictionary
    resDict = {"message": "custom msg", 
                "book_id": book_id,
                "title": book.title}
    
    # check if the book_id already exists in the db
    check_book_id = await collection.count_documents({"book_id": book_id}, limit = 1)
    if check_book_id > 0:
        raise HTTPException(status_code=409, detail="Book with same book_id already exists in the Database!")
    
    if search_keyword:
        searchedBook = await search_book(collection, search_keyword)
        if searchedBook:
            resDict["message"] = f"found {search_keyword} in Book Title {searchedBook["title"]}"
            resDict["book_id"] = searchedBook["book_id"]
            resDict["title"] = searchedBook["title"]
            return resDict
    
        
    # Saving a book to the DB
    result = await collection.insert_one({**book.model_dump(),
                     "book_id": book_id})
    
    if result.acknowledged:
        # Now we know the data is safe in Atlas!
        resDict["message"] = f"Heres the book {book_id} with chapter {book.chapter_no} and page {book.pg_no} open with the title {book.title}"
        return resDict
    else:
        raise HTTPException(status_code=500, detail="The server encountered an error and cound not complete you request!")


@router.get('/all-books', response_model=list[AllBooksOutputSchema])
async def allBooks(collection: Any = Depends(get_db)):
    # # for just printing in the log/terminal
    # for book in database:
    #     print(f"Book ID {book["book_id"]} with Title {book["title"]}")
    books_cursor = collection.find({}, {"_id": 0})
    database = await books_cursor.to_list(length = 100)
    
    
    return database