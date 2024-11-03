import mysql.connector
from prettytable import PrettyTable


config = {
    "user": "yaroslav",
    "password": "passYaroslav",
    "host": "localhost",
    "database": "my_database"
}


def connect_to_db():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("Підключення до бази даних встановлено.")
        return connection
    except mysql.connector.Error as e:
        print(f"Помилка підключення до бази даних: {e}")
        return None


def fetch_and_print_table_structure(cursor, table_name):
    cursor.execute(f"DESCRIBE {table_name}")
    structure = cursor.fetchall()
    table_structure = PrettyTable()
    table_structure.field_names = ["Field", "Type", "Null", "Key", "Default", "Extra"]

    for row in structure:
        table_structure.add_row(row)

    print(f"\nСтруктура таблиці `{table_name}`:")
    print(table_structure)


def fetch_and_print_table_data(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    table_data = PrettyTable()
    table_data.field_names = columns

    for row in rows:
        table_data.add_row(row)

    print(f"\nДані таблиці `{table_name}`:")
    print(table_data)


def main():

    connection = connect_to_db()
    if not connection:
        return

    cursor = connection.cursor()


    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()


    for (table_name,) in tables:
        fetch_and_print_table_structure(cursor, table_name)
        fetch_and_print_table_data(cursor, table_name)


    cursor.close()
    connection.close()
    print("\nПідключення до бази даних закрито.")


if __name__ == "__main__":
    main()