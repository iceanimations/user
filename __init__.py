from site import addsitedir as asd
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")

if True:
    import tactic_client_lib as tcl

    from socket import error as socketerror
    from xmlrpclib import ProtocolError, Fault

    import logging
    import types
    import os
    import time
    import getpass


class TacticUserException(tcl.TacticApiException):
    pass


class TacticServerMeta(type):
    '''metaclass which wrap all inherited methods with retries in case of any
    error that occured due to network conditions'''

    __retries__ = 2

    def __new__(mcls, name, bases, namespace):
        namespace['__retries__'] = mcls.__retries__
        for key, value in bases[0].__dict__.items():
            if isinstance(value, types.FunctionType):
                namespace[key] = mcls._wrap(value)
        cls = super(TacticServerMeta, mcls).__new__(
                mcls, name, bases, namespace)
        return cls

    @classmethod
    def _wrap(mcls, func):
        def _wrapper(self, *args, **kwargs):
            for i in range(self.__retries__):
                try:
                    return func(self, *args, **kwargs)
                except (socketerror, ProtocolError) as e:
                    logging.error('Swallowing a Network Error: %s' % str(e))
            return func(self, *args, **kwargs)
        _wrapper.__orig_func__ = func
        _wrapper.__doc__ = func.__doc__
        return _wrapper


class TacticServer(tcl.TacticServerStub):
    '''Tactic Server Meta will wrap all calls with retries'''
    __metaclass__ = TacticServerMeta

    def copy(self):
        new_server = TacticServer(setup=False)
        new_server.set_project(self.get_project())
        new_server.set_server(self.get_server_name())
        new_server.login = self.login
        new_server.set_ticket(self.get_transaction_ticket())
        return new_server

    def create_resource_file(self):
        if self.login and self.ticket:
            resource_path = self.create_resource_path(self.login)
            if _mkdir(os.path.dirname(resource_path)):
                with open(resource_path, 'w') as file:
                    file.write("login=%s\n" % self.login)
                    file.write("server=%s\n" % server_name)
                    file.write("ticket=%s\n" % self.get_transaction_ticket())
                    if self.project_code:
                        file.write("project=%s\n" % self.project_code)
            else:
                raise TacticUserException("Cannot create resource dir")
        else:
            raise TacticUserException("User is not logger in!")

    def delete_resource_file(self):
        if self.login:
            resource_path = self.create_resource_path(self.login)
        else:
            resource_path = self.create_resource_path()
        if os.path.exists(resource_path):
            os.unlink(resource_path)

    def test_conn(self):
        try:
            if self.login and self.ticket:
                return False
            self.ping()
        except (Fault, AttributeError):
            return False

    def log_in(self, login, password, project=None):
        ticket = self.get_ticket(login, password)
        self.login = login
        self.set_ticket(ticket)
        if project:
            self.set_project(project)
        return True

    def log_out(self):
        self.login = self.ticket = None


# if the user have not registered to Maya in the current
# Python session then `_present' will be `None'.

_present = True
_server = None
_age_limit = 47 * 3600

# change this get the server name/ip from a config file
server_name = 'ice-tactic'

def _mkdir(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            return False
        return True
    parent = os.path.dirname(path)
    if parent and _mkdir(parent):
        os.mkdir(path)
        return True


def _nascent_server():
    _server = TacticServer(setup=False)
    _server.set_server(server_name)
    return _server


def _assign_server():
    global _present, _server

    try:
        _server = TacticServer()
        resource_path = _server.create_resource_path()
        if os.path.exists(resource_path):
            age = time.time() - os.path.getmtime(resource_path)
            if age > _age_limit:
                raise TacticUserException()
        if not (_server.get_server_name() == server_name):
            raise TacticUserException("Server credentials don\'t match")
        _server.create_resource_path()
        _present = True

    except tcl.TacticApiException as exc:
        logging.warning(str(exc))
        _server = _nascent_server()
        _server.delete_resource_file()
        _present = None


def verify_server(force_new=False):
    global _present, _server
    if _server.verify_server():
        _present = True
    else:
        if force_new:
            _server = _nascent_server()
        _present = None
    return _present


def user_registered():
    if _present is not None:
        return True
    else:
        return False


def get_server():
    if user_registered():
        return _server
    else:
        raise TacticUserException("User not logged in.")


def get_server_copy():
    if user_registered():
        return _server.copy()
    else:
        raise TacticUserException("User not logged in.")


def _create_resource_file():
    if _server.login and _server.ticket and _server.login == getpass.getuser():
        _server.create_resource_file()
        return True


def login(login, password, project=None):
    global _present
    if _server.log_in(login, password, project):
        _create_resource_file()
        _present = True
        return True


def logout():
    global _present
    _server.log_out()
    _present = None


def get_user():
    if user_registered():
        return _server.get_login()
    else:
        raise TacticUserException("User not registered")


_assign_server()
