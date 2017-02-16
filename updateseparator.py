'''
Created on Feb 10, 2017

@author: Andre
'''
from datetime import datetime


class UpdateSeparator:
    
    def __init__(self):
        self.break_line = "--------------------------------"
        pass
    def get_separator(self):
        return self.break_line+str(datetime.now())