from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Define a Pydantic model for Address
class Address(BaseModel):
    street: str
    city: str
    district: str
    state: str
    zip_code: str

# Define a Pydantic model for User
class User(BaseModel):
    firstname: str
    lastname: str
    phonenumber: str
    email: str
    addresses: List[Address] = []

# In-memory database to store users
db = []

# Endpoint to create a new user
@app.post("/users/", response_model=User)
async def create_user(user: User):
    # Check if the email already exists
    for existing_user in db:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    # If the email doesn't exist, add the user to the database
    db.append(user)
    return user

# Endpoint to get a user by email
@app.get("/users/{email}", response_model=User)
async def get_user(email: str):
    for user in db:
        if user.email == email:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to add an address to a user
@app.post("/users/{email}/addresses/", response_model=User)
async def add_address_to_user(email: str, address: Address):
    for user in db:
        if user.email == email:
            user.addresses.append(address)
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to update a user's address
@app.put("/users/{email}/addresses/{address_index}", response_model=User)
async def update_address(email: str, address_index: int, address: Address):
    for user in db:
        if user.email == email:
            if 0 <= address_index < len(user.addresses):
                user.addresses[address_index] = address
                return user
            else:
                raise HTTPException(status_code=404, detail="Address not found")
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to delete a user's address
@app.delete("/users/{email}/addresses/{address_index}", response_model=User)
async def delete_address(email: str, address_index: int):
    for user in db:
        if user.email == email:
            if 0 <= address_index < len(user.addresses):
                del user.addresses[address_index]
                return user
            else:
                raise HTTPException(status_code=404, detail="Address not found")
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to get all users
@app.get("/users/", response_model=List[User])
async def get_all_users():
    return db
