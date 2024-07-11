import os
import csv
import pandas as pd
from cryptography.fernet import Fernet

# File to store the encryption key
KEY_FILE = '.encryption.key'  # Prefix with a dot to hide on Unix-based systems

# File to store passwords
PASSWORD_FILE = '.passwords.csv'  # Prefix with a dot to hide on Unix-based systems

# Function to set file as hidden on Windows
def set_hidden_windows(file_path):
    if os.name == 'nt':  # Check if the system is Windows
        os.system(f'attrib +h {file_path}')

# Generate or load the key
def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as file:
            key = file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as file:
            file.write(key)
        set_hidden_windows(KEY_FILE)
    return key

# Initialize the cipher suite with the loaded key
key = load_or_generate_key()
cipher_suite = Fernet(key)

# Initialize the CSV file if it doesn't exist
if not os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Domain', 'Encrypted_Password'])
    set_hidden_windows(PASSWORD_FILE)

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def add_password(domain, password):
    encrypted_password = encrypt_password(password)
    with open(PASSWORD_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([domain, encrypted_password])
    print(f"Password for {domain} added successfully.")

def update_password(domain, new_password):
    df = pd.read_csv(PASSWORD_FILE)
    if domain in df['Domain'].values:
        df.loc[df['Domain'] == domain, 'Encrypted_Password'] = encrypt_password(new_password)
        df.to_csv(PASSWORD_FILE, index=False)
        print(f"Password for {domain} updated successfully.")
    else:
        print(f"No password found for {domain}.")

def delete_password(domain):
    df = pd.read_csv(PASSWORD_FILE)
    if domain in df['Domain'].values:
        df = df[df['Domain'] != domain]
        df.to_csv(PASSWORD_FILE, index=False)
        print(f"Password for {domain} deleted successfully.")
    else:
        print(f"No password found for {domain}.")

def view_password(domain):
    df = pd.read_csv(PASSWORD_FILE)
    if domain in df['Domain'].values:
        encrypted_password = df.loc[df['Domain'] == domain, 'Encrypted_Password'].values[0]
        print(f"Password for {domain} is: {decrypt_password(encrypted_password)}")
    else:
        print(f"No password found for {domain}.")

def view_all_passwords():
    df = pd.read_csv(PASSWORD_FILE)
    if not df.empty:
        print("All stored passwords:")
        for index, row in df.iterrows():
            domain = row['Domain']
            encrypted_password = row['Encrypted_Password']
            decrypted_password = decrypt_password(encrypted_password)
            print(f"Domain: {domain}, Password: {decrypted_password}")
    else:
        print("No passwords stored yet.")

def main():
    while True:
        command = input("Enter command (add/update/delete/view/viewall/exit): ").strip().lower()
        if command == "add":
            domain = input("Enter domain: ").strip()
            password = input("Enter password: ").strip()
            add_password(domain, password)
        elif command == "update":
            domain = input("Enter domain: ").strip()
            new_password = input("Enter new password: ").strip()
            update_password(domain, new_password)
        elif command == "delete":
            domain = input("Enter domain: ").strip()
            delete_password(domain)
        elif command == "view":
            domain = input("Enter domain: ").strip()
            view_password(domain)
        elif command == "viewall":
            view_all_passwords()
        elif command == "exit":
            break
        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
