class DataSource:
    def __init__(self,name:str):
        self.name = name

class DataTask:
    def __init__(self,name:str):
        self.name = name
        print(f'You created Datatask of {self.name}')
        
    def add_data_source(self,data_source:DataSource):
        self._data_source = data_source
    def add_data_target(self,data_source:DataSource):
        self._data_target = data_source

