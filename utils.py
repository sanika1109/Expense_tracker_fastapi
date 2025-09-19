# Helper functions 

import json

# logic to load data from json file
def load_data():
        with open('expenses.json') as f:
             data=json.load(f)
        return data
print(load_data())  # load data from json file     

# LOGIC TO INSERT DATA INTO JSON FILE
def save_to_json(data):
    with open('expenses.json','w') as f:
        json.dump(data, f, default=str, indent=4)

# logic to calculate total expenses
def calculate_total_expenses(data):
    total=sum(item['amount'] for item in data.values())
    return total