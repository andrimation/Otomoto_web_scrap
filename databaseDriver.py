import requests
import mysql.connector

def databaseDriver():
    whatToDo = input("Type create database = 1 or connect to database = 2:   ")
    if whatToDo == "1":
        try:
            db_connection = mysql.connector.connect(host="localhost",
                                    user="andrik",
                                    password="osaosa")
            connected = True
        except:
            print("MySql Database connection failed")
            connected = False

        #sprawdzić czy istnieje baza danych otomoto, jeśli nie to utworzyć.
        if connected:
            db_cursor = db_connection.cursor()
            db_cursor.execute("SHOW DATABASES")

            databaseExist = False
            for db in db_cursor:
                if db[0] == "otomoto_database":
                    databaseExist = True
                    break

            if not databaseExist:
                db_cursor.execute("CREATE DATABASE otomoto_database")
                print("Utworzono otomoto_database")
    elif whatToDo =="2":
        try:
            db_connection = mysql.connector.connect(host="localhost",
                                    user="andrik",
                                    password="osaosa",
                                    database="otomoto_database")
            connected = True
            print("Connected to otomoto_database")
            db_cursor = db_connection.cursor()
        except:
            print("MySql Database connection failed")
            connected = False

    while True:
        whatToDo = input("type 1 ='create cars table' or 2 = run gathering program or 3 = print database tables names:   ")
        if connected:
            if whatToDo == '1':
                while True:
                    newTableName = input("Podaj nazwę nowej tabeli:")
                    db_cursor.execute("Show tables;")
                    tableFlag = False
                    for table in db_cursor:
                        print(table[0])
                        if table[0] == newTableName:
                            tableFlag = True
                    if tableFlag == False:
                        create_movies_table = f"CREATE TABLE {newTableName}(id INT AUTO_INCREMENT PRIMARY KEY, car_url VARCHAR(250))"
                        db_cursor.execute(create_movies_table)
                        db_connection.commit()
                        break
                    else:
                        print(f"Tablica {newTableName} jest już w bazie danych")


            elif whatToDo == "2":
                return True,db_cursor,db_connection

            elif whatToDo == "3":
                db_cursor.execute("Show tables;")
                tableFlag = False
                for table in db_cursor:
                    print(table[0])


def checkIfCarExistInDatabase(db_connection,carUrl,currentTable):
    databaseCursor = db_connection.cursor()

    query = f"SELECT * FROM {currentTable} WHERE car_url = %s"
    params = (carUrl,)
    databaseCursor.execute(query,params)
    result = databaseCursor.fetchall()
    print(result)
    if result:
        return True
    else:
        return False

def updateDatabaseColumns(db_connection,carDataDict,currentTable):
    databaseCursor = db_connection.cursor()
    columnsQuery = f"SHOW COLUMNS FROM {currentTable}"
    databaseCursor.execute(columnsQuery)
    columns = [column[0] for column in databaseCursor.fetchall()]
    print("Columns: ",columns)
    print("liczba kolumn: ",len(columns))
    for key in carDataDict:
        if key not in columns:
            databaseCursor = db_connection.cursor()
            print(key,"not in ",columns)
            columnType = getColumnType(key)
            addColumns = f"ALTER TABLE {currentTable} ADD {key} {columnType}"
            databaseCursor.execute(addColumns)
            databaseCursor.commit()
        else:
            pass


def getColumnType(key):
    if key in ["offerAddDate","offerLastSeenDate","firstRegisterDate"]:
        return "DATETIME"
    else:
        return "TEXT"

def addNewCarToDatabase(db_connection,carDataDict,currentTable):
    # sprawdzenie jakie są kolumny w tabeli
    pass

def updateExistingCarLastSeenDate():
    pass

def updateOfferAddDateIfMissing():
    pass


