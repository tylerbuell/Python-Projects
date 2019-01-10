import sqlite3

db = "TicketDB.db"
dbContents = []



def insert(object):
    dbConn = sqlite3.connect(db)

    if object.__class__.__name__ == "Ticket":
        ticket = object
        table = "TICKET"
        attributes = {"ID": ticket.ID, "Creator": ticket.creator,
                             "Name": ticket.name, "Callback": ticket.callback,
                             "Location": ticket.location, "Summary": ticket.summary,
                             "Detail": ticket.detail, "Assigned_User": ticket.user_assigned_to,
                             "Workgroup": ticket.workgroup_assigned_to, "Status": ticket.status,
                             "Resolved": ticket.resolved, "Resolution_Note": ticket.resolution_note}

        insert = "INSERT INTO {} VALUES(:ID,:Creator,:Name,:Callback,:Location,:Summary," \
                 ":Detail,:Assigned_User,:Workgroup,:Status,:Resolved,:Resolution_Note)".format(table)
    else:
        user = object
        table = "USER"
        attributes = {"ID":user.ID,"username": user.username,
                           "workgroup": user.workgroup, "assigned_tickets": str(user.assigned_tickets)}

        insert = "INSERT INTO {} VALUES(:ID,:username,:workgroup,:assigned_tickets)".format(table)

    dbConn.execute(insert,attributes)
    dbConn.commit()

    dbConn.close()
    fill_db()

def update_user(user,**column):
    dbConn = sqlite3.connect(db)
    if column.get("assigned_tickets"):
        update = "UPDATE USER SET assigned_tickets = '" + str(user.assigned_tickets) + "' WHERE ID = '" + str(user.ID)+"'"
    dbConn.execute(update)
    dbConn.commit()
    dbConn.close()

def update_ticket(ticket,**column):
    dbConn = sqlite3.connect(db)
    if column.get("Assigned_User"):
        update = "UPDATE TICKET SET Assigned_User = '"+ ticket.user_assigned_to + "' WHERE ID = '" + str(ticket.ID) + "'"
    if column.get("Workgroup"):
        update = "UPDATE TICKET SET Workgroup = '"+ ticket.workgroup_assigned_to + "' WHERE ID = '" + str(ticket.ID) + "'"
    if column.get("Status"):
        update = "UPDATE TICKET SET Status = '"+ ticket.status + "' WHERE ID = '" + str(ticket.ID) + "'"
    if column.get("Resolved"):
        update = "UPDATE TICKET SET Resolved = '"+ str(ticket.resolved) + "' WHERE ID = '" + str(ticket.ID) + "'"
    if column.get("Resolution_Note"):
        update = "UPDATE TICKET SET Resolution_Note = '"+ ticket.resolution_note + "' WHERE ID = '" + str(ticket.ID) + "'"
    dbConn.execute(update)
    dbConn.commit()
    dbConn.close()

def delete():
    dbConn = sqlite3.connect(db)
    fill_db()
    print(dbContents)

    delName = input("Enter the name to delete or enter ALL to clear all records >> ")
    if delName == "ALL":
        delete = "DELETE FROM NameDB"
        dbConn.execute(delete)
        dbContents.clear()
        print("All Records Successfully Deleted")
    else:
        if delName in dbContents:
            delete = "DELETE FROM NameDB WHERE FIRST_NAME = '" + delName + "'"
            dbConn.execute(delete)
            dbContents.remove(delName)
            print(delName + " has successfully been Deleted")
        else:
            print("Record does not exist in database")
    dbConn.commit()
    dbConn.close()
    fill_db()






def query():
    dbConn = sqlite3.connect(db)
    print("Connection to Database: " + db + " Successful\n")
    selectList = []
    moreColumns = ""

    while moreColumns != "N":
        print("Query SELECT:\n" + "1.First Name\n" + "2.Last Name\n" + "3.Age\n")
        selQueryCol = input("Query SELECT Which Column >> ")
        selQueryCol = int(selQueryCol) - 1
        selectList.append(dbColumns[selQueryCol])
        print(selectList)
        moreColumns = input("Select another column? (Y/N) >> ")

    print("Query WHERE:\n" + "1.First Name\n" + "2.Last Name\n" + "3.Age\n")
    queryWhere = input("Query WHERE which Column >> ")
    queryWhere = int(queryWhere) - 1
    whereValue = input("Query WHERE " + dbColumns[queryWhere] + " =  ")
    try:
        query = "SELECT " + str(",".join(selectList)) + " FROM NameDB" + " WHERE " + dbColumns[
            queryWhere] + " = '" + whereValue + "'"
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
    query = "SELECT * FROM Ticket"
    cursor = dbConn.execute(query)
    records = cursor.fetchall()
    for r in records:
        if r[0] not in dbContents:
            dbContents.append(r[0])
    dbConn.close()


def display():
    dbConn = sqlite3.connect(db)
    print("Connection to Database: " + db + " Successful\n")
    query = "SELECT * FROM Ticket"
    cursor = dbConn.execute(query)
    records = cursor.fetchall()
    print("Database: " + db + " All Records:\n")

    print("--------------------------------")
    for r in records:
        for c in r:
            print(c)
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


# if __name__ == "__main__":
#     fill_db()
#     menu()
