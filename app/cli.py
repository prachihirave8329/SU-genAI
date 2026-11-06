
from app.records import load_records, search, count_by, get_by_id


while True:
    print("\n===== JanAushadhiFinder =====")
    print("1. View all medicines")
    print("2. Search medicine")
    print("3. Count medicines by category")
    print("4. Find medicine by code")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        medicines = load_records()

        for medicine in medicines:
            print(medicine)

    elif choice == "2":
        keyword = input("Enter medicine name: ")
        results = search(keyword)

        if results:
            for medicine in results:
                print(medicine)
        else:
            print("Medicine not found.")

    elif choice == "3":
        counts = count_by()

        for category, count in counts.items():
            print(category, ":", count)

    elif choice == "4":
        drug_code = input("Enter drug code: ")
        medicine = get_by_id(drug_code)

        if medicine:
            print(medicine)
        else:
            print("Medicine code not found.")

    elif choice == "0":
        print("Thank you for using JanAushadhiFinder!")
        break

    else:
        print("Invalid choice. Please try again.")
