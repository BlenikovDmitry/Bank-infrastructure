from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import config as conf


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
принимает запрос, возвращает результат
в файле config.py прописаны настройки подключения к БД
'''
def base_connect_and_get_data(query):
    res = []
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host = conf.host,
            user = conf.user,
            password = conf.password,
            database = conf.database
            )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            res = cursor.fetchall()
    except mysql.connector.Error as error:
        raise HTTPException(status_code = 503, detail = "Service Unavailable")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    
    return res


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
        'message': base_connect_and_get_data("select * from users")
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



    
