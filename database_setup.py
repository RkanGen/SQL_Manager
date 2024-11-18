import mysql.connector
from datetime import datetime, timedelta
import random
import faker
import pandas as pd
import numpy as np

class DatabaseSetup:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        self.database = database
        self.fake = faker.Faker()
        
    def create_database(self):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        self.cursor.execute(f"USE {self.database}")
        print(f"Database '{self.database}' created successfully!")

    def create_tables(self):
        """Create all necessary tables"""
        # Categories table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INT PRIMARY KEY AUTO_INCREMENT,
                category_name VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Products table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT PRIMARY KEY AUTO_INCREMENT,
                category_id INT,
                product_name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                stock_quantity INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        """)

        # Customers table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT PRIMARY KEY AUTO_INCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Orders table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT PRIMARY KEY AUTO_INCREMENT,
                customer_id INT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) NOT NULL,
                status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                shipping_address TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)

        # Order Items table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT,
                product_id INT,
                quantity INT NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                subtotal DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)

        print("All tables created successfully!")

    def generate_sample_data(self):
        """Generate and insert sample data into all tables"""
        # Sample categories
        categories = [
            ("Electronics", "Electronic devices and accessories"),
            ("Clothing", "Apparel and fashion items"),
            ("Books", "Books and publications"),
            ("Home & Garden", "Home improvement and garden supplies"),
            ("Sports", "Sports equipment and accessories")
        ]
        
        self.cursor.executemany(
            "INSERT INTO categories (category_name, description) VALUES (%s, %s)",
            categories
        )
        self.conn.commit()

        # Sample product names for each category
        product_names = {
            1: [ # Electronics
                "Smartphone", "Laptop", "Tablet", "Headphones", "Smart Watch",
                "Camera", "Speaker", "Power Bank", "Gaming Console", "Monitor"
            ],
            2: [ # Clothing
                "T-Shirt", "Jeans", "Dress", "Jacket", "Sweater",
                "Shorts", "Skirt", "Coat", "Socks", "Hat"
            ],
            3: [ # Books
                "Novel", "Textbook", "Cookbook", "Biography", "Science Fiction",
                "Mystery", "History Book", "Self-Help", "Comic Book", "Dictionary"
            ],
            4: [ # Home & Garden
                "Plant Pot", "Garden Tools", "Lamp", "Pillow", "Blanket",
                "Curtains", "Rug", "Storage Box", "Vase", "Clock"
            ],
            5: [ # Sports
                "Basketball", "Tennis Racket", "Soccer Ball", "Yoga Mat", "Dumbbells",
                "Running Shoes", "Bicycle", "Swimming Goggles", "Golf Clubs", "Jump Rope"
            ]
        }

        # Generate products
        products = []
        for category_id in range(1, 6):
            for product_name in product_names[category_id]:
                product = (
                    category_id,
                    product_name,
                    self.fake.text(max_nb_chars=100),
                    round(random.uniform(10, 1000), 2),
                    random.randint(0, 1000)
                )
                products.append(product)

        self.cursor.executemany(
            """INSERT INTO products 
               (category_id, product_name, description, price, stock_quantity)
               VALUES (%s, %s, %s, %s, %s)""",
            products
        )
        self.conn.commit()

        # Generate customers
        customers = []
        for _ in range(100):  # 100 customers
            customer = (
                self.fake.first_name(),
                self.fake.last_name(),
                self.fake.email(),
                self.fake.phone_number(),
                self.fake.address()
            )
            customers.append(customer)

        self.cursor.executemany(
            """INSERT INTO customers 
               (first_name, last_name, email, phone, address)
               VALUES (%s, %s, %s, %s, %s)""",
            customers
        )
        self.conn.commit()

        # Generate orders and order items
        order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        for _ in range(1000):  # 1000 orders
            # Generate order
            customer_id = random.randint(1, 100)
            order_date = self.fake.date_time_between(start_date='-1y', end_date='now')
            status = random.choice(order_statuses)
            
            # Insert order
            self.cursor.execute(
                """INSERT INTO orders 
                   (customer_id, order_date, total_amount, status, shipping_address)
                   VALUES (%s, %s, %s, %s, %s)""",
                (customer_id, order_date, 0, status, self.fake.address())
            )
            order_id = self.cursor.lastrowid

            # Generate order items
            total_amount = 0
            num_items = random.randint(1, 5)
            
            for _ in range(num_items):
                product_id = random.randint(1, 50)
                quantity = random.randint(1, 5)
                
                # Get product price
                self.cursor.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
                unit_price = self.cursor.fetchone()[0]
                subtotal = unit_price * quantity

                # Insert order item
                self.cursor.execute(
                    """INSERT INTO order_items 
                       (order_id, product_id, quantity, unit_price, subtotal)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (order_id, product_id, quantity, unit_price, subtotal)
                )
                
                total_amount += subtotal

            # Update order total
            self.cursor.execute(
                "UPDATE orders SET total_amount = %s WHERE order_id = %s",
                (total_amount, order_id)
            )

        self.conn.commit()
        print("Sample data generated successfully!")

    def close_connection(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()
        print("Database connection closed.")

def main():
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',  # Update with your MySQL username
        'password': '00000000000',  # Update with your MySQL password
        'database': 'retail_db'
    }

    try:
        # Initialize and setup database
        db_setup = DatabaseSetup(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )

        # Create database and tables
        db_setup.create_database()
        db_setup.create_tables()

        # Generate sample data
        db_setup.generate_sample_data()

        # Close connection
        db_setup.close_connection()

        print("Database setup completed successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()