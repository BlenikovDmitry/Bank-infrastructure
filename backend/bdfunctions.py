import mysql.connector
import config as conf
from fastapi import HTTPException

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
