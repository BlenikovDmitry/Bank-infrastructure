from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

"""
запуск на локальной машине
python -m uvicorn server:app --reload
"""

app = FastAPI()

class login_request(BaseModel):
    login: str
    password: str


SECRET_KEY = '12345'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


    except jwt.PyJWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Невалидный токен"
            )

@app.get("/")
def root():
    return {"Message: привет"}


@app.post("/login")
def autorization(data: login_request):
    if data.login == "user" and data.password == "1234":
        access_token = create_access_token(data={"sub":data.login})
        return {
            "access_token":access_token,
            "token_type": "bearer"

            }
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Неверный логин или пароль"
        )

@app.get("/get_user")
def get_current_user(username: str = Depends(get_user_from_token)):
    return {"data": "Тут типа данные текущего юзверя"}

@app.get("/accounts")
def get_all_accounts(username: str = Depends(get_user_from_token)):
    return {"Тут типа все счета юзверя"}

@app.get("/transactions")
def get_all_transactions(username: str = Depends(get_user_from_token)):
    return {"Тут типа все транзакции"}

