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
    id: int
    balance: int

#платеж
class Payment(BaseModel):
    id: int
    pay: int
    account_id: int


users_list: list[User] = []
'''
создаем подключение и указываем флаг чтобы соединение создавалось только один раз
если БД упадет и подключение разорвется, то что будет?
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
    query = f"select * from accounts where user_id = {user_id}"
    res =  bd.base_get_data(connection, query)
    if not res:
        raise HTTPException(status_code=404, detail="Accounts not found")
    else:
        current_user = unpack_data_accounts(res)
        return {
            'message': current_user
            }
'''
вспомогательная функция - распаковка результатов sql запросов для заполнения списка платежей юзера
'''
def unpack_data_payments(data):
    result = []
    for elem in data:
        tmp = Payment(**elem)
        result.append(tmp)
    return result

'''
вспомогательная функция - распаковка результатов sql запросов для заполнения списка счетов юзера
'''
def unpack_data_accounts(data):
    result = []
    for elem in data:
        tmp = Account(**elem)
        result.append(tmp)
    return result
        
    
    
@app.get('/user/{user_id}/payments')
async def get_user_payments(user_id: int):
    '''
    найти все платежи пользователя, заполнить сущность Payment и  отдать клиенту
    payments - список объектов класса Payment
    но сначала добавь в базу
    '''
    query = f"SELECT p.id AS id, p.pay AS pay, p.account_id FROM payment p JOIN accounts a ON p.account_id = a.id JOIN users u ON a.user_id = u.id WHERE u.id = {user_id}"
    res =  bd.base_get_data(connection, query)
    if not res:
        raise HTTPException(status_code=404, detail="Payments not found")
    else:
        current_user = unpack_data_payments(res)
        return {
            'message': current_user
            }



    
