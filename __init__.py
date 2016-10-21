

from site import addsitedir as asd
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")

import tactic_client_lib as tcl

from socket import error as socketerror
from xmlrpclib import ProtocolError

import logging


class TacticServer(object):
    __retries__ = 2

    def __init__(self, *args, **kwargs):
        self.server = tcl.TacticServerStub(*args, **kwargs)

    def __getattr__(self, name):
        stub = self.server
        attr = getattr(stub, name)
        if type(attr) == type(getattr(stub, 'set_ticket')):
            def _wrapper(*args, **kwargs):
                for i in range(self.__retries__):
                    try:
                        return attr(*args, **kwargs)
                    except (socketerror, ProtocolError) as e:
                        logging.error('Swallowing a network Error: %s'%str(e))
                return attr(*args, **kwargs)
            return _wrapper
        return attr

    def login():
        doc = "The login property."
        def fget(self):
            return self.server.get_login()
        def fset(self, value):
            self.server.login = value
        return locals()
    login = property(**login())


# if the user have not registered to Maya in the current
# Python session then `_present' will be `None'.

_present = None

# change this get the server name/ip from a config file
server_name = "ice-sql"
server = TacticServer(setup = False)
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

def get_server_copy():
    if user_registered():
        new_server = tcl.TacticServerStub(setup=False)
        new_server.set_project(server.get_project())
        new_server.set_server(server.get_server_name())
        new_server.set_ticket(server.get_transaction_ticket())
        return new_server
    else: raise Exception("User not logged in.")

def logout():
    global _present
    _present = server.login = server.ticket = None

def get_user():
    if user_registered():
        return server.get_login()
    else:
        raise Exception("User not registered")

