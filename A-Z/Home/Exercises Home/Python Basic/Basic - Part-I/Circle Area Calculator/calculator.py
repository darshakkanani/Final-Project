def area(r):
    return 3.14*r*r

def main():
    try:
        r = int(input("Enter the radius: "))
        print(round(area(r),4))
    except ValueError:
        print("Enter integers only")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
