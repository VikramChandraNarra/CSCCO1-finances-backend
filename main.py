from flask import Flask, jsonify, request, abort
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime

import uuid  # Use uuid for generating unique IDs

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


# Mock Data
users = [
    {
        "userId": str(uuid.uuid4()),
        "name": "John Doe",
        "email": "john@example.com",
        "password": generate_password_hash("1234")
    },
    {
        "userId": str(uuid.uuid4()),
        "name": "Jane Smith",
        "email": "jane@example.com",
        "password": generate_password_hash("1234")
    }
]

budgets = [
    {
        "budgetId": str(uuid.uuid4()),
        "userId": users[0]["userId"],
        "income": 5000,
        "expenses": [
            {
                "category": "Rent",
                "amount": 1200,
                "date": str(datetime.now()),
                "note": "Monthly rent"
            },
            {
                "category": "Food",
                "amount": 300,
                "date": str(datetime.now()),
                "note": "Groceries"
            }
        ],
        "savings": 500,
        "createdAt": str(datetime.now())
    },
    {
        "budgetId": str(uuid.uuid4()),
        "userId": users[0]["userId"],
        "income": 6000,
        "expenses": [
            {
                "category": "Travel",
                "amount": 800,
                "date": str(datetime.now()),
                "note": "Vacation"
            },
            {
                "category": "Utilities",
                "amount": 150,
                "date": str(datetime.now()),
                "note": "Electricity bill"
            }
        ],
        "savings": 1000,
        "createdAt": str(datetime.now())
    },
    {
        "budgetId": str(uuid.uuid4()),
        "userId": users[1]["userId"],
        "income": 4500,
        "expenses": [
            {
                "category": "Rent",
                "amount": 1100,
                "date": str(datetime.now()),
                "note": "Monthly rent"
            },
            {
                "category": "Food",
                "amount": 250,
                "date": str(datetime.now()),
                "note": "Groceries"
            }
        ],
        "savings": 700,
        "createdAt": str(datetime.now())
    },
    {
        "budgetId": str(uuid.uuid4()),
        "userId": users[1]["userId"],
        "income": 5500,
        "expenses": [
            {
                "category": "Travel",
                "amount": 500,
                "date": str(datetime.now()),
                "note": "Weekend trip"
            },
            {
                "category": "Entertainment",
                "amount": 200,
                "date": str(datetime.now()),
                "note": "Movie night"
            }
        ],
        "savings": 800,
        "createdAt": str(datetime.now())
    }
]

# API Endpoints

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    print("Request Body (Signup):", data)  # Log request body
    if not all(key in data for key in ["name", "email", "password"]):
        abort(400, description="Missing required fields")
    if any(user['email'] == data['email'] for user in users):
        abort(400, description="Email already exists")
    new_user = {
        "userId": str(uuid.uuid4()),
        "name": data['name'],
        "email": data['email'],
        "password": generate_password_hash(data['password'])
    }
    users.append(new_user)
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print("Request Body (Login):", data)  # Log request body
    if not all(key in data for key in ["email", "password"]):
        abort(400, description="Missing email or password")
    user = next((u for u in users if u["email"] == data["email"]), None)
    if not user or not check_password_hash(user["password"], data["password"]):
        abort(401, description="Invalid email or password")
    return jsonify({"userId": user["userId"]}), 200

# 1. Get all users
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

# 2. Get a user by ID
@app.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = next((u for u in users if u["userId"] == user_id), None)
    if not user:
        abort(404, description="User not found")
    return jsonify(user), 200

# 3. Get all budgets for a user
@app.route('/users/<user_id>/budgets', methods=['GET'])
def get_budgets_by_user(user_id):
    user_budgets = [b for b in budgets if b["userId"] == user_id]
    if not user_budgets:
        abort(404, description="No budgets found for this user")
    return jsonify(user_budgets), 200

# 4. Add a new budget
@app.route('/budgets', methods=['POST'])
def add_budget():
    data = request.json
    print("Request Body (Add Budget):", data)  # Log request body
    if "userId" not in data or "income" not in data or "expenses" not in data:
        abort(400, description="Missing required fields")
    # Parse dates in expenses
    for expense in data["expenses"]:
        try:
            # Ensure date is in ISO format
            datetime.strptime(expense["date"], "%Y-%m-%d")
        except ValueError:
            expense["date"] = str(datetime.now())
    new_budget = {
        "budgetId": str(uuid.uuid4()),
        "userId": data["userId"],
        "income": data["income"],
        "expenses": data["expenses"],
        "savings": data.get("savings", 0),
        "createdAt": str(datetime.now())
    }
    budgets.append(new_budget)
    return jsonify(new_budget), 201

# 5. Update a budget by ID
@app.route('/budgets/<budget_id>', methods=['PUT'])
def update_budget(budget_id):
    data = request.json
    print("Request Body (Update Budget):", data)  # Log request body
    budget = next((b for b in budgets if b["budgetId"] == budget_id), None)
    if not budget:
        abort(404, description="Budget not found")
    # Update only the allowed fields
    for key in ['income', 'expenses', 'savings']:
        if key in data:
            budget[key] = data[key]
    return jsonify(budget), 200

# 6. Delete a budget by ID
@app.route('/budgets/<budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    global budgets
    budget = next((b for b in budgets if b["budgetId"] == budget_id), None)
    if not budget:
        abort(404, description="Budget not found")
    budgets = [b for b in budgets if b["budgetId"] != budget_id]
    return jsonify({"message": "Budget deleted successfully"}), 200



@app.route('/budgets/<budget_id>/expenses/<int:expense_index>', methods=['DELETE'])
def delete_expense(budget_id, expense_index):
    budget = next((b for b in budgets if b["budgetId"] == budget_id), None)
    if not budget:
        abort(404, description="Budget not found")
    if 0 <= expense_index < len(budget["expenses"]):
        del budget["expenses"][expense_index]
        return jsonify({"message": "Expense deleted successfully"}), 200
    else:
        abort(404, description="Expense not found")
if __name__ == '__main__':
    app.run(debug=True)
