from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from jose import JWTError, jwt

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

# Secret key for encoding/decoding JWT tokens
SECRET_KEY = "your-secret-key"

# Create an instance of HTTPBearer for JWT token verification
bearer_scheme = HTTPBearer()

# Function to validate JWT token
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    for user in db:
        if user.email == email:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to create a new user (no authentication required)
@app.post("/users/", response_model=User)
async def create_user(user: User):
    # Check if the email already exists
    for existing_user in db:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    # If the email doesn't exist, add the user to the database
    db.append(user)
    return user

# Endpoint to get a user by email (authentication required)
@app.get("/users/{email}", response_model=User)
async def get_user(email: str, current_user: User = Depends(get_current_user)):
    return current_user

# Endpoint to add an address to a user (authentication required)
@app.post("/users/{email}/addresses/", response_model=User)
async def add_address_to_user(email: str, address: Address, current_user: User = Depends(get_current_user)):
    for user in db:
        if user.email == email:
            user.addresses.append(address)
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to update a user's address (authentication required)
@app.put("/users/{email}/addresses/{address_index}", response_model=User)
async def update_address(email: str, address_index: int, address: Address, current_user: User = Depends(get_current_user)):
    for user in db:
        if user.email == email:
            if 0 <= address_index < len(user.addresses):
                user.addresses[address_index] = address
                return user
            else:
                raise HTTPException(status_code=404, detail="Address not found")
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to delete a user's address (authentication required)
@app.delete("/users/{email}/addresses/{address_index}", response_model=User)
async def delete_address(email: str, address_index: int, current_user: User = Depends(get_current_user)):
    for user in db:
        if user.email == email:
            if 0 <= address_index < len(user.addresses):
                del user.addresses[address_index]
                return user
            else:
                raise HTTPException(status_code=404, detail="Address not found")
    raise HTTPException(status_code=404, detail="User not found")

# Endpoint to get all users (authentication required)
@app.get("/users/", response_model=List[User])
async def get_all_users(current_user: User = Depends(get_current_user)):
    return db
