"""Create a separate seller account."""
from getpass import getpass

from werkzeug.security import generate_password_hash

from database import create_user, get_user_by_username, init_db, set_user_role


def main():
    init_db()
    username = input("Seller username: ").strip()
    if not username or len(username) > 40 or not username.replace("_", "").replace("-", "").isalnum():
        raise SystemExit("Use a username of 1 to 40 letters, numbers, underscores, or hyphens.")
    if get_user_by_username(username):
        raise SystemExit("That username already exists. Choose a new seller username; member accounts are unchanged.")

    name = input("Seller name: ").strip()
    email = input("Email (optional): ").strip().lower() or None
    password = getpass("Password (8+ characters): ")
    if not name or len(name) > 80 or len(password) < 8 or len(password) > 256:
        raise SystemExit("Enter a name of 1 to 80 characters and a password of 8 to 256 characters.")
    user_id = create_user(name, username, email, generate_password_hash(password))
    set_user_role(user_id, "admin")
    print("Separate seller account created.")


if __name__ == "__main__":
    main()
