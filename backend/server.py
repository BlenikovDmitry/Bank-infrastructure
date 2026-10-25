from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import bdfunctions as bd
from typing import Optional


app = FastAPI()

#пользователь
class User(BaseModel):
    id: int
    email: str
    fullname: str
    role_: str
    is_active: int

#пользователь для записи в БД
class User_Create(BaseModel):
    email: str
    fullname: str
    role_: str
    is_active: int
    
#пользователь для обновления записи в БД
class User_Patch(BaseModel):
    email: Optional[str] = None
    fullname: Optional[str] = None
    role_: Optional[str] = None
    is_active: Optional[int] = None
    
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
Пользовательская часть
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
'''
Админская часть
+ создать пользователя
+ удалить пользователя
+ обновить пользователя
- получить список пользователей с их балансами
'''
@app.post('/user/create')
async def create_user(user: User_Create):
    '''
    метод создает пользователя в БД
    '''
    user = user.model_dump()
    query = "INSERT INTO users (email, fullname, role_, is_active) VALUES (%s, %s, %s, %s)"
    values = (user['email'], user['fullname'], user['role_'], user['is_active'])

    bd.base_post_data(connection, query, values)
    return { 'result': 'success'}

@app.delete('/user/{user_id}/delete')
async def delete_user(user_id: int):
    '''
    метод находит пользователя по id и удаляет его из БД
    '''
    query = 'delete from users where id = %s'
    bd.delete_user(connection, query, (user_id,))
    return { 'result': 'success'}
    
@app.patch('/user/{user_id}/update')
async def patch_user(user_id: int, patched_user: User_Patch):
    '''
    метод находит пользователя по id и обновляет поля
    '''
    changes = patched_user.model_dump(exclude_unset = True)
    set_clause = ", ".join([f"{key} = %s" for key in changes.keys()])
    query = f"UPDATE users SET {set_clause} WHERE id = %s"
    values = list(changes.values()) + [user_id]
    bd.base_post_data(connection, query, values)
    return { 'result': 'success'}
    
