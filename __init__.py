

from site import addsitedir as asd
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")

import tactic_client_lib as tcl

# if the user have not registered to Maya in the current
# Python session then `_present' will be `None'.

_present = None

# change this get the server name/ip from a config file
server_name = "tactic"


server = tcl.TacticServerStub(setup = False)
server.set_server(server_name)

class _User(object):
    def __init__(self, login, ticket):
        pass

def login(login, password = None):
    global _present
    if _present:
        return _present
    else:
        ticket = server.get_ticket(login, password)
        server.login = login
        server.set_ticket(ticket)
        _present = True

def user_registered():
    if _present:
        return True
    else: return False

def get_server():

    if user_registered(): return server

    else: raise Exception("User not logged in.")


def logout():
    global _present
    _present = server.login = server.ticket = None
    


def get_user():
    if user_registered():
        return server.get_login()
    else:
        raise Exception("User not registered")

def get_server():
    return server
