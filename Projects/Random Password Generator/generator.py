import random
import string

def random_password_generator(length):
    mix = string.digits + string.ascii_lowercase + string.ascii_uppercase + string.punctuation

    password = ''.join(random.choice(mix) for i in range(length))

    return password

def main():

    try:
        user_input = input("Enter length of password: ").strip()
        if user_input == "":
            length = 8
        else:
            length = int(user_input)
        print("Your password is:",random_password_generator(length))

    except ValueError:
        print("Enter integer only")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()