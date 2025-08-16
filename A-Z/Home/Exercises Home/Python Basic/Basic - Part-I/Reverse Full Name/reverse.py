first_name = input("Enter your first name: ")
last_name = input("Enter your last name: ")

comb_name = first_name + " " + last_name

name_list = list(comb_name)
name_list.reverse()
rev_name = "".join(name_list)
print(rev_name)