from termcolor import colored
import sys
import DatabaseHandler






class User:

    #initializing DB
    # db = create_engine("sqlite:///TicketDB.db")
    # metadata = MetaData(db)
    # UserDB = Table("User", metadata, autoload=True)
    #
    # #DB functions
    # UserDB_insert = UserDB.insert()
    # UserDB_update = UserDB.update()
    # UserDB_delete = UserDB.delete()

    user_count = 0
    workgroups = ["Support Center", "Analyst"]
    user_dict = {"username": {}, "workgroup": {}, "assigned_tickets": {}}
    logged_in_username = ""
    logged_in_user = object()
    logged_in_workgroup = ""
    colored_user = ""
    colored_workgroup = ""
    logged_in = False


    def __init__(self,username, workgroup):
        User.user_count += 1
        self.ID = User.user_count
        self.user_count = User.user_count
        self.username = username
        self.workgroup = workgroup
        self.assigned_tickets = []

        #inserting into Database
        DatabaseHandler.insert(self)

    def assign_ticket(self):
        user_dict = User.user_dict
        ticket = ticket_select()
        previous_owner = ticket.assigned_user
        if ticket.resolved:
            print(colored("\n**Ticket# {} for {} is resolved and therefore cannot be assigned**".format(ticket.ID,ticket.name),"red"))
            input("[Enter to continue to menu]")
            menu()
        user = user_select()
        ticket.user_assigned_to = user.username
        ticket.assigned_user = user
        ticket.workgroup_assigned_to = user.workgroup

        # updating assigned tickets list when a ticket is passed from one user to another
        if ticket.ID in self.assigned_tickets:
            self.assigned_tickets.remove(ticket.ID)
            user.assigned_tickets.append(ticket.ID)
        elif ticket.ID in previous_owner.assigned_tickets:
            previous_owner.assigned_tickets.remove(ticket.ID)
            user.assigned_tickets.append(ticket.ID)
        else:
            user.assigned_tickets.append(ticket.ID)
        # Updating user database assigned tickets
        DatabaseHandler.update_user(user, assigned_tickets=True)
        DatabaseHandler.update_user(previous_owner, assigned_tickets= True)
        user_dict["assigned_tickets"][user.username] = ticket

        # Updating ticket database assigned user and workgroup
        DatabaseHandler.update_ticket(ticket,Assigned_User= True)
        DatabaseHandler.update_ticket(ticket, Workgroup= True)


        # Updating Databases after assignment of ticket
        # User.UserDB_update.where(User.UserDB.c.username == ticket.user_assigned_to).\
        #     values(assigned_tickets = str(user.assigned_tickets)).execute()
        #
        # User.UserDB_update.where(User.UserDB.c.username == previous_owner). \
        #          values(assigned_tickets = str(self.assigned_tickets)).execute()
        #
        # Ticket.TicketDB_update.where(Ticket.TicketDB.c.ID == ticket.ID). \
        #     values(Assigned_User = ticket.user_assigned_to)

        print(colored("\n**Ticket# {} assigned to User: {} in the {} workgroup**".format(ticket.ID, user.username,
                                                                               user.workgroup),"blue"))
        input("[Enter to continue to menu]")


# test analysts
# analyst1 = User("Analyst1", User.workgroups[1])
# analyst2 = User("Analyst2", User.workgroups[1])
# analyst3 = User("Tyler", User.workgroups[0])
#
# # populating dictionaries for searching
# User.user_dict["username"][analyst1.username] = analyst1
# User.user_dict["workgroup"][analyst1.workgroup] = analyst1
# User.user_dict["username"][analyst2.username] = analyst2
# User.user_dict["workgroup"][analyst2.workgroup] = analyst2
# User.user_dict["username"][analyst3.username] = analyst3
# User.user_dict["workgroup"][analyst3.workgroup] = analyst3


def create_user():
    space = "\n" * 10
    print(space + "Create User Account:\n-------------------")
    username = input("Create Username: ")
    print("Workgroups: {}".format(User.workgroups))
    workgroup = input("Select Workgroup: ")
    while workgroup not in User.workgroups:
        workgroup = input("Select Workgroup: ")

    user = User(username, workgroup)
    print(colored("\n**User: {} created successfully**".format(user.username),"blue"))
    input("[Enter to continue...]")
    User.user_dict["username"][user.username] = user
    User.user_dict["workgroup"][user.username] = user
    menu()
    return user


def user_select():
    user_dict = User.user_dict
    valid_users = list(user_dict["username"].keys())
    print("\nValid Users: {}".format(valid_users))
    try:
        username = input("Enter Username: ")
        while username not in valid_users:
            username = input("Enter Username: ")
        user = user_dict["username"][username]
        return user
    except KeyError:
        print("\n**User {} doesn't exist**".format(username))
        input("[Enter to continue to menu]")
        menu()


def user_login():
    space = "\n" * 10
    print(space + "Select a user to login as:")
    user = user_select()
    User.colored_user = colored(user.username,"blue")
    User.colored_workgroup = colored(user.workgroup,"red")
    User.logged_in_username = user.username
    User.logged_in_workgroup = user.workgroup
    User.logged_in_user = user
    User.logged_in = True
    print(colored("\n**Successfully logged in as: {}**".format(user.username),"blue"))
    input("[Enter to continue...]")


class Ticket:
    # initializing DB
    # db = create_engine("sqlite:///TicketDB.db")
    # metadata = MetaData(db)
    # TicketDB = Table("Ticket", metadata, autoload=True)
    #
    # # DB functions
    # TicketDB_insert = TicketDB.insert()
    # TicketDB_update = TicketDB.update()
    # TicketDB_delete = TicketDB.delete()

    created_tickets = 0
    tick_dict = {"ID": {}, "name": {}, "creator": {}}
    name_tickets = []
    creator_tickets = []
    ID = 1000

    def __init__(self, creator, name, callback, location, summary, detail):
        Ticket.ID += 1
        Ticket.created_tickets += 1
        self.creator = creator
        self.name = name
        self.callback = callback
        self.location = location
        self.summary = summary
        self.detail = detail
        self.ID = Ticket.ID
        self.created_tickets = Ticket.created_tickets
        self.workgroup_assigned_to = User.logged_in_workgroup
        self.user_assigned_to = User.logged_in_username
        self.assigned_user = User.logged_in_user
        self.resolution_note = ""
        self.status = "Open"
        self.resolved = False
        # Inserting into Database
        DatabaseHandler.insert(self)
        #Inserting Ticket into Database
        # Ticket.TicketDB_insert.execute({"ID": self.ID, "Creator": self.creator,
        #                                 "Name": self.name, "Callback": self.callback,
        #                                 "Location": self.location, "Summary": self.summary,
        #                                 "Detail": self.detail, "Assigned_User": self.user_assigned_to,
        #                                 "Workgroup": self.workgroup_assigned_to, "Status": self.status,
        #                                 "Resolved": self.resolved, "Resolution_Note": self.resolution_note})


    def __repr__(self):
        repres = "Ticket({},{},{},{},{},{},{})".format(self.ID, self.creator, self.name, self.callback, self.location,
                                                       self.summary, self.detail)
        return repres

    def __str__(self):
        if self.resolution_note == "":
            return "\nTicket# {}\nCreated By: {}\nName: {}\nCallback #: {}\nLocation: {}\nSummary: {}\nDetails: {" \
                   "}\nStatus: {}\nAssigned to: {}".format(
                self.ID, self.creator, self.name, self.callback, self.location, self.summary, self.detail, self.status,
                self.user_assigned_to + " - " + self.workgroup_assigned_to)
        else:
            return "\nTicket# {}\nCreated By: {}\nName: {}\nCallback #: {}\nLocation: {}\nSummary: {}\nDetails: {" \
                   "}\nStatus: {}\nResolution Note: {}\nAssigned to: {}".format(
                self.ID, self.creator, self.name, self.callback, self.location, self.summary, self.detail, self.status,
                self.resolution_note, self.user_assigned_to + " - " + self.workgroup_assigned_to)

    def resolve(self):

        if self.workgroup_assigned_to != User.logged_in_workgroup:
            print(colored("\n**User unauthorized to resolve for tickets assigned to the {} workgroup**".format(self.workgroup_assigned_to),"red"))
            input("[Enter to continue to menu]")
            menu()

        print("\nAre you sure you want to resolve the below ticket?\nID: {}\nName: {}".format(self.ID, self.name))

        resolve = input("-------------------\nResolve Y or N: ")
        if resolve.lower() == "y":
            self.resolved = True
            self.status = "Resolved"
            self.resolution_note = input("\nEnter Resolution Notes: ")

            # Updating Database status resolved boolean and resolution notes
            DatabaseHandler.update_ticket(self, Status=True)
            DatabaseHandler.update_ticket(self, Resolved= True)
            DatabaseHandler.update_ticket(self, Resolution_Note=True)

            print(colored("\n**Ticket# {} has been resolved**".format(self.ID),"blue"))
            input("[Enter to continue...]")
        else:
            print(colored("\n**Ticket# {} is still Open**".format(self.ID),"red"))
            input("[Enter to continue...]")

    def unresolve(self):
        print("\nAre you sure you want to un-resolve the below ticket?"
              "\nID: {}\nName: {}\nResolution Note: {}".format(self.ID, self.name,self.resolution_note))

        resolve = input("-------------------\nUn-resolve Y or N: ")
        if resolve.lower() == "y":
            self.resolved = False
            self.status = "Open"
            self.resolution_note = ""

            # Updating Database status resolved boolean and resolution notes
            DatabaseHandler.update_ticket(self, Status=True)
            DatabaseHandler.update_ticket(self, Resolved=True)
            DatabaseHandler.update_ticket(self, Resolution_Note=True)


            print(colored("\n**Ticket# {} is now back Open**".format(self.ID),"blue"))
            input("[Enter to continue...]")
        else:
            print(colored("\n**Ticket# {} is still Resolved**".format(self.ID),"red"))
            input("[Enter to continue...]")


def generate_ticket(user):
    space = "\n" * 10
    print(space + "Fill in ticket information:\n")
    ticket = Ticket(user.username, input("Name: "), input("Callback #: "), input("Location: ")
                    , input("Summary: "), input("Details: "))

    ticket.name_tickets.append(ticket)
    ticket.creator_tickets.append(ticket)
    user.assigned_tickets.append(ticket.ID)

    ticket.tick_dict["ID"][ticket.ID] = ticket
    ticket.tick_dict["name"][ticket.name] = ticket.name_tickets
    ticket.tick_dict["creator"][ticket.creator] = ticket.creator_tickets
    DatabaseHandler.update_user(user, assigned_tickets=True)


    print(colored("\n**Ticket# {} created successfully for customer name: {}**".format(ticket.ID, ticket.name),"blue"))
    input("[Enter to continue...]")
    return ticket


def ticket_select():
    try:
        search = "ID"
        valid_tickets = list(Ticket.tick_dict["ID"].keys())
        print("\nValid Tickets: {}".format(valid_tickets))
        ID = input("Enter ticket ID: ")
        try:
            while ID == "" or int(ID) not in valid_tickets:
                ID = input("Enter ticket ID: ")
            ticket = Ticket.tick_dict[search][int(ID)]
        except ValueError:
            print(colored("\n**Invalid Input Type, try again**"),"red")
            input("[Enter to continue...]")
            menu()
        print(ticket)
        input("[Enter to select this ticket]")
        return ticket
    except KeyError:
        print("\n**Ticket {} doesn't exist**".format(ID))
        input("[Enter to continue to menu]")
        menu()


def ticket_lookup():
    # column_count = 0
    error = True
    space = "\n" * 10
    print(
        space + "Search By:\n\n1.Ticket ID#\n2.Name on Ticket\n3.Name of Creator\n4.Open Tickets\n5.Resolved "
                "Tickets\n6.Assigned Tickets")
    search_method = input("\nSelect search method: ")
    try:
        if search_method == "1":
            search = "ID"
            valid_ids = list(Ticket.tick_dict[search].keys())
            print("\nValid IDs: {}".format(valid_ids))
            ID = input("Enter ID: ")


            while ID == "" or int(ID) not in valid_ids:
                ID = input("Enter ID: ")
            ticket = Ticket.tick_dict[search][int(ID)]
            print(ticket)
            input("[Enter to continue...]")
            menu()

        if search_method == "2":
            search = "name"
            valid_names = list(Ticket.tick_dict[search].keys())
            print("\nValid names: {}".format(valid_names))
            name = input("Enter Name: ")
            for ticket in Ticket.tick_dict[search][name]:
                if ticket.name == name:
                    print(ticket)
                    input("[Enter to continue...]")
                    error = False
            else:
                menu()
            if error:
                raise KeyError

        if search_method == "3":
            search = "creator"
            valid_creators = list(Ticket.tick_dict[search].keys())
            print("\nValid creators: {}".format(valid_creators))
            creator = input("Enter Creator name: ")
            for ticket in Ticket.tick_dict[search][creator]:
                if ticket.creator == creator:
                    print(ticket)
                    input("[Enter to continue...]")
                    error = False
            else:
                menu()
            if error:
                raise KeyError

        if search_method == "4":
            count = 0
            for ticket in Ticket.tick_dict["ID"].values():
                if not ticket.resolved:
                    print(ticket)
                    count += 1
                    input("[Enter to continue...]")
            if count < 1:
                print(colored("\n**No open tickets returned**","red"))
                input("[Enter to continue...]")

        if search_method == "5":
            count = 0
            for ticket in Ticket.tick_dict["ID"].values():
                if ticket.resolved:
                    print(ticket)
                    count += 1
                    input("[Enter to continue...]")
            if count < 1:
                print(colored("\n**No resolved tickets returned**","red"))
                input("[Enter to continue...]")

        if search_method == "6":
            count = 0
            print("\nValid Workgroups: {}".format(User.workgroups))
            workgroup = input("Enter Workgroup: ")
            while workgroup not in User.workgroups:
                workgroup = input("Enter Workgroup: ")
            for ticket in Ticket.tick_dict["ID"].values():
                if ticket.workgroup_assigned_to == workgroup:
                    print(ticket)
                    count += 1
                    input("[Enter to continue...]")
            if count < 1:
                print(colored("\n**No tickets returned for the {} workgroup**".format(workgroup),"red"))
                input("[Enter to continue...]")

    except KeyError:
        print("\nTicket {} doesn't exsist".format(search))
        input("[Enter to continue...]")


def menu():
    action = ""
    space = "\n" * 10

    while action.lower() != "q":
        print(space + "|********************************| ")
        print(" [ Logged in as: {} ]".format(User.colored_user))
        print(" [ Workgroup: {} ]".format(User.colored_workgroup))
        print("|********************************|\n" 
              "\n1.Login or [C to Create User])\n2.Create Ticket\n3.Ticket Lookup\n"
              "4.Resolve Ticket\n5.Un-resolve Ticket\n6.Assign Ticket\n -[Q to Quit]-")

        action = input("\nSelection: ")

        if action == "1" and User.user_count > 0:
            user_login()
            # test ticket
            ticket = Ticket(User.logged_in_username, "John Wilson", "341-6330", "ER", "Test", "Test")
            User.logged_in_user.assigned_tickets.append(ticket.ID)
            DatabaseHandler.update_user(User.logged_in_user, assigned_tickets=True)
            ticket.name_tickets.append(ticket)
            ticket.creator_tickets.append(ticket)
            ticket.tick_dict["ID"][ticket.ID] = ticket
            ticket.tick_dict["name"][ticket.name] = ticket.name_tickets
            ticket.tick_dict["creator"][ticket.creator] = ticket.creator_tickets
        elif action == "1" and User.user_count < 1:
            print(colored("**Please Create a User First**", "red"))
            input("[Enter to continue...]")
            create_user()
        if action.lower() == "c":
            create_user()
        if User.logged_in:
            if action == "2":
                generate_ticket(User.logged_in_user)
            if Ticket.created_tickets > 0:
                if action == "3":
                    ticket_lookup()
                if action == "4":
                    ticket = ticket_select()
                    ticket.resolve()
                if action == "5":
                    ticket = ticket_select()
                    ticket.unresolve()
                if action == "6" and User.user_count > 1:
                    User.logged_in_user.assign_ticket()
                elif action == "6":
                    print(colored("**No additional users to assign to**", "red"))
                    input("[Enter to continue...]")
            elif action.lower() != "q" and int(action) > 2:
                print(colored("**Please Create a Ticket First**","red"))
                input("[Enter to continue...]")

        elif action.lower() != "q":
            print(colored("**Please Login First**","red"))
            input("[Enter to continue...]")

    print(colored("\n**Exiting ticket system**","red"))
    input("[Enter to continue...]")
    sys.exit()


menu()
