from auth import login
from payment import process_payment


def main():
    user = login()
    process_payment(user)


if __name__ == "__main__":
    main()
