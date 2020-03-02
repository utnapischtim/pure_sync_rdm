


def add_spaces(value, max_spaces):
    spaces = max_spaces - len(str(value))
    return ''.ljust(spaces) + str(value)



l = [5, 88, 777, 6544, 98787, 21]

for i in l:
    response = add_spaces(i, 6)
    print(response)