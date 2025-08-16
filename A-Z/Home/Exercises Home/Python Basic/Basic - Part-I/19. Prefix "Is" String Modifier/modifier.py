user_input = input("Enter the string: ").strip()

list = list(user_input)

if list[0] == 'i' and list[1] == 's':
	print(user_input)
else:
	print("is "+user_input)