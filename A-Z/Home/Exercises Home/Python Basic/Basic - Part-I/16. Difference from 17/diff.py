user_input = int(input("Enter the number: "))

if user_input <= 17:
	ans = 17 - user_input
	print(ans)
else:
	ans = (user_input - 17)*2
	print(ans)