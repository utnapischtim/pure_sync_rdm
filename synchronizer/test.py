import os

dirpath = os.path.dirname(os.path.abspath(__file__))

file_toReTransfer = dirpath + "/reports/test.log"
to_delete = 'edo'

with open(file_toReTransfer, "r") as f:
    lines = f.readlines()
with open(file_toReTransfer, "w") as f:
    for line in lines:
        if line.strip("\n") != to_delete:
            f.write(line)