from fastapi import FastAPI, HTTPException, Depends  # Import FastAPI, HTTPException for error handling, and Depends for dependencies.
from models.expense import Expense  # Import Expense model, assumed to be a Pydantic model for validation.
from database.db import get_db  # Import get_db, a dependency function for database connections.
from bson import ObjectId  # Import ObjectId for handling MongoDB object IDs.
from fastapi.responses import JSONResponse  # Import JSONResponse to send JSON formatted responses.
from fastapi.encoders import jsonable_encoder  # Import jsonable_encoder to convert data for JSON response.



app = FastAPI()  # Create a FastAPI application instance.





class ExpenseHandler:  # Define a class to manage expense operations.
    def __init__(self, database):  # Initialize with database connection.
        self.db = database  # Store database connection.

    async def get_all_expenses(self):  # Asynchronously retrieve all expenses.
        expenses = await self.db["expense"].find().to_list(None)  # Query all expenses from the database.
        return expenses  # Return the list of expenses.

    async def create_expense(self, expense: Expense):  # Asynchronously create an expense.
        result = await self.db["expense"].insert_one(expense.dict())  # Insert expense into the database.
        expense_id = result.inserted_id  # Get the ID of the inserted expense.
        return {'message': 'Expense created successfully.', 'id': str(expense_id)}  # Return success message and ID.

    async def delete_expense(self, expense_id: str):  # Asynchronously delete an expense.
        result = await self.db["expense"].delete_one({"_id": ObjectId(expense_id)})  # Delete the expense by ID.
        if result.deleted_count == 0:  # Check if the expense was found and deleted.
            raise HTTPException(status_code=404, detail="Expense not found")  # Raise an error if no expense was deleted.
        return {'message': 'Expense deleted successfully.'}  # Return a success message.
    
    
    
    
    
    

# Endpoint definitions
@app.get("/expenses/", response_class=JSONResponse)  # Define a GET endpoint for retrieving expenses.
async def get_expenses(db=Depends(get_db)):  # Dependency injection for database connection.
    handler = ExpenseHandler(db)  # Instantiate ExpenseHandler with database.
    expenses = await handler.get_all_expenses()  # Get all expenses.
    
    # Convert MongoDB ObjectId to string for each expense.
    for expense in expenses:
        if '_id' in expense:
            expense['_id'] = str(expense['_id'])
    
    # Convert expenses to JSON compatible format using jsonable_encoder.
    json_compatible_item_data = jsonable_encoder(expenses)
    return JSONResponse(content=json_compatible_item_data)  # Return the JSON response.

@app.post("/expenses/", status_code=201)  # Define a POST endpoint to create an expense.
async def create_expense_route(expense: Expense, db=Depends(get_db)):  # Receive expense data and database dependency.
    handler = ExpenseHandler(db)  # Instantiate the handler.
    return await handler.create_expense(expense)  # Create the expense and return the result.

@app.delete("/expenses/{expense_id}", status_code=204)  # Define a DELETE endpoint for deleting an expense.
async def delete_expense_route(expense_id: str, db=Depends(get_db)):  # Get expense_id and database dependency.
    handler = ExpenseHandler(db)  # Instantiate the handler.
    return await handler.delete_expense(expense_id)  # Delete the expense and return the result.
