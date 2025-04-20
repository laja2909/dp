class RemoteSSH:
    def __init__(self, hostname:str,port:int=22):
        self._hostname = hostname
        self._port = port
    