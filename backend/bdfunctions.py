import mysql.connector
import config as conf
from fastapi import HTTPException

'''
заготовка для подключения к БД
принимает запрос, возвращает результат
в файле config.py прописаны настройки подключения к БД
'''
def base_connect():
    #res = []
    connection = None
    #cursor = None
    try:
        connection = mysql.connector.connect(
            host = conf.host,
            user = conf.user,
            password = conf.password,
            database = conf.database
            )

    except mysql.connector.Error as error:
        raise HTTPException(status_code = 503, detail = "Service Unavailable")

    return connection
'''
функция закрывает подключение(пока не используется, так как подключение разрывается после завершения приложения)
'''
def connection_close(connection):
    connection.close()
    
'''
функция выполняет запрос к БД и возвращает данные
'''
def base_get_data(connection, query):
    res = []
    if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            res = cursor.fetchall()
    if cursor:
        cursor.close()
    
    return res

'''
функция выполняет запрос к БД и возвращает данные
'''
def base_post_data(connection, query, values):
    cursor = connection.cursor()
    cursor.execute(query, values)
    connection.commit()
    cursor.close()

def delete_user(connection, query, values):
    base_post_data(connection, query, values)
    
    
