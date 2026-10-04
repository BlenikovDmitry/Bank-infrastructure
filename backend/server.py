from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

#пользователь
class User(BaseModel):
    id1: int
    email: str
    full_name: str
    role: str

#счет
class Account(BaseModel):
    id1: int
    balance: int

#платеж
class Payment(BaseModel):
    id1: int
    pay: int

'''
заготовка для подключения к БД
подключаемся один раз и используем в работе
'''
def base_connect():
    return

'''
синтетический пользователь пока не подключена БД
'''
user1 = User(
id1 = 123,
email = '123@gmail.com',
full_name = 'blenikov',
role = 'admin')


@app.get('/')
async def root():
    return {
        'message': 'Главная типа страница'
        }

'''
+ Получить данные о себе(id, email, full_name) 
+ Получить список своих счетов и балансов 
+ Получить список своих платежей 
'''
@app.get('/user/{user_id}')
async def get_user_info(user_id: int):
    '''
    найти пользователя в базе, заполнить сущность user, отдать клиенту
    '''
    if user_id == user1.id1:
        return {
            'message': 'Данные клиента',
            'user_id': user1.id1,
            'email': user1.email,
            'fullname': user1.full_name,
            'role': user1.role
            }
    raise HTTPException(status_code = 404, detail = "User not found")

@app.get('/user/{user_id}/accounts')
async def get_user_accounts(user_id: int):
    '''
    найти все счета пользователя, заполнить сущность accounts и отдать клиенту
    accounts - список объектов класса Account
    '''
    return {
        'message': 'вот типа все счета пользователя'
        }

@app.get('/user/{user_id}/payments')
async def get_user_payments(user_id: int):
    '''
    найти все платежи пользователя, заполнить сущность Payment и  отдать клиенту
    payments - список объектов класса Payment
    '''
    return {
        'message': 'вот типа все платежи пользователя'
        }



    
