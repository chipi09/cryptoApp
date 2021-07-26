import sqlite3

class DBmanager():

    def __init__(self, path):
        self.path = path
        
    def consulta(self, query):
        conexion = sqlite3.connect(self.path)
        cursor = conexion.cursor()
        cursor.execute(query)
        lista = cursor.fetchall()
        conexion.close()
        return lista
    
    def insert(self, query):
        conexion = sqlite3.connect(self.path)
        cursor = conexion.cursor()
        cursor.execute(query)
        conexion.commit()
        conexion.close()
        return cursor.lastrowid