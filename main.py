from core import logic

def start_engine():
    # Hum 'logic' file ke andar se 'sam_processor' ko bula hain hain
    result = logic.sam_processor("System is Live")
    print(result)

if __name__ == "__main__":
    start_engine()
