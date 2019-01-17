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
        attributes = {"ID": user.ID, "username": user.username,
                      "workgroup": user.workgroup, "assigned_tickets": str(user.assigned_tickets)}

        insert = "INSERT INTO {} VALUES(:ID,:username,:workgroup,:assigned_tickets)".format(table)

    dbConn.execute(insert, attributes)
    dbConn.commit()

    dbConn.close()


def update_user(user, **column):
    dbConn = sqlite3.connect(db)
    if column.get("assigned_tickets"):
        update = "UPDATE USER SET assigned_tickets = '" + str(user.assigned_tickets) + "' WHERE ID = '" + str(
            user.ID) + "'"
    dbConn.execute(update)
    dbConn.commit()
    dbConn.close()


def update_ticket(ticket, **column):
    dbConn = sqlite3.connect(db)
    if column.get("Assigned_User"):
        update = "UPDATE TICKET SET Assigned_User = '" + ticket.user_assigned_to + "' WHERE ID = '" + str(
            ticket.ID) + "'"
    if column.get("Workgroup"):
        update = "UPDATE TICKET SET Workgroup = '" + ticket.workgroup_assigned_to + "' WHERE ID = '" + str(
            ticket.ID) + "'"
    if column.get("Status"):
        update = "UPDATE TICKET SET Status = '" + ticket.status + "' WHERE ID = '" + str(ticket.ID) + "'"
    if column.get("Resolved"):
        update = "UPDATE TICKET SET Resolved = '" + str(ticket.resolved) + "' WHERE ID = '" + str(ticket.ID) + "'"
    if column.get("Resolution_Note"):
        update = "UPDATE TICKET SET Resolution_Note = '" + ticket.resolution_note + "' WHERE ID = '" + str(
            ticket.ID) + "'"
    dbConn.execute(update)
    dbConn.commit()
    dbConn.close()


def delete():
    dbConn = sqlite3.connect(db)
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


def user_count():
    dbConn = sqlite3.connect(db)
    query = """SELECT count(*) FROM USER"""
    cursor = dbConn.execute(query)
    user_count = cursor.fetchone()
    dbConn.commit()
    dbConn.close()
    return int(user_count[0])


def ticket_count():
    dbConn = sqlite3.connect(db)
    query = """SELECT count(*) FROM TICKET"""
    cursor = dbConn.execute(query)
    ticket_count = cursor.fetchone()
    dbConn.commit()
    dbConn.close()
    return int(ticket_count[0])


def query(table, select, where):
    records = []
    dbConn = sqlite3.connect(db)
    moreColumns = ""

    if table == "TICKET":
        if select == "*":
            query = """SELECT {} FROM {} WHERE ID = {}""".format(select, table, int(where))
        else:
            query = """SELECT {} FROM {}""".format(select, table)
        try:
            cursor = dbConn.execute(query)
            record_list = cursor.fetchall()
            for record in record_list:
                records.append(record)
            return records
        except:
            print("**Query ERROR**")

    if table == "USER":
        query = """SELECT {} FROM {}""".format(select, table)
        try:
            cursor = dbConn.execute(query)
            record_list = cursor.fetchall()
            for record in record_list:
                records.append(record)
            return records
        except:
            print("**Query ERROR**")

# if __name__ == "__main__":
