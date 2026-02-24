from database import create_tables
from scanner import scan_directory
from search import search_by_name
from backup import create_backup
from restore import restore_backup

def main():
    create_tables()

    while True:
        print("\n1. Scan Directory")
        print("2. Search File")
        print("3. Backup File")
        print("4. Restore Backup")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            path = input("Enter folder path: ")
            scan_directory(path)

        elif choice == "2":
            name = input("Enter file name to search: ")
            search_by_name(name)

        elif choice == "3":
            path = input("Enter file path to backup: ")
            create_backup(path)

        elif choice == "4":
            path = input("Enter backup zip path: ")
            dest = input("Enter restore location: ")
            restore_backup(path, dest)

        elif choice == "5":
            break

        else:
            print("Invalid Choice")

if __name__ == "__main__":
    main()