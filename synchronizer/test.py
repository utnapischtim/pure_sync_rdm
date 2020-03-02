
num = 54861

# ----------

digits = 1

while True:
    num /= 10
    if num < 1:
        break
    digits += 1

print(digits)

# ----------

digits = len(str(num))

print(digits)