from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import bdfunctions as bd


app = FastAPI()

#пользователь
class User(BaseModel):
    id: int
    email: str
    fullname: str
    role_: str
    is_active: int

#счет
class Account(BaseModel):
    id1: int
    balance: int

#платеж
class Payment(BaseModel):
    id1: int
    pay: int


users_list: list[User] = []
'''
создаем подключение и указываем флаг чтобы соединение создавалось только один раз
'''
connection = None
flag = False
if not flag:
    connection = bd.base_connect()
    flag = True


@app.get('/')
async def root():
    return {
        'message': '1'
        }

'''
+ Получить данные о себе(id, email, full_name) 
+ Получить список своих счетов и балансов 
+ Получить список своих платежей
подумать о кешировании?
'''
@app.get('/user/{user_id}')
async def get_user_info(user_id: int):
    '''
    находим пользователя, проводим валидацию, отдаем клиенту
    '''
    query = f"select * from users where id = {user_id}"
    res =  bd.base_get_data(connection, query)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        current_user = User(**res[0])
        return {
            'message': current_user
            }

@app.get('/user/{user_id}/accounts')
async def get_user_accounts(user_id: int):
    '''
    найти все счета пользователя, заполнить сущность accounts и отдать клиенту
    accounts - список объектов класса Account
    но сначала добавь в базу
    '''
    return {
        'message': 'вот типа все счета пользователя'
        }

@app.get('/user/{user_id}/payments')
async def get_user_payments(user_id: int):
    '''
    найти все платежи пользователя, заполнить сущность Payment и  отдать клиенту
    payments - список объектов класса Payment
    но сначала добавь в базу
    
    '''
    return {
        'message': 'вот типа все платежи пользователя'
        }



    
