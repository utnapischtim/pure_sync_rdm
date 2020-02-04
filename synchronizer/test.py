import json
import os
from pprint import pprint

dirpath = os.path.dirname(os.path.abspath(__file__))
file_name = dirpath + '/reports/to_delete.log'

with open(file_name, "r") as f:
    lines = f.readlines()
with open(file_name, "w") as f:
    for line in lines:
        if line.strip("\n") != "pa1eh-6c419":
            f.write(line)