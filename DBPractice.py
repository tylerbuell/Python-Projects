
import sqlite3

db = "NameDB.db"
dbContents = []
dbColumns = ["FIRST_NAME","LAST_NAME","AGE"]

def insert():
    newRecord = ""
    dbConn = sqlite3.connect(db)
    print("Connection to Database: " + db + " Successful\n")

    while newRecord.upper() != "N":
        firstName = input("\nFirst Name: ")
        lastName = input("Last Name: ")
        age = input("Age: ")

        insert = "INSERT INTO NameDB(FIRST_NAME,LAST_NAME,AGE)" \
                 "VALUES ('" + firstName + "','" + lastName + "'," + age + ")"

        dbConn.execute(insert)
        dbConn.commit()
        print("Record inserted Successfully\n")
        newRecord = input("Add another Record? (Y/N) >> ")
    dbConn.close()
    fill_db()
    menu()

def delete():
    dbConn = sqlite3.connect(db)
    fill_db()
    print("Connection to Database: " + db + " Successful\n")
    print(dbContents)

    delName = input("Enter the name to delete or enter ALL to clear all records >> ")
    if delName == "ALL":
        delete = "DELETE FROM NameDB"
        dbConn.execute(delete)
        dbContents.clear()
        print("All Records Successfully Deleted")
    else:
        if delName in dbContents:
            delete = "DELETE FROM NameDB WHERE FIRST_NAME = '"+delName+"'"
            dbConn.execute(delete)
            dbContents.remove(delName)
            print(delName+" has successfully been Deleted")
        else:
            print("Record does not exist in database")
    dbConn.commit()
    dbConn.close()
    fill_db()
    menu()

def update():
    dbConn = sqlite3.connect(db)
    print("Connection to Database: " + db + " Successful\n")
    print(dbContents)

    oldName = input("Old Name: ")
    while oldName not in dbContents:
        oldName = input("Old Name: ")
    newName = input("Set "+oldName+" to: ")
    update = "UPDATE NameDB SET FIRST_NAME = '"+newName+"' WHERE FIRST_NAME = '"+oldName+"'"
    dbConn.execute(update)
    dbConn.commit()
    dbContents.remove(oldName)
    dbConn.close()

    print(oldName + " Has been updated to: " + newName)
    menu()

def query():
    dbConn = sqlite3.connect(db)
    print("Connection to Database: " + db + " Successful\n")
    selectList = []
    moreColumns = ""


    while moreColumns != "N":
        print("Query SELECT:\n"+"1.First Name\n"+"2.Last Name\n"+"3.Age\n")
        selQueryCol = input("Query SELECT Which Column >> ")
        selQueryCol = int(selQueryCol) - 1
        selectList.append(dbColumns[selQueryCol])
        print(selectList)
        moreColumns = input("Select another column? (Y/N) >> ")

    print("Query WHERE:\n"+"1.First Name\n"+"2.Last Name\n"+"3.Age\n")
    queryWhere = input("Query WHERE which Column >> ")
    queryWhere = int(queryWhere) - 1
    whereValue = input("Query WHERE "+dbColumns[queryWhere]+" =  ")
    try:
        query = "SELECT "+str(",".join(selectList))+" FROM NameDB"+" WHERE "+dbColumns[queryWhere]+" = '"+whereValue+"'"
        cursor = dbConn.execute(query)
        records = cursor.fetchall()
        print("\n[Query Result]")
        for r in records:
            print(r)
        menu()
    except:
         print("**Query ERROR**")
         menu()

def fill_db():
    dbConn = sqlite3.connect(db)
    query = "SELECT * FROM NameDB"
    cursor = dbConn.execute(query)
    records = cursor.fetchall()
    for r in records:
        if r[0] not in dbContents:
            dbContents.append(r[0])
    dbConn.close()

def display():
    dbConn = sqlite3.connect(db)
    print("Connection to Database: " + db + " Successful\n")
    query = "SELECT * FROM NameDB"
    cursor = dbConn.execute(query)
    records = cursor.fetchall()
    print("Database: " +db+" All Records:\n")
    print("| "+dbColumns[0]+" | "+dbColumns[1]+" | "+dbColumns[2]+" |")
    print("--------------------------------")
    for r in records:
        print("\t{}        {}      {}".format(r[0],r[1],r[2]))
    if len(dbContents) == 0:
        print("Database is empty")


    dbConn.close()
    menu()

def menu():
    print("""\n1.(I)nsert\n2.(U)pdate\n3.(DEL)ete\n4.(Q)uery\n5.(D)isplay""")

    menuSelection = input("Select a DB Function >> ")
    if menuSelection.upper() == "I":
        return insert()
    if menuSelection.upper() == "U":
        return update()
    if menuSelection.upper() == "DEL":
        return delete()
    if menuSelection.upper() == "Q":
        return query()
    if menuSelection.upper() == "D":
        return display()

fill_db()
menu()


