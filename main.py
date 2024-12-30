import sqlite3
import time
import qrcode
from datetime import datetime
import random
import cv2
from pyzbar.pyzbar import decode
import csv

# Connect to SQLite database
conn = sqlite3.connect('ticket_booking.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        phone TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cinemas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location_id INTEGER,
        FOREIGN KEY (location_id) REFERENCES locations (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS studios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cinema_id INTEGER,
        FOREIGN KEY (cinema_id) REFERENCES cinemas (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        genre TEXT,
        date TEXT,
        time TEXT,
        studio_id INTEGER,
        FOREIGN KEY (studio_id) REFERENCES studios (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        seat_label TEXT,
        is_booked INTEGER DEFAULT 0,
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT,
        username TEXT,
        movie_id INTEGER,
        seats TEXT,
        total_price INTEGER,
        type_payment TEXT,
        payment_status TEXT DEFAULT 'Pending',
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    )
''')

conn.commit()

def generate_qr_code(data, filename):
    """
    Generate a QR code using the given data and save it as an image file.
    """
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def scan_qr_code_with_camera():
    """
    Scan QR code using the computer's camera.
    """
    cap = cv2.VideoCapture(1)
    print("Align the QR code with the camera...")

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            cap.release()
            cv2.destroyAllWindows()
            return obj.data.decode('utf-8')

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

        if time.time() - start_time > 30:
            print("Auto-closing due to timeout.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

# Sign-up Function
def sign_up(username, password, phone):
    try:
        cursor.execute('INSERT INTO users (username, password, phone) VALUES (?, ?, ?)', (username, password, phone))
        conn.commit()
        return 'User registered successfully'
    except sqlite3.IntegrityError:
        return 'Username already exists'

# Login Function
def login(username, password):
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    return user is not None

# Add Locations, Cinemas, and Studios
movies_data = [
    {"title": "The Great Adventure", "genre": "Action", "date": "2024-12-20", "time": "18:00"},
    {"title": "Romantic Getaway", "genre": "Romance", "date": "2024-12-21", "time": "19:00"},
    {"title": "Mystery of the Night", "genre": "Mystery", "date": "2024-12-22", "time": "20:00"},
    {"title": "The Last Stand", "genre": "Drama", "date": "2024-12-23", "time": "21:00"},
    {"title": "Comedy Hour", "genre": "Comedy", "date": "2024-12-24", "time": "17:00"},
    {"title": "Horror Nights", "genre": "Horror", "date": "2024-12-25", "time": "22:00"},
    {"title": "Sci-Fi Chronicles", "genre": "Sci-Fi", "date": "2024-12-26", "time": "16:00"},
]

def setup_locations_and_movies():
    cities = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Medan', 'Makassar', 'Denpasar']
    cinemas = ['CGV', 'XXI', 'Cinepolis']

    for city in cities:
        cursor.execute('INSERT INTO locations (city) VALUES (?)', (city,))
        location_id = cursor.lastrowid

        for cinema in cinemas:
            cursor.execute('INSERT INTO cinemas (name, location_id) VALUES (?, ?)', (cinema, location_id))
            cinema_id = cursor.lastrowid

            for studio_num in range(1, 4):  # Each cinema has 3 studios
                studio_name = f"Studio {studio_num}"
                cursor.execute('INSERT INTO studios (name, cinema_id) VALUES (?, ?)', (studio_name, cinema_id))
                studio_id = cursor.lastrowid

                # Add 7 movies to each studio
                for movie in movies_data:
                    add_movie_to_studio(
                        studio_id,
                        movie["title"],
                        movie["genre"],
                        movie["date"],
                        movie["time"]
                    )

    conn.commit()

# Display Cinema Locations
def get_cinema_location(auto_detect, city=None):
    if auto_detect:
        # Simulate GPS auto-detection
        city = 'Bandung'
    elif not city:
        return 'City is required if GPS is not enabled'
    return city

# Add Movies
def add_movie_to_studio(studio_id, title, genre, date, time):
    cursor.execute('INSERT INTO movies (title, genre, date, time, studio_id) VALUES (?, ?, ?, ?, ?)',
                   (title, genre, date, time, studio_id))
    movie_id = cursor.lastrowid

    # Generate seats for the movie
    for row in 'ABCDEF':
        for num in range(1, 11):  # 10 seats per row
            seat_label = f"{row}{num}"
            cursor.execute('INSERT INTO seats (movie_id, seat_label) VALUES (?, ?)', (movie_id, seat_label))
    conn.commit()

# Display Movie Information
def display_movies(city):
    cursor.execute('''
        SELECT m.id, m.title, m.genre, m.date, m.time, s.name, c.name
        FROM movies m
        JOIN studios s ON m.studio_id = s.id
        JOIN cinemas c ON s.cinema_id = c.id
        JOIN locations l ON c.location_id = l.id
        WHERE l.city = ?
    ''', (city,))
    return cursor.fetchall()

# Select Seats
def get_available_seats(movie_id):
    cursor.execute('SELECT seat_label FROM seats WHERE movie_id = ? AND is_booked = 0', (movie_id,))
    return set(row[0] for row in cursor.fetchall())

def display_seat_chart(movie_id):
    """
    Display the seating chart for the given movie ID, indicating booked and available seats.
    """
    cursor.execute('SELECT seat_label, is_booked FROM seats WHERE movie_id = ?', (movie_id,))
    seats = cursor.fetchall()

    # Create a dictionary for easier seat lookup
    seat_map = {seat[0]: seat[1] for seat in seats}

    rows = 'ABCDEF'
    cols = range(1, 11)  # 10 seats per row

    print("\nSeating Chart:")
    print("  " + " ".join([f"{col:2}" for col in cols]))  # Print column numbers
    print("  " + "---" * len(cols))

    for row in rows:
        row_display = f"{row} "  # Start row with letter
        for col in cols:
            seat_label = f"{row}{col}"
            if seat_map.get(seat_label, 1) == 0:
                row_display += "[ ] "  # Available seat
            else:
                row_display += "[X] "  # Booked seat
        print(row_display)

    print("\n[X] = Booked, [ ] = Available")

def book_seat(username, movie_id, selected_seats):
    available_seats = get_available_seats(movie_id)

    if not available_seats.issuperset(selected_seats):
        return 'Some seats are not available'

    # Mark seats as booked
    cursor.executemany('UPDATE seats SET is_booked = 1 WHERE movie_id = ? AND seat_label = ?',
                       [(movie_id, seat) for seat in selected_seats])

    # Save booking details
    booking_id = str(int(time.time()))  # Unique booking ID
    total_price = len(selected_seats) * 50000  # Assume each ticket costs 50,000
    cursor.execute('INSERT INTO bookings (booking_id, username, movie_id, seats, total_price) VALUES (?, ?, ?, ?, ?)',
                   (booking_id, username, movie_id, ','.join(selected_seats), total_price))
    conn.commit()
    return booking_id, total_price

# Payment Process
def complete_payment(booking_id, type_payment):
    # Validate payment type
    if type_payment not in ('Cash', 'Card', 'E-Wallet'):
        raise ValueError('Invalid payment type')

    # Update database with payment status
    try:
        cursor.execute(
            'UPDATE bookings SET payment_status = ?, type_payment = ? WHERE booking_id = ?',
            ('Completed', type_payment, booking_id)
        )
        conn.commit()
    except Exception as e:
        raise RuntimeError(f"Database error: {e}")

    # Generate QR code
    qr_filename = f'qr_{booking_id}.png'
    try:
        generate_qr_code(booking_id, qr_filename)
    except Exception as e:
        raise RuntimeError(f"QR code generation failed: {e}")
    
    return qr_filename

# Ticket Validation
def validate_ticket(qr_code_data):
    cursor.execute('SELECT * FROM bookings WHERE booking_id = ? AND payment_status = ?', (qr_code_data, 'Completed'))
    booking = cursor.fetchone()
    return 'Valid Ticket' if booking else 'Invalid Ticket'

# Print Ticket
def print_ticket(booking_id):
    cursor.execute('''
        SELECT b.booking_id, b.username, m.title, m.date, m.time, s.name AS studio, c.name AS cinema, l.city, b.seats, b.payment_status
        FROM bookings b
        JOIN movies m ON b.movie_id = m.id
        JOIN studios s ON m.studio_id = s.id
        JOIN cinemas c ON s.cinema_id = c.id
        JOIN locations l ON c.location_id = l.id
        WHERE b.booking_id = ?
    ''', (booking_id,))
    ticket = cursor.fetchone()

    if ticket:
        ticket_info = f"""
        ======= TICKET =======
        Booking ID: {ticket[0]}
        Username: {ticket[1]}
        Movie: {ticket[2]}
        Date: {ticket[3]} {ticket[4]}
        Studio: {ticket[5]}
        Cinema: {ticket[6]}
        City: {ticket[7]}
        Seats: {ticket[8]}
        Payment Status: {ticket[9]}
        ======================
        """
        print(ticket_info)
        return ticket_info
    else:
        return "No ticket found for this Booking ID."
    


def display_movies_by_cinema(city):
    """
    Display cinemas in the chosen city and list movies available in the selected cinema.
    """
    # Retrieve cinemas in the chosen city
    cursor.execute('''
        SELECT c.id, c.name
        FROM cinemas c
        JOIN locations l ON c.location_id = l.id
        WHERE l.city = ?
    ''', (city,))
    cinemas = cursor.fetchall()

    if not cinemas:
        print("No cinemas found in the selected city.")
        return

    print("\nAvailable Cinemas in", city, ":")
    print("--------------------------------")
    for i, cinema in enumerate(cinemas[:3]):
        print(f"{cinema[0]}. {cinema[1]}")
    print("--------------------------------")

    # Select a cinema
    try:
        cinema_id = int(input("Enter cinema ID to view available movies: "))
        selected_cinema = next(cinema for cinema in cinemas if cinema[0] == cinema_id)
    except StopIteration:
        print("Invalid cinema ID.")
        return

    # Retrieve movies in the selected cinema
    cursor.execute('''
        SELECT m.id, m.title, m.genre, m.date, m.time, s.name
        FROM movies m
        JOIN studios s ON m.studio_id = s.id
        JOIN cinemas c ON s.cinema_id = c.id
        WHERE c.id = ?
    ''', (cinema_id,))
    movies = cursor.fetchall()

    if not movies:
        print("No movies available in the selected cinema.")
        return

    print("\nAvailable Movies in", selected_cinema[1], ":")
    print("-----------------------------------------------------------------")
    print("| ID | Title                | Genre      | Date       | Time  | Studio |")
    print("-----------------------------------------------------------------")
    for movie in movies:
        print(f"| {movie[0]:<2} | {movie[1]:<20} | {movie[2]:<10} | {movie[3]:<10} | {movie[4]:<5} | {movie[5]:<6} |")
    print("-----------------------------------------------------------------")

    return movies

def terminal_menu():
    setup_locations_and_movies()
    while True:
        print("\n=== TICKET BOOKING SYSTEM ===")
        print("1. Sign Up")
        print("2. Log In")
        print("3. Print Ticket")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            phone = input("Enter phone number: ")
            print(sign_up(username, password, phone))

        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")

            if login(username, password):
                print("Login successful!")
                city = input("Enter city or type 'auto' for GPS detection: ")
                if city.lower() == 'auto':
                    city = get_cinema_location(auto_detect=True)
                print("Selected city:", city)

                # Display cinemas and movies
                movies = display_movies_by_cinema(city)
                if movies:
                    try:
                        movie_id = int(input("Enter movie ID to book: "))

                        # Show seating chart
                        display_seat_chart(movie_id)

                        seats = input("Enter seats (comma-separated, e.g., A1,A2): ").split(',')
                        result = book_seat(username, movie_id, seats)

                        if result is None:
                            print("Booking failed. Please try again.")
                            continue

                        booking_id, total_price = result
                        print(f"Booking ID: {booking_id}, Total Price: {total_price}")

                        # Complete payment
                        confirm = input("Confirm payment? (yes/no): ").strip().lower()
                        if confirm == 'yes':
                            print("\nSelect Payment Type:")
                            print("1. Card")
                            print("2. Cash")
                            print("3. E-Wallet")

                            payment_choice = input("Choose payment type (1/2/3): ").strip()
                            payment_types = {"1": "Card", "2": "Cash", "3": "E-Wallet"}
                            type_payment = payment_types.get(payment_choice)

                            if not type_payment:
                                print("Invalid payment type. Payment canceled.")
                                continue

                            print(f"Selected Payment Type: {type_payment}")

                            try:
                                qr_code_file = complete_payment(booking_id, type_payment)
                                print(f"Payment successful! Payment Method: {type_payment}. QR Code saved as: {qr_code_file}")
                            except Exception as e:
                                print(f"Error: {e}")
                        elif confirm == 'no':
                            print("Payment canceled.")
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                    except ValueError:
                        print("Invalid input. Please enter valid IDs and seats.")
                    except Exception as e:
                        print(f"Unexpected error: {e}")
            else:
                print("Invalid username or password.")

        elif choice == '3':
            print("\n=== PRINT TICKET ===")
            print("1. Enter Booking ID")
            print("2. Scan QR Code")
            print("3. Back")
            sub_choice = input("Choose an option: ")

            if sub_choice == '1':
                booking_id = input("Enter Booking ID: ")
                print_ticket(booking_id)

            elif sub_choice == '2':
                print("Starting QR code scanner...")
                qr_code_data = scan_qr_code_with_camera()
                if qr_code_data and validate_ticket(qr_code_data) == 'Valid Ticket':
                    print_ticket(qr_code_data)
                else:
                    print("Invalid or unpaid ticket.")

            elif sub_choice == '3':
                continue

        elif choice == '4':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")
            
def export_table_to_csv(table_name, file_name):
    """
    Export the contents of a SQLite table to a CSV file.

    Args:
        table_name (str): The name of the SQLite table to export.
        file_name (str): The name of the output CSV file.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect('ticket_booking.db')
        cursor = conn.cursor()

        # Execute a query to fetch all data from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Fetch column names
        column_names = [description[0] for description in cursor.description]

        # Write data to CSV file
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the column headers
            writer.writerow(column_names)

            # Write the rows
            writer.writerows(rows)

        print(f"Table '{table_name}' has been exported to '{file_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    terminal_menu()
    tables_to_export = ["users", "locations", "cinemas", "studios", "movies", "seats", "bookings"]
    for table in tables_to_export:
        file_name = f"{table}.csv"
        export_table_to_csv(table, file_name)

    print("All tables have been exported to CSV files.")


