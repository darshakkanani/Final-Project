import string

user_input = input("Enter your password to check strength: ")

if len(user_input) >= 8:
    a = b = c = d = 0
    for char in user_input:
        if char in string.ascii_lowercase:
            a = a + 1
        elif char in string.ascii_uppercase:
            b = b + 1
        elif char in string.digits:
            c = c + 1
        elif char in string.punctuation:
            d = d + 1
    if a > 0 and b > 0 and c > 0 and d > 0:
        print("Yes")
    else:
        print("No")
else:
    print("No")

