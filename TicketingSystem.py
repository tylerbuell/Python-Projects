import DatabaseHandler
from termcolor import colored
import sys
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
        self.ID = DatabaseHandler.max_userid() + 1
        self.username = username
        self.workgroup = workgroup
        self.assigned_tickets = []
        self.logged_in = False

    def straight_assignment(self, user, ticket):
        previous_owner = ticket.assigned_user
        user_dict = User.user_dict
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

    def assign_ticket(self):
        print("Select a ticket ID to assign:\n")
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
            print("\nSelect a User to assign to:")
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
                "\n**Not Authorized to assign Ticket# {} for {} is assigned to a user in the {} workgroup **"
                    .format(ticket.ID, ticket.name, ticket.workgroup_assigned_to), "red"))
            input("[Enter to continue to menu]")

    def update_user(self):
        user_update_dict = {"Username": lambda: input("Updated Username: "),
                            "Workgroup": lambda: input("Updated Workgroup: ")}
        update_fields = list(user_update_dict.keys())
        print("Select User Field to Update:\n")
        print("Valid Fields: {}".format(update_fields))
        field = input("Field: ")
        while field not in update_fields:
            field = input("Field: ")
        current_value = getattr(self, field.lower())
        print("\n{} is currently: {}\n".format(field, current_value))
        updated_value = user_update_dict[field]()
        if field == "Workgroup":
            print(self.workgroups)
            updated_value = user_update_dict[field]()
            while updated_value not in self.workgroups:
                updated_value = user_update_dict[field]()
        update_check = input("Are you sure you want to set {} to {} for User ID# {}? (Y/N)"
                             .format(current_value, updated_value, self.ID))
        if update_check == "y":
            setattr(self, field.lower(), updated_value)
            DatabaseHandler.update_user(self, column=field.lower())
            print(colored("\n**{} Updated successfully to: {}**".format(field, updated_value), "blue"))
            input("[Enter to continue...]")
        else:
            print(colored("\n**{} was not updated**".format(field), "red"))
            input("[Enter to continue...]")


def create_user():
    space = "\n" * 50
    print(space + "Create User Account:\n-------------------")
    username = input("\nCreate Username: ")
    workgroup = workgroup_select()
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


def delete_user():
    print("\nSelect User to Delete:")
    tickets_remain = False
    del_user = user_select()
    user_tickets = len(del_user.assigned_tickets)
    if user_tickets > 0:
        tickets_remain = True
        remainder_tickets = del_user.assigned_tickets.copy()
        print(colored("\n**User {} has {} ticket(s) assigned".format(del_user.username, user_tickets), "red"))
        print("Choose a user to assign {}'s ticket(s) to:\n".format(del_user.username))
        assign_user = user_select()
        for ID in remainder_tickets:
            ticket = Ticket.tick_dict["ID"][ID]
            del_user.straight_assignment(assign_user, ticket)
        input("[Enter to continue]")
    deleted = DatabaseHandler.delete(del_user)
    User.user_count = DatabaseHandler.user_count()
    if deleted:
        if del_user.logged_in:
            log_out(del_user)
        print(colored("\n**{} from the {} workgroup Successfully Deleted**".
                      format(del_user.username, del_user.workgroup), "blue"))
        input("[Enter to continue...]")
        menu()
    else:
        if tickets_remain:
            for ID in remainder_tickets:
                ticket = Ticket.tick_dict["ID"][ID]
                assign_user.straight_assignment(del_user, ticket)
        print(colored("\n**User {} was NOT Deleted**".format(del_user.username, del_user.workgroup), "red"))
        input("[Enter to continue...]")
        menu()


def matching_item(username, user_list):
    for user in user_list:
        if username.lower() in user.lower():
            return user


def workgroup_select():
    valid_workgroups = sorted(User.workgroups)
    workgroup = ""
    while workgroup not in User.workgroups:
        print("\nValid Workgroups: {}".format(valid_workgroups))
        workgroup = input("Select Workgroup: ")
        if workgroup in valid_workgroups:
            break
        else:
            close_workgroup = matching_item(workgroup, valid_workgroups)
            while close_workgroup is not None:
                workgroup_check = input("Did you mean {}? (Y/N)".format(close_workgroup)).lower()
                if workgroup_check == "y":
                    workgroup = close_workgroup
                    break
                break
            else:
                print(colored("\n**Not a matching workgroup, try again**", "red"))
    return workgroup


def user_select():
    user_dict = User.user_dict
    valid_users = sorted(list(user_dict["username"].keys()))
    username = ""
    close_user = ""
    while username not in valid_users:
        print("\nValid Users: {}".format(list(valid_users)))
        username = input("Enter Username: ")
        if username in valid_users:
            break
        else:
            close_user = matching_item(username, valid_users)
            while close_user is not None:
                user_check = input("Did you mean {}? (Y/N)".format(close_user)).lower()
                if user_check == "y":
                    username = close_user
                    break
                break
            else:
                print(colored("\n**Not a matching user, try again**", "red"))
    user = user_dict["username"][username]
    return user


def log_out(user):
    User.colored_user = ""
    User.colored_workgroup = ""
    User.logged_in_username = ""
    User.logged_in_workgroup = ""
    User.logged_in_user = User.temp_user
    User.logged_in = False
    user.logged_in = False


def log_in(user):
    User.colored_user = colored(user.username, "blue")
    User.colored_workgroup = colored(user.workgroup, "red")
    User.logged_in_username = user.username
    User.logged_in_workgroup = user.workgroup
    User.logged_in_user = user
    User.logged_in = True
    user.logged_in = True


def user_login():
    space = "\n" * 50
    print(space + "Select a user to login as:")
    user = user_select()
    log_in(user)
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
        self.ID = DatabaseHandler.max_ticketid() + 1
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
                                                                                   self.status,
                                                                                   self.user_assigned_to + " - " +
                                                                                   self.workgroup_assigned_to,
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

    def update_ticket(self):
        ticket_update_dict = {"Name": lambda: input("Updated Name: "),
                              "Callback": lambda: input("Updated Callback #: "),
                              "Location": lambda: input("Updated Location: "),
                              "Summary": lambda: input("Updated Ticket Summary: "),
                              "Detail": lambda: Ticket.multiline_input("Updated Ticket Detail")}
        update_fields = list(ticket_update_dict.keys())
        print("\nSelect Ticket Field to Update:\n")
        print("Valid Fields: {}".format(update_fields))
        field = input("Field: ")
        while field not in update_fields:
            field = input("Field: ")
        current_value = getattr(self, field.lower())
        print("{} is currently: {}".format(field, current_value))
        updated_value = ticket_update_dict[field]()
        update_check = input("Are you sure you want to set {} to {} for ticket# {}? (Y/N)"
                             .format(current_value, updated_value, self.ID))
        if update_check == "y":
            setattr(self, field.lower(), updated_value)
            DatabaseHandler.update_ticket(self, column=field)
            print(colored("\n**{} Updated successfully to: {}**".format(field, updated_value), "blue"))
            input("[Enter to continue...]")
        else:
            print(colored("\n**{} was not updated**".format(field), "red"))
            input("[Enter to continue...]")
            menu()

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
            menu()
        else:
            print(colored("\n**Ticket# {} is still Open**".format(self.ID), "red"))
            input("[Enter to continue...]")
            menu()

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
            menu()
        else:
            print(colored("\n**Ticket# {} is still Resolved**".format(self.ID), "red"))
            input("[Enter to continue...]")
            menu()


def generate_ticket(user):
    space = "\n" * 50
    print(space + "Fill in ticket information to create a Ticket:\n")
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
    menu()


def delete_ticket():
    print("\nSelect Ticket ID to Delete:")
    ticket = ticket_select()
    deleted = DatabaseHandler.delete(ticket)
    # updating ticket count
    Ticket.created_tickets = DatabaseHandler.ticket_count()
    if deleted:
        print(colored("\n**Ticket# {} for {} Successfully Deleted**".format(ticket.ID, ticket.name), "blue"))
        input("[Enter to continue...]")
        menu()
    else:
        print(colored("\n**Ticket# {} was NOT deleted**".format(ticket.ID), "red"))
        input("[Enter to continue...]")
        menu()


def ticket_select():
    try:
        search = "ID"
        valid_tickets = list(Ticket.tick_dict["ID"].keys())
        print("\nValid Tickets: {}".format(valid_tickets))
        ID = input("Enter ticket ID: ")

        while ID == "" or int(ID) not in valid_tickets:
            print(colored("**Invalid Ticket ID**", "red"))
            ID = input("\nEnter Ticket ID: ")
        ticket = Ticket.tick_dict[search][int(ID)]
        print(ticket)
        input("[Enter to select this ticket]")
        return ticket
    except KeyError:
        print("\n**Ticket {} doesn't exist**".format(ID))
        input("[Enter to continue to menu]")
        menu()


def ticket_lookup():
    error = True
    space = "\n" * 50
    print(
        space + "Select a lookup method:\n\n1.Ticket ID#\n2.My Tickets\n3.Name on Ticket\n4.Name of Creator\n5.Open Tickets\n6.Resolved "
                "Tickets\n7.Assigned Tickets")
    search_method = input("\nSelect search method: ")
    try:
        if search_method == "1":
            search = "ID"
            valid_ids = list(Ticket.tick_dict[search].keys())
            print("\nValid IDs: {}".format(valid_ids))
            ID = input("Enter Ticket ID: ")

            while ID == "" or int(ID) not in valid_ids:
                print(colored("**Invalid Ticket ID**", "red"))
                ID = input("\nEnter Ticket ID: ")
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
            close_name = ""
            name = ""
            valid_names = list(Ticket.tick_dict[search].keys())
            while name not in valid_names:
                print("\nValid ticket names: {}".format(valid_names))
                name = input("Enter ticket Name: ")
                if name in valid_names:
                    break
                else:
                    close_name = matching_item(name, valid_names)
                    while close_name is not None:
                        name_check = input("Did you mean {}? (Y/N)".format(close_name)).lower()
                        if name_check == "y":
                            name = close_name
                            break
                        break
                    else:
                        print(colored("\n**Not a matching ticket name, try again**", "red"))
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
            creator = ""
            close_creator = ""
            valid_creators = list(Ticket.tick_dict[search].keys())
            while creator not in valid_creators:
                print("\nValid creators: {}".format(valid_creators))
                creator = input("Enter Creator name: ")
                if creator in valid_creators:
                    break
                else:
                    close_creator = matching_item(creator, valid_creators)
                    while close_creator is not None:
                        name_check = input("Did you mean {}? (Y/N)".format(close_creator)).lower()
                        if name_check == "y":
                            creator = close_creator
                            break
                        break
                    else:
                        print(colored("\n**Not a matching creator, try again**", "red"))
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
            workgroup = workgroup_select()
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


def search_tickets():
    results = False
    ticket_dict = Ticket.tick_dict
    print("\nEnter Keywords to search by:\n")
    keywords = input("Keywords (separated by comma): ").split(",")
    for ticket in ticket_dict["ID"].values():
        ticket_details = [str(ticket.ID),ticket.creator,ticket.name,ticket.location,ticket.summary,ticket.detail.split(" ")]
        for keyword in keywords:
           for i in ticket_details:
               if keyword in i:
                   results = True
                   print(ticket)
                   input("[Enter to continue...]")

    if not results:
        print(colored("No tickets match Keywords: {}".format(keywords), "red"))
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
                                                  "Location, Summary, Detail,Assigned_User,Workgroup,Status,Resolved,Resolution_Note",
                                        "")
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

        # print(ticket.tick_dict["ID"])
        # print(ticket.tick_dict["name"])
        # print(ticket.tick_dict["creator"])
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
              "\n1.Login \n2.Create User [UU to Update User or DU to Delete User]"
              "\n3.Create Ticket [UT to Update Ticket or DT to Delete Ticket]\n4.Ticket Lookup [S to search keywords]\n"
              "5.Resolve Ticket\n6.Un-resolve Ticket\n7.Assign Ticket\n -[Q to Quit]-")
        action = input("\nSelection: ")
        if action == "1" and User.user_count > 0:
            user_login()
        elif action == "1" and User.user_count < 1:
            print(colored("**No Users Exist, Please Create a User First**", "red"))
            input("[Enter to continue...]")
            create_user()
        if action.lower() == "2":
            create_user()
        if User.logged_in:
            if action.lower() == "uu":
                print("\nSelect a user ID to update:")
                user = user_select()
                user.update_user()
                menu()
            if action.lower() == "du":
                delete_user()
            if action == "3":
                generate_ticket(User.logged_in_user)
            if Ticket.created_tickets > 0:
                if action.lower() == "ut":
                    print("\nSelect a ticket ID to update:")
                    ticket = ticket_select()
                    ticket.update_ticket()
                if action.lower() == "dt":
                    delete_ticket()
                if action == "4":
                    ticket_lookup()
                if action.lower() == "s":
                    search_tickets()
                if action == "5":
                    print("\nSelect a ticket ID to resolve:")
                    ticket = ticket_select()
                    ticket.resolve()
                if action == "6":
                    print("\nSelect a ticket ID to un-resolve:")
                    ticket = ticket_select()
                    ticket.unresolve()
                if action == "7" and User.user_count > 1:
                    User.logged_in_user.assign_ticket()
                elif action == "7":
                    print(colored("**No additional users to assign to**", "red"))
                    input("[Enter to continue...]")
            elif action.lower() != "q" and action.lower() in ["dt", "ut", "4", "5", "6", "7"]:
                print(colored("**Please Create a Ticket First**", "red"))
                input("[Enter to continue...]")
        elif action.lower() != "q":
            print(colored("**Please Login First**", "red"))
            input("[Enter to continue...]")
    print(colored("\n**Exiting ticket system**", "red"))
    input("[Enter to continue...]")
    sys.exit()


menu()
