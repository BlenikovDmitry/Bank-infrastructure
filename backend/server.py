from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import bdfunctions as bd
from typing import Optional
import config as conf


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
@app.get('/user')
async def get_user_info(
    user_id: Optional[int] = Query(None, description = "по ид пользователя"),
    fullname: Optional[str] = Query(None, description = "по имени пользователя")
    ):

    if user_id is None and fullname is None:
        raise HTTPException(status_code = 400, detail = 'нет ни id ни имени пользователя')

    if user_id is not None:
        query = "select * from users where id = %s and is_active = 1"
        values = (user_id,)
    else:
        query = "select * from users where fullname = %s and is_active = 1"
        values = (fullname,)
        
    '''
    находим пользователя, проводим валидацию, отдаем клиенту
    '''
    res =  bd.base_get_data_save(connection, query, values)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        current_user = User(**res[0])
        return {
            'message': current_user
            }

@app.get('/user/accounts')
async def get_user_accounts(
    user_id: Optional[int] = Query(None, description = "по ид пользователя")
    ):

    if user_id is None:
        raise HTTPException(status_code = 400, detail = 'нет ни id пользователя')
    '''
    найти все счета пользователя, заполнить сущность accounts и отдать клиенту
    accounts - список объектов класса Account
    '''
    query = "select * from accounts where user_id = %s"
    values = (user_id,)
    res =  bd.base_get_data_save(connection, query, values)
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
        
    
    
@app.get('/user/payments')
async def get_user_payments(
    user_id: Optional[int] = Query(None, description = "по ид пользователя")
    ):

    if user_id is None:
        raise HTTPException(status_code = 400, detail = 'нет ни id пользователя')
    '''
    найти все платежи пользователя, заполнить сущность Payment и  отдать клиенту
    payments - список объектов класса Payment
    '''
    query = "SELECT p.id AS id, p.pay AS pay, p.account_id FROM payment p JOIN accounts a ON p.account_id = a.id JOIN users u ON a.user_id = u.id WHERE u.id = %s"
    values = (user_id,)
    res =  bd.base_get_data_save(connection, query, values)
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
+ получить список пользователей с их балансами
'''
@app.post('/admin/user/create')
async def create_user(user: User_Create):
    '''
    метод создает пользователя в БД
    '''
    user = user.model_dump()
    query = "INSERT INTO users (email, fullname, role_, is_active) VALUES (%s, %s, %s, %s)"
    values = (user['email'], user['fullname'], user['role_'], user['is_active'])
    if user['role_'] in conf.user_roles:
        bd.base_post_data(connection, query, values)
        return { 'result': 'success'}
    else:
        raise HTTPException(status_code=400, detail="Invalid user role")
        

@app.delete('/admin/user/delete')
async def delete_user(
    user_id: Optional[int] = Query(None, description = "по ид пользователя"),
    fullname: Optional[str] = Query(None, description = "по имени пользователя")
    ):
    '''
    метод переводит пользователя из состояния is_active = 1 в состояние is_active = 0
    такой метод нужен для того, чтобы вести архивные данные
    '''

    if user_id is None and fullname is None:
        raise HTTPException(status_code = 400, detail = 'нет ни id ни имени пользователя')

    # Меняем логику с DELETE на UPDATE
    if user_id is not None:
        query = "UPDATE users SET is_active = %s WHERE id = %s"
        values = (0, user_id)
    else:
        query = "UPDATE users SET is_active = %s WHERE fullname = %s"
        values = (0, fullname)
    '''
    метод находит пользователя по id и удаляет его из БД
    '''
    bd.delete_user(connection, query, values)
    return { 'result': 'success'}
    
@app.patch('/admin/user/update')
async def patch_user(
    patched_user: User_Patch,
    user_id: Optional[int] = Query(None, description = "по ид пользователя")
    ):
    '''
    метод изменяет уже созданного пользователя 
    '''
    if user_id is None:
        raise HTTPException(status_code = 400, detail = 'нет id пользователя')
    '''
    метод находит пользователя по id и обновляет поля
    '''
    changes = patched_user.model_dump(exclude_unset = True)
    set_clause = ", ".join([f"{key} = %s" for key in changes.keys()])
    query = f"UPDATE users SET {set_clause} WHERE id = %s"
    values = list(changes.values()) + [user_id]
    bd.base_post_data(connection, query, values)
    return { 'result': 'success'}

@app.get('/admin/user/get/users')
async def get_all_users():
    '''
    метод выводит список всех пользователей и их балансов
    '''
    query = "select u.id, u.fullname, u.email, a.balance from users u left join accounts a on a.user_id = u.id where u.is_active != 0"
    res =  bd.base_get_data_save(connection, query)
    if not res:
        raise HTTPException(status_code=404, detail="Payments not found")
    else:
        return {
            'message': res

            }
