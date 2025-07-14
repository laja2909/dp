class DataSource:
    def __init__(self,name:str, type:str):
        self.name = name
        self._type = type

    def get_type(self):
        return self._type

class DataTask:
    def __init__(self,name:str):
        self.name = name
        print(f'You created Datatask of {self.name}')
        
    def add_data_source(self,data_source:DataSource):
        self._data_source = data_source
    def add_data_target(self,data_source:DataSource):
        self._data_target = data_source

    def set_task_type(self,task_type:str):
        #incremental
        #full refresh
        self._task_type = task_type
    def get_task_type(self):
        return self._task_type


