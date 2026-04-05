import datetime

def sam_processor(data, category="INFO"):
    """Logs data with a timestamp and category."""
    t = datetime.datetime.now().strftime("%H:%M:%S")
    return f"|SKJ| [{t}] [{category}] -> {data}"

def get_valid_name():
    """Prompts user for a valid alphabetic name and converts to UPPERCASE."""
    while True:
        name = input("Enter your name: ").strip()
        if name.replace(" ", "").isalpha():
            # Yahan humne .upper() lagaya hai
            return name.upper()
        print("Error: Naam mein sirf letters hone chahiye.")

def get_valid_age():
    """Prompts user for a valid positive integer age."""
    while True:
        try:
            age = int(input("Enter your age: "))
            if age >= 0:
                return age
            print("Error: Age positive honi chahiye.")
        except ValueError:
            print("Error: Please enter a valid number.")

def main():
    print("--- Python Basic Logic v2.0 (Final) ---")
    
    user_name = get_valid_name()
    user_age = get_valid_age()
    
    # Logs mein bhi naam Capital dikhega
    result = sam_processor(f"User {user_name} registered successfully.")
    print(f"\n{result}")
    
    print(f"HELLO {user_name}!")
    print(f"In 5 years, you will be {user_age + 5} years old.")

if __name__ == "__main__":
    main()
