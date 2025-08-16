import hashlib

def encoder(normal_string: str) ->str:

    encoded_string = normal_string.encode('utf-8')

    sha256_hash = hashlib.sha256()

    sha256_hash.update(encoded_string)

    hex_value = sha256_hash.hexdigest()

    return hex_value

def main():

    try:
        normal_string = input("Enter the string: ").strip()
        if not normal_string:
            print("Enter valid string")
            return
    except:
        print("Enter valid string")
        return

    try:
        print("SHA-256 Hash:",encoder(normal_string))
    except Exception as e:
        print(f"Error occured: {e}")

if __name__  == "__main__":
    main()