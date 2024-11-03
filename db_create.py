import mysql.connector
from mysql.connector import Error
from faker import Faker
import random
from datetime import date

DB_NAME = "my_database"
DB_USER = "yaroslav"
DB_PASSWORD = "passYaroslav"
DB_HOST = "mysql"
DB_PORT = "3306"

# Set Faker to use the Ukrainian locale
fake = Faker('uk_UA')

# Define lists of common Ukrainian middle names by gender
male_middle_names = ["Олексійович", "Петрович", "Іванович", "Сергійович", "Миколайович"]
female_middle_names = ["Олексіївна", "Петрівна", "Іванівна", "Сергіївна", "Миколаївна"]
phone_regex = r"^\+380\d{9}$"  # Регулярний вираз для перевірки номера без пробілів

def get_middle_name(first_name):
    # Визначення статі на основі першої літери імені
    male_middle_names = ["Олексійович", "Петрович", "Іванович", "Сергійович", "Миколайович"]
    female_middle_names = ["Олексіївна", "Петрівна", "Іванівна", "Сергіївна", "Миколаївна"]

    # Використовуємо першу літеру для визначення статі
    first_letter = first_name[-1].lower()
    if first_letter in ['о', 'а', 'и', 'я']:  # Список літер, що вказують на жіноче ім'я
        return random.choice(female_middle_names)
    else:
        return random.choice(male_middle_names)

def clean_phone_number(phone_number):
    return ''.join(filter(str.isdigit, phone_number))  # Залишити лише цифри

def create_tables():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS clients (
            client_id INT AUTO_INCREMENT PRIMARY KEY,
            client_type VARCHAR(50) NOT NULL,
            address VARCHAR(100) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS phones (
            phone_number VARCHAR(20) PRIMARY KEY,
            client_id INT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tariffs (
            tariff_id INT AUTO_INCREMENT PRIMARY KEY,
            call_type VARCHAR(20) NOT NULL,
            cost_per_minute DECIMAL(5, 2) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS calls (
            call_id INT AUTO_INCREMENT PRIMARY KEY,
            call_date DATE NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            duration_minutes INT NOT NULL CHECK (duration_minutes > 0),
            tariff_id INT NOT NULL,
            FOREIGN KEY (phone_number) REFERENCES phones(phone_number),
            FOREIGN KEY (tariff_id) REFERENCES tariffs(tariff_id)
        )
        """
    ]
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cur = conn.cursor()

        for command in commands:
            cur.execute(command)

        conn.commit()
        print("Tables created successfully.")

        cur.close()
        conn.close()
    except Error as error:
        print(f"Error: {error}")

def insert_data():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cur = conn.cursor()

        # Generate client data with Ukrainian names and addresses
        client_data = []
        for _ in range(5):
            # Вибір статі
            gender = random.choice(['male', 'female'])

            client_type = random.choice(['фізична особа', 'відомство'])
            address = fake.address()

            # Генерація імені та прізвища в залежності від статі
            if gender == 'male':
                first_name = fake.first_name_male()
                last_name = fake.last_name_male()
                middle_name = random.choice(male_middle_names)  # Вибір побатькового
            else:
                first_name = fake.first_name_female()
                last_name = fake.last_name_female()
                middle_name = random.choice(female_middle_names)  # Вибір побатькового

            client_data.append((client_type, address, last_name, first_name, middle_name))

        cur.executemany("""INSERT INTO clients (client_type, address, last_name, first_name, middle_name)
                          VALUES (%s, %s, %s, %s, %s)""", client_data)

        # Retrieve all client IDs from the clients table
        cur.execute("SELECT client_id FROM clients")
        client_ids = [row[0] for row in cur.fetchall()]

        phone_data = []

        # Ensure each client has one phone number
        for client_id in client_ids:
            phone_number = fake.phone_number()  # Generate a phone number using Faker
            phone_data.append((phone_number, client_id))

        # Randomly select 2 clients to assign an additional phone number
        additional_phone_count = 2
        additional_clients = random.sample(client_ids, min(additional_phone_count, len(client_ids)))

        # Assign an additional phone number to the selected clients
        for client_id in additional_clients:
            phone_number = fake.phone_number()  # Generate another phone number
            phone_data.append((phone_number, client_id))

        cur.executemany("""INSERT INTO phones (phone_number, client_id)
                          VALUES (%s, %s)""", phone_data)

        # Insert tariff data in Ukrainian
        tariff_data = [
            ('внутрішній', 0.20),
            ('міжміський', 1.50),
            ('мобільний', 2.00)
        ]
        cur.executemany("""INSERT INTO tariffs (call_type, cost_per_minute)
                          VALUES (%s, %s)""", tariff_data)

        # Generate call data
        call_data = []
        for _ in range(20):
            call_date = fake.date_between_dates(date_start=date(2024, 10, 1), date_end=date(2024, 10, 31))
            phone_number = random.choice(phone_data)[0]  # Select a phone number from generated phone data
            duration_minutes = random.randint(1, 60)
            tariff_id = random.randint(1, 3)
            call_data.append((call_date, phone_number, duration_minutes, tariff_id))

        cur.executemany("""INSERT INTO calls (call_date, phone_number, duration_minutes, tariff_id)
                          VALUES (%s, %s, %s, %s)""", call_data)

        conn.commit()
        print("Data inserted successfully.")

        cur.close()
        conn.close()
    except Error as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    create_tables()
    insert_data()