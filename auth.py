#This file holds the secret key for signing tokens
#It also holds a fake user database with 2 roles and respectively 2 users.
import jwt#JSON Web Token
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()

#Global constants — loaded from environment variables
secret_key = os.environ.get("JWT_SECRET_KEY", "clinicalshield-cs-key")
algo= "HS256" #HMAC-SHA256, conventionally used for JWT

#Creating the fake user database
users = {
    "patient_u": {"password": os.environ.get("PATIENT_PASSWORD", "patient123"), "role": "patient"},
    "doctor_u": {"password": os.environ.get("DOCTOR_PASSWORD", "doc123"), "role": "practitioner"}
}

#Pydantic model for API request validation
class TokenReq(BaseModel):
    username : str
    password : str

#defining a variable for API routing
router = APIRouter()

#Defining the endpoint
@router.post("/auth/token")
def get_token(body : TokenReq):
    if body.username not in users:
        raise HTTPException(status_code=401, detail="Invalid Credentials :(")
    else:
        if body.password != users[body.username]["password"]:
            raise HTTPException(status_code=401, detail="Invalid Credentials bro!")
    
    role = users[body.username]["role"] #fetching the role
    payload = {
        "sub":body.username,
        "role" :role,
        "exp" : datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(payload, secret_key, algo)
    return {
        "access_token" : token,
        "token_type" : "Bearer"
    }

#Dependency function for verification
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)): #Ideal value for authorisation -----> "Bearer ezy1f0XAi"
    token = credentials.credentials
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return decoded