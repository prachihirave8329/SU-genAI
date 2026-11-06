
while True:
    print("\n----- JanAushadhiFinder Menu -----")
    print("1. About JanAushadhiFinder")
    print("2. Sample Questions")
    print("3. Medicine Information")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("JanAushadhiFinder helps people find nearby Jan Aushadhi Kendras.")

    elif choice == "2":
        print("Sample Questions:")
        print("What is JanAushadhiFinder?")
        print("Where is the nearest Kendra?")
        print("Where can I get medicine information?")

    elif choice == "3":
        query = input("Enter stock or kendra: ")

        if query.lower() == "stock":
            print("Please contact the Kendra to check medicine stock.")

        elif query.lower() == "kendra":
            print("You can check the official Kendra locator.")

        else:
            print("Please enter a valid query.")

    elif choice == "0":
        print("Thank you for using JanAushadhiFinder!")
        break

    else:
        print("Invalid choice. Please try again.")
