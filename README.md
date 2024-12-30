🎟️ Cinema Ticket Booking System

A Python-based cinema ticket booking system that provides an end-to-end solution for managing user sign-up, movie and seat selection, booking, payment processing, and ticket validation with QR code integration.

🚀 Features

User Management: User registration and login functionality.

Location & Cinema Management: Add cities, cinemas, and studios.

Movie Management: Add and display movies based on cities and cinemas.

Seat Booking: View seat availability and book seats.

Payment Processing: Supports multiple payment methods (Cash, Card, E-Wallet).

QR Code Integration: Generate QR codes for tickets and validate them using a camera.

Data Persistence: Stores all data in an SQLite database.

Seating Chart: Visual representation of available and booked seats.

🛠️ Tech Stack

Programming Language: Python

Database: SQLite

Libraries:

qrcode for QR code generation

cv2 (OpenCV) for QR code scanning via the camera

pyzbar for decoding QR codes

csv for data management (optional)

🐂️ Database Structure

Tables

users: Stores user information.

locations: Stores cinema locations.

cinemas: Stores cinema details.

studios: Stores studio details within cinemas.

movies: Stores movie details.

seats: Stores seat information for each movie.

bookings: Stores booking details, including payment status.

🗈️ Setup Instructions

Clone this repository:

git clone https://github.com/your-username/cinema-ticket-booking.git

Navigate to the project directory:

cd cinema-ticket-booking

Install required libraries:

pip install qrcode opencv-python pyzbar

Run the script to initialize the database:

python ticket_booking.py

🎮 How to Use

1. User Registration & Login

Register a new user with a username, password, and phone number.

Login with the registered credentials to access features.

2. Add Movies and Locations

Run the setup_locations_and_movies() function to populate the database with sample data.

3. Book Tickets

View available movies by city.

Select a movie and view the seat chart.

Choose your seats and confirm the booking.

4. Complete Payment

Choose a payment method (Cash, Card, E-Wallet).

Generate a QR code for your ticket upon successful payment.

5. Validate Ticket

Use a camera to scan the QR code and validate your ticket.

🖼️ Screenshots

Seating Chart:

QR Code Ticket:
