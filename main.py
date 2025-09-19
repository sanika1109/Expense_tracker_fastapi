from fastapi import FastAPI,Path,HTTPException,Query
from datetime import datetime ,date 
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel,Field,computed_field
from typing import List,Dict,Optional,Annotated,Literal
import json, requests, time
from utils import * # import all functions from utils.py
from schema.pydantic_models import * # import all pydantic models from pydantic_models.py
import sqlite3
app=FastAPI()


@app.get('/')  #Human readable endpoint
def home():
     return {'messages':"Welcome to Expense Tracker API"}

@app.get('/health') #machine readable endpoint # for cloud services
def health_check():
     return {'status':'ok'}

@app.get("/get_expenses")
def get_expenses():
     try:
          data=load_data()
     except Exception as e:
          return {'error':str(e)}
     
     return data

@app.get('/get_expense/{expense_id}')
def get_expense(expense_id:str=Path(...,title="Expense id",description="Enter the id of expense",examle='e_001')):
     try:
          data=load_data()
     except Exception as e:
          return {'error':str(e)}
     
     if expense_id in data:
          return data[expense_id]
     else:
          return {'error':'Expense not found'}

@app.post('/add_expense')
def add_expense(expense:Expense): # expense is an instance of Expense model
          try:
               data=load_data()
          except Exception as e:
               return {'error':str(e)}
     
          print(data)
          if expense.id in data:
               raise HTTPException(status_code=400,detail="expense with this id already exists")
          
          data[expense.id]=expense.model_dump(exclude=['id']) #exclude id field from model_dump
          print('****'*15)
          print(data)
          try:
               save_to_json(data)
          except Exception as e:
                    return {'error':str(e)}
          try:
               total_expense=calculate_total_expenses(data)
          except Exception as e:
               return {'error':str(e)}
          
          return {"message":"Expense added successfully","Your Total Expense ":total_expense}
          # return JSONResponse(status_code=202,content={"message":"Expense added successfully"})

     
@app.put('/update_expense/{expense_id}')
def update_expense(expense_id:str,expense_update:UpdateExpense):
     try:
          data=load_data()
     except Exception as e:
          return {'error':str(e)}
     
     if expense_id not in data:
          raise HTTPException(status_code=404,detail={"message":"Expense not found"})
     existing_expense_info=data[expense_id]
     print('***'*20)
     print('Existing Expense Info:', existing_expense_info)  # Debugging line to check existing expense info
     
     updated_expense_info=expense_update.model_dump(exclude_unset=True)
     print('Updated Expense Info:', updated_expense_info)

     for key,value in updated_expense_info.items():
          existing_expense_info[key]=value
          print('*'*20)
          print(existing_expense_info)
        #   data[expense_id]=existing_expense_info
     data[expense_id]=existing_expense_info

     # Save updated data to JSON file
     try:
          save_to_json(data)
     except Exception as e:
          return {'error':str(e)}
     # Calculate total expenses
     try:
          total_expense=calculate_total_expenses(data)
     except Exception as e:
          return {'error':str(e)}
     
     return {"message":"Expense updated successfully","Updated Expense Info":existing_expense_info,"your total expense ":total_expense}
          

@app.delete('/delete_expense/{expense_id}')
def delete_expense(expense_id:str):
     try:
      data=load_data()
     except Exception as e:
      return {'error':str(e)}
     
     if expense_id not in data:
          raise HTTPException(status_code=404,detail={'messge':'Expense id not found'})
     del data[expense_id]
     print('****'*20)
     print(data)
     try:
          save_to_json(data)
     except Exception as e:
          return {'error':str(e)}
     try:
          total_expense=calculate_total_expenses(data)
     except Exception as e:
          return {'error':str(e)}
     
     return {'message':'Expense daleted successfully','Your Total Expense ':total_expense}
     



@app.get('/get_expense_by_range')
def get_expense_by_range(
    start_date: str = Query(..., description="Enter the start date in YYYY-MM-DD format"),
    end_date: str = Query( date.today().strftime("%Y-%m-%d"), description="Enter the end date in YYYY-MM-DD format"),
):
     try:
          data = load_data()
     except Exception as e:
          return {'error':str(e)}
     
     filtered_expenses = {}


     # Convert user input to datetime
     try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
     except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

     for key, value in data.items():
         try:
            expense_date = datetime.fromisoformat(value["date"])  # handles both YYYY-MM-DD and full ISO format
         except ValueError:
            continue  # skip if date is invalid
         
        # Normalize: drop timezone info if present
         if expense_date.tzinfo is not None:
            expense_date = expense_date.replace(tzinfo=None)

         if start_dt <= expense_date <= end_dt:
            filtered_expenses[key] = value

     if not filtered_expenses:
         raise HTTPException(status_code=404, detail="No expenses found in this date range")
     
     print('filterd expenses:', filtered_expenses)

     total_expenses=calculate_total_expenses(filtered_expenses)
     print('Total expenses in this date range:', total_expenses)
     print('****'*20)
     print(start_date.split('-')[1])
     print(type(start_date),type(end_date))

     return JSONResponse(
         status_code=200,
         content={'message':'Expenses fetched successfully',
                  f'Your total expenses in {start_date} to {end_date} date range':total_expenses}
     )


@app.get('/get_expense_by_month')
def get_expense_by_month(
    month: str = Query(..., description="Enter the month in MM format"),
    year: str = Query(..., description="Enter the year in YYYY format"),
):   
     try:
          data = load_data()
     except Exception as e:
          return {'error':str(e)}
     
     filtered_expenses = {}

     for key , value in data.items():
          if value['date'].split('-')[1]==month and value['date'].split('-')[0]==year:
               filtered_expenses[key]=value
     if not filtered_expenses:
          raise HTTPException(status_code=404,detail="No expenses found in this month")
     total_expenses=calculate_total_expenses(filtered_expenses)
     return JSONResponse(
          status_code=200,
          content={'message':'Expenses fetched successfully',
                   f'Your total expenses in  {month}/{year}':total_expenses}     
     )


if __name__=='__main__':
     uvicorn.run("main:app",host='127.0.0.1',port=5000,reload=True)

     # this code will only run when we run this file directly, not when we import it
     # here we can also do a function call