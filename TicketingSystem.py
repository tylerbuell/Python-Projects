from termcolor import colored
import sys
import DatabaseHandler
import textwrap


class User:
    # initializing temp user until real one is created
    temp_user = lambda: None
    temp_user.assigned_tickets = []
    ID = 1
    users_pulled = False
    user_count = DatabaseHandler.user_count()
    workgroups = sorted(["Support Center", "Epic Analyst", "Deskside", "Client Engineering"])
    user_dict = {"username": {}, "workgroup": {}, "assigned_tickets": {}}
    logged_in_username = ""
    logged_in_user = temp_user
    logged_in_workgroup = ""
    colored_user = ""
    colored_workgroup = ""
    logged_in = False

    def __init__(self, username, workgroup):
        self.user_count = User.user_count
        self.ID = User.ID + User.user_count
        self.username = username
        self.workgroup = workgroup
        self.assigned_tickets = []

    def assign_ticket(self):
        user_dict = User.user_dict
        ticket = ticket_select()
        previous_owner = ticket.assigned_user

        if ticket.resolved:
            print(colored(
                "\n**Ticket# {} for {} is resolved and therefore cannot be assigned**".format(ticket.ID, ticket.name),
                "red"))
            input("[Enter to continue to menu]")
            menu()

        if User.logged_in_user.workgroup == ticket.assigned_user.workgroup:
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

            DatabaseHandler.update_user(previous_owner, assigned_tickets=True)
            # updating dictionaries
            user_dict["assigned_tickets"][user.username] = ticket
            ticket.tick_dict["ID"][ticket.ID] = ticket
            ticket.tick_dict["name"][ticket.name] = ticket.name_tickets

            # Updating ticket database assigned user and workgroup
            DatabaseHandler.update_ticket(ticket, Assigned_User=True)
            DatabaseHandler.update_ticket(ticket, Workgroup=True)

            print(colored("\n**Ticket# {} assigned to User: {} in the {} workgroup**".format(ticket.ID, user.username,
                                                                                             user.workgroup), "blue"))
            input("[Enter to continue to menu]")
        else:
            print(colored(
                "\n**Not Authorized to Resolve Ticket# {} for {} is assigned to a user in the {} workgroup **"
                    .format(ticket.ID, ticket.name, ticket.workgroup_assigned_to), "red"))
            input("[Enter to continue to menu]")


def create_user():
    space = "\n" * 10
    print(space + "Create User Account:\n-------------------")
    username = input("Create Username: ")
    print("Workgroups: {}".format(User.workgroups))
    workgroup = input("Select Workgroup: ")
    while workgroup not in User.workgroups:
        workgroup = input("Select Workgroup: ")

    user = User(username, workgroup)
    print(colored("\n**User: {} created successfully**".format(user.username), "blue"))
    input("[Enter to continue...]")
    User.user_dict["username"][user.username] = user
    User.user_dict["workgroup"][user.username] = user
    # inserting into Database
    DatabaseHandler.insert(user)
    # Counting Users
    User.user_count = DatabaseHandler.user_count()
    menu()
    return user


def user_select():
    user_dict = User.user_dict
    valid_users = list(user_dict["username"].keys())
    print("\nValid Users: {}".format(list(valid_users)))
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
    User.colored_user = colored(user.username, "blue")
    User.colored_workgroup = colored(user.workgroup, "red")
    User.logged_in_username = user.username
    User.logged_in_workgroup = user.workgroup
    User.logged_in_user = user
    User.logged_in = True
    print(colored("\n**Successfully logged in as: {}**".format(user.username), "blue"))
    input("[Enter to continue...]")


class Ticket:
    ID = 1001
    tickets_pulled = False
    created_tickets = DatabaseHandler.ticket_count()
    tick_dict = {"ID": {}, "name": {}, "creator": {}}
    name_tickets = []
    creator_tickets = []

    def __init__(self, creator, name, callback, location, summary, detail):
        self.creator = creator
        self.name = name
        self.callback = callback
        self.location = location
        self.summary = summary
        self.detail = detail
        self.ID = Ticket.ID + Ticket.created_tickets
        self.created_tickets = Ticket.created_tickets
        self.workgroup_assigned_to = User.logged_in_workgroup
        self.user_assigned_to = User.logged_in_username
        self.assigned_user = User.logged_in_user
        self.resolution_note = ""
        self.status = "Open"
        self.resolved = False

    def __repr__(self):
        repres = "Ticket({},{},{},{},{},{},{})".format(self.ID, self.creator, self.name, self.callback, self.location,
                                                       self.summary, self.detail)
        return repres

    def __str__(self):
        divider = "-" * 70 + "\n"
        if self.resolution_note == "":
            return "\n{}Ticket# {}\nCreated By: {}\nName: {}\nCallback #: {}\nLocation: {}\nTicket Status: {}" \
                   "\nAssigned to: {}\n{}Summary: {}\n{}Details:\n\n{}\n{}".format(divider,
                                                                                   self.ID, self.creator, self.name,
                                                                                   self.callback, self.location,
                                                                                   self.status
                                                                                   ,
                                                                                   self.user_assigned_to + " - " + self.workgroup_assigned_to,
                                                                                   divider, self.summary, divider,
                                                                                   self.detail,
                                                                                   divider)
        else:
            return "\n{}Ticket# {}\nCreated By: {}\nName: {}\nCallback #: {}\nLocation: {}\nTicket Status: {}" \
                   "\nResolution Note: {}\nAssigned to: {}\n{}Summary: {}\n{}Details:\n\n{}\n{}".format(divider,
                                                                                                        self.ID,
                                                                                                        self.creator,
                                                                                                        self.name,
                                                                                                        self.callback,
                                                                                                        self.location,
                                                                                                        self.status,
                                                                                                        self.resolution_note,
                                                                                                        self.user_assigned_to + " - " + self.workgroup_assigned_to,
                                                                                                        divider,
                                                                                                        self.summary,
                                                                                                        divider,
                                                                                                        self.detail,
                                                                                                        divider)

    def multiline_input(string):
        line_count = 1
        details = """"""
        detail = """ """
        while detail != """""":
            detail = input("{} line {}: ".format(string, line_count))
            details += " " + detail + "\n"
            line_count += 1
            details = textwrap.fill(details)
        return details

    def resolve(self):
        assigned_user = self.assigned_user
        if self.workgroup_assigned_to != User.logged_in_workgroup:
            print(colored("\n**User unauthorized to resolve for tickets assigned to the {} workgroup**".format(
                self.workgroup_assigned_to), "red"))
            input("[Enter to continue to menu]")
            menu()
        elif self.resolved:
            print(colored("\n**Ticket is already resolved**", "red"))
            input("[Enter to continue to menu]")
            menu()
        print("\nAre you sure you want to resolve the below ticket?\nID: {}\nName: {}".format(self.ID, self.name))

        resolve = input("-------------------\nResolve Y or N: ")
        if resolve.lower() == "y":
            self.resolved = True
            self.status = "Resolved"
            self.resolution_note = Ticket.multiline_input("Enter Resolution Note")
            assigned_user.assigned_tickets.remove(self.ID)

            # Updating Database status resolved boolean and resolution notes
            DatabaseHandler.update_ticket(self, Status=True)
            DatabaseHandler.update_ticket(self, Resolved=True)
            DatabaseHandler.update_ticket(self, Resolution_Note=True)
            DatabaseHandler.update_user(assigned_user, assigned_tickets=True)

            print(colored("\n**Ticket# {} has been resolved**".format(self.ID), "blue"))
            input("[Enter to continue...]")
        else:
            print(colored("\n**Ticket# {} is still Open**".format(self.ID), "red"))
            input("[Enter to continue...]")

    def unresolve(self):
        assigned_user = self.assigned_user
        if not self.resolved:
            print(colored("\n**Ticket is already Open**", "red"))
            input("[Enter to continue to menu]")
            menu()
        print("\nAre you sure you want to un-resolve the below ticket?"
              "\nID: {}\nName: {}\nResolution Note: {}".format(self.ID, self.name, self.resolution_note))

        resolve = input("-------------------\nUn-resolve Y or N: ")
        if resolve.lower() == "y":
            self.resolved = False
            self.status = "Open"
            self.resolution_note = ""
            assigned_user.assigned_tickets.append(self.ID)
            # Updating Database status resolved boolean and resolution notes
            DatabaseHandler.update_ticket(self, Status=True)
            DatabaseHandler.update_ticket(self, Resolved=True)
            DatabaseHandler.update_ticket(self, Resolution_Note=True)
            DatabaseHandler.update_user(assigned_user, assigned_tickets=True)

            print(colored("\n**Ticket# {} is now back Open**".format(self.ID), "blue"))
            input("[Enter to continue...]")
        else:
            print(colored("\n**Ticket# {} is still Resolved**".format(self.ID), "red"))
            input("[Enter to continue...]")


def generate_ticket(user):
    space = "\n" * 10
    print(space + "Fill in ticket information:\n")
    ticket = Ticket(user.username, input("Name: "), input("Callback #: "), input("Location: ")
                    , input("Ticket Summary: "), Ticket.multiline_input("Ticket Detail"))

    ticket.name_tickets.append(ticket)
    ticket.creator_tickets.append(ticket)
    user.assigned_tickets.append(ticket.ID)

    ticket.tick_dict["ID"][ticket.ID] = ticket
    ticket.tick_dict["name"][ticket.name] = ticket.name_tickets
    ticket.tick_dict["creator"][ticket.creator] = ticket.creator_tickets
    # Inserting into Database
    DatabaseHandler.insert(ticket)
    # updating assigned tickets for user
    DatabaseHandler.update_user(user, assigned_tickets=True)
    # Counting tickets
    Ticket.created_tickets = DatabaseHandler.ticket_count()

    print(colored("\n**Ticket# {} created successfully for customer name: {}**".format(ticket.ID, ticket.name), "blue"))
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
            print(colored("\n**Invalid Input Type, try again**"), "red")
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
    error = True
    space = "\n" * 10
    print(
        space + "Search By:\n\n1.Ticket ID#\n2.My Tickets\n3.Name on Ticket\n4.Name of Creator\n5.Open Tickets\n6.Resolved "
                "Tickets\n7.Assigned Tickets")
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
            search = "ID"
            IDs = User.logged_in_user.assigned_tickets
            user = User.logged_in_user
            if len(IDs) != 0:
                for ID in IDs:
                    # print(Ticket.tick_dict[search][ID])
                    for ticket in Ticket.tick_dict[search].values():
                        if ticket.ID == ID and not ticket.resolved:
                            print(ticket)
                            input("[Enter to continue...]")
            else:
                print(colored("\n**No tickets returned for {}**".format(user.username), "red"))
                input("[Enter to continue...]")
                menu()
        if search_method == "3":
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

        if search_method == "4":
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

        if search_method == "5":
            count = 0
            for ticket in Ticket.tick_dict["ID"].values():
                if not ticket.resolved:
                    print(ticket)
                    count += 1
                    input("[Enter to continue...]")
            if count < 1:
                print(colored("\n**No open tickets returned**", "red"))
                input("[Enter to continue...]")

        if search_method == "6":
            count = 0

            for ticket in Ticket.tick_dict["ID"].values():
                if ticket.resolved:
                    print(ticket)
                    count += 1
                    input("[Enter to continue...]")
            if count < 1:
                print(colored("\n**No resolved tickets returned**", "red"))
                input("[Enter to continue...]")

        if search_method == "7":
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
                print(colored("\n**No tickets returned for the {} workgroup**".format(workgroup), "red"))
                input("[Enter to continue...]")

    except KeyError:
        print("\nTicket {} doesn't exsist".format(search))
        input("[Enter to continue...]")


# for converting string boolean to true boolean for resolution
def strtobool(string):
    if str(string).capitalize() == "True":
        return True
    else:
        return False


def pull_users_from_db():
    # pulling user table attributes in from USER table
    user_data = DatabaseHandler.query("USER", "ID,username,workgroup, assigned_tickets", "")
    # for every ticket in DB creating a ticket object and assigning object attributes
    for i in range(len(user_data)):
        user = User(user_data[i][1], user_data[i][2])
        user.ID = user_data[i][0]
        user.assigned_tickets = user_data[i][3]
        # Filling Dictionaries
        User.user_dict["username"][user.username] = user
        User.user_dict["workgroup"][user.username] = user

        # creating empty list if string represents an empty list object
        if user.assigned_tickets == "[]":
            user.assigned_tickets = list()
        else:
            user.assigned_tickets = list()
            # striping out the list brackets and appending ID to empty list of assigned tickets if empty
            # Splitting ticket Ids into list and appending individually
            ticket_ids = user_data[i][3].strip("[]").split(",")
            for ticket_id in ticket_ids:
                user.assigned_tickets.append(int(ticket_id))
    # boolean flag so pulling from DB only occurs once
    User.users_pulled = True


def pull_tickets_from_db():
    # pulling ticket table attributes in from TICKET table
    ticket_data = DatabaseHandler.query("TICKET", "ID,Creator, Name, Callback,"
                    "Location, Summary, Detail,Assigned_User,Workgroup,Status,Resolved,Resolution_Note","")
    # for every ticket in DB creating a ticket object and assigning object attributes
    for i in range(len(ticket_data)):
        ticket = Ticket(ticket_data[i][1], ticket_data[i][2], ticket_data[i][3], ticket_data[i][4], ticket_data[i][5],
                        ticket_data[i][6])
        ticket.ID = ticket_data[i][0]
        ticket.name_tickets.append(ticket)
        ticket.creator_tickets.append(ticket)
        ticket.user_assigned_to = ticket_data[i][7]
        ticket.assigned_user = User.user_dict["username"][ticket_data[i][7]]
        ticket.workgroup_assigned_to = ticket_data[i][8]
        ticket.status = ticket_data[i][9]
        ticket.resolved = strtobool(ticket_data[i][10])
        ticket.resolution_note = ticket_data[i][11]
        # filling dictionaries
        ticket.tick_dict["ID"][ticket.ID] = ticket
        ticket.tick_dict["name"][ticket.name] = ticket.name_tickets
        ticket.tick_dict["creator"][ticket.creator] = ticket.creator_tickets
    # boolean flag so pulling from DB only occurs once
    Ticket.tickets_pulled = True


def menu():
    action = ""
    space = "\n" * 50
    # only pulling rom DB if it has data to pull
    if User.user_count > 0 and not User.users_pulled:
        pull_users_from_db()
    if Ticket.created_tickets > 0 and not Ticket.tickets_pulled:
        pull_tickets_from_db()

    while action.lower() != "q":
        print(space + "|********************************| ")
        print(" [ Logged in as: {} ]".format(User.colored_user))
        print(" [ Workgroup: {} ]".format(User.colored_workgroup))
        print(" [ Tickets Assigned: {} ]".format(len(User.logged_in_user.assigned_tickets)))
        print("|********************************|\n"
              "\n1.Login or [C to Create User])\n2.Create Ticket\n3.Ticket Lookup\n"
              "4.Resolve Ticket\n5.Un-resolve Ticket\n6.Assign Ticket\n -[Q to Quit]-")
        action = input("\nSelection: ")
        if action == "1" and User.user_count > 0:
            user_login()
        elif action == "1" and User.user_count < 1:
            print(colored("**No Users Exist, Please Create a User First**", "red"))
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
                print(colored("**Please Create a Ticket First**", "red"))
                input("[Enter to continue...]")

        elif action.lower() != "q":
            print(colored("**Please Login First**", "red"))
            input("[Enter to continue...]")

    print(colored("\n**Exiting ticket system**", "red"))
    input("[Enter to continue...]")
    sys.exit()


menu()
