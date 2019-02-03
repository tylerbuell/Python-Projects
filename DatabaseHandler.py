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
        print(user.ID)
        attributes = {"ID": user.ID, "username": user.username,
                      "workgroup": user.workgroup, "assigned_tickets": str(user.assigned_tickets)}

        insert = "INSERT INTO {} VALUES(:ID,:username,:workgroup,:assigned_tickets)".format(table)

    dbConn.execute(insert, attributes)
    dbConn.commit()
    dbConn.close()


def max_userid():
    dbConn = sqlite3.connect(db)
    select = "ID"
    table = "USER"
    query = """SELECT MAX(CAST({} as INTEGER)) FROM {}""".format(select, table)
    cursor = dbConn.execute(query)
    max_id = cursor.fetchone()
    return max_id[0]


def max_ticketid():
    dbConn = sqlite3.connect(db)
    select = "ID"
    table = "TICKET"
    query = """SELECT MAX(CAST({} as INTEGER)) FROM {}""".format(select, table)
    cursor = dbConn.execute(query)
    max_id = cursor.fetchone()
    return max_id[0]


def user_count():
    dbConn = sqlite3.connect(db)
    query = """SELECT count(*) FROM USER"""
    cursor = dbConn.execute(query)
    user_count = cursor.fetchone()[0]
    dbConn.commit()
    dbConn.close()
    return int(user_count)


def ticket_count():
    dbConn = sqlite3.connect(db)
    query = """SELECT count(*) FROM TICKET"""
    cursor = dbConn.execute(query)
    ticket_count = cursor.fetchone()[0]
    dbConn.commit()
    dbConn.close()
    return int(ticket_count)


def update_user(user, **column):
    dbConn = sqlite3.connect(db)
    if column.get("column") == "username":
        update = "UPDATE USER SET username = '" + str(user.username) + "' WHERE ID = '" + str(
            user.ID) + "'"
    if column.get("column") == "workgroup":
        update = "UPDATE USER SET workgroup = '" + str(user.workgroup) + "' WHERE ID = '" + str(
            user.ID) + "'"
    if column.get("assigned_tickets"):
        update = "UPDATE USER SET assigned_tickets = '" + str(user.assigned_tickets) + "' WHERE ID = '" + str(
            user.ID) + "'"
    dbConn.execute(update)
    dbConn.commit()
    dbConn.close()


def update_ticket(ticket, **column):
    dbConn = sqlite3.connect(db)
    if column.get("column") == "Name":
        update = "UPDATE TICKET SET Name = '" + ticket.name + "' WHERE ID = '" + str(
            ticket.ID) + "'"
    if column.get("column") == "Callback":
        update = "UPDATE TICKET SET Callback = '" + ticket.callback + "' WHERE ID = '" + str(
            ticket.ID) + "'"
    if column.get("column") == "Location":
        update = "UPDATE TICKET SET Location = '" + ticket.location + "' WHERE ID = '" + str(
            ticket.ID) + "'"
    if column.get("column") == "Summary":
        update = "UPDATE TICKET SET Summary = '" + ticket.summary + "' WHERE ID = '" + str(
            ticket.ID) + "'"
    if column.get("column") == "Detail":
        update = "UPDATE TICKET SET Detail = '" + ticket.detail + "' WHERE ID = '" + str(
            ticket.ID) + "'"
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


def delete(object):
    object_name = object.__class__.__name__
    dbConn = sqlite3.connect(db)
    delete_check = input("Are you sure you want to delete selected {}? (Y/N)".format(object_name)).lower()
    if delete_check == "y":
        if object_name == "Ticket":
            ticket = object
            table = "TICKET"
            delete = """DELETE FROM {} WHERE ID = {}""".format(table, ticket.ID)
            associated_user = ticket.assigned_user
            if len(associated_user.assigned_tickets) > 0:
                if ticket.ID in associated_user.assigned_tickets:
                    associated_user.assigned_tickets.remove(ticket.ID)
                update_user(associated_user, assigned_tickets=True)
                del ticket.tick_dict["ID"][ticket.ID]
                del ticket.tick_dict["name"][ticket.name]
                del ticket.tick_dict["creator"][ticket.creator]
                del ticket

        else:
            user = object
            table = "USER"
            delete = """DELETE FROM {} WHERE ID = {}""".format(table, user.ID)
            del user.user_dict["username"][user.username]
            del user.user_dict["workgroup"][user.username]
            del user

        dbConn.execute(delete)
        dbConn.commit()
        dbConn.close()
        return True


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
