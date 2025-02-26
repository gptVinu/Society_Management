import mysql.connector
import hashlib

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Vinu@8898",
                database="society_management"
            )
            self.cursor = self.conn.cursor(buffered=True)
        except mysql.connector.Error as err:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Vinu@8898"
            )
            self.cursor = self.conn.cursor(buffered=True)
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS society_management")
            self.conn.database = "society_management"

    def create_tables(self):
        # Create tables if they don't exist (removed DROP TABLE statements)
        # Members table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            flat_number VARCHAR(50) NOT NULL UNIQUE,
            contact VARCHAR(50) NOT NULL,
            pin VARCHAR(4),
            is_admin BOOLEAN DEFAULT FALSE,
            admin_password VARCHAR(255)
        )
        """)
        
        # Complaints table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            flat_number VARCHAR(50),
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            status ENUM('pending', 'resolved') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flat_number) REFERENCES members(flat_number)
        )
        """)
        
        # Maintenance table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            flat_number VARCHAR(50),
            amount DECIMAL(10,2) NOT NULL,
            month VARCHAR(20) NOT NULL,
            year INT NOT NULL,
            status ENUM('paid', 'unpaid') DEFAULT 'unpaid',
            FOREIGN KEY (flat_number) REFERENCES members(flat_number)
        )
        """)
        
        # Insert default admin only if no admin exists
        self.cursor.execute("SELECT COUNT(*) FROM members WHERE is_admin = TRUE")
        if self.cursor.fetchone()[0] == 0:
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute("""
            INSERT INTO members (name, flat_number, contact, is_admin, admin_password)
            VALUES ('Admin', 'ADMIN', '0000000000', TRUE, %s)
            """, (admin_password,))
            
        self.conn.commit()

    def authenticate_admin(self, admin_id, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("""
        SELECT id, name FROM members 
        WHERE flat_number = %s AND admin_password = %s AND is_admin = TRUE
        """, (admin_id, hashed_password))
        return self.cursor.fetchone()

    def authenticate_member(self, flat_number, pin):
        self.cursor.execute("""
        SELECT id, name, flat_number FROM members 
        WHERE flat_number = %s AND pin = %s AND is_admin = FALSE
        """, (flat_number, pin))
        return self.cursor.fetchone()

    def add_member(self, name, flat_number, contact, pin):
        self.cursor.execute("""
        INSERT INTO members (name, flat_number, contact, pin)
        VALUES (%s, %s, %s, %s)
        """, (name, flat_number, contact, pin))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_member(self, flat_number, name, contact, pin):
        self.cursor.execute("""
        UPDATE members SET name = %s, contact = %s, pin = %s
        WHERE flat_number = %s
        """, (name, contact, pin, flat_number))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_member(self, flat_number):
        try:
            flat_number = str(flat_number)  # Ensure flat_number is string
            if (flat_number.upper() == 'ADMIN'):
                return False
                
            # First delete related records from maintenance and complaints tables
            self.cursor.execute("DELETE FROM maintenance WHERE flat_number = %s", (flat_number,))
            self.cursor.execute("DELETE FROM complaints WHERE flat_number = %s", (flat_number,))
            # Then delete the member
            self.cursor.execute("DELETE FROM members WHERE flat_number = %s AND is_admin = FALSE", (flat_number,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def get_members(self):
        self.cursor.execute("SELECT name, flat_number, contact FROM members WHERE is_admin = FALSE")
        return self.cursor.fetchall()

    def get_member_by_flat(self, flat_number):
        self.cursor.execute("""
        SELECT id, name, flat_number, contact
        FROM members 
        WHERE flat_number = %s AND is_admin = FALSE
        """, (flat_number,))
        return self.cursor.fetchone()

    def get_member_name(self, flat_number):
        self.cursor.execute("""
        SELECT name FROM members 
        WHERE flat_number = %s AND is_admin = FALSE
        """, (flat_number,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_flat_numbers(self):
        """Get all flat numbers except admin"""
        self.cursor.execute("SELECT flat_number FROM members WHERE is_admin = FALSE ORDER BY flat_number")
        return [row[0] for row in self.cursor.fetchall()]

    def add_complaint(self, flat_number, title, description):
        self.cursor.execute("""
        INSERT INTO complaints (flat_number, title, description)
        VALUES (%s, %s, %s)
        """, (flat_number, title, description))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_complaints(self, flat_number=None):
        if (flat_number):
            self.cursor.execute("SELECT * FROM complaints WHERE flat_number = %s", (flat_number,))
        else:
            self.cursor.execute("SELECT * FROM complaints")
        return self.cursor.fetchall()

    def submit_complaint(self, flat_number, title, description):
        try:
            self.cursor.execute("""
            INSERT INTO complaints (flat_number, title, description)
            VALUES (%s, %s, %s)
            """, (flat_number, title, description))
            self.conn.commit()
            return True
        except:
            return False

    def get_complaints_by_flat(self, flat_number):
        self.cursor.execute("""
        SELECT id, title, description, status, created_at 
        FROM complaints 
        WHERE flat_number = %s 
        ORDER BY created_at DESC
        """, (flat_number,))
        return self.cursor.fetchall()

    def maintenance_exists(self, flat_number, month, year):
        """Check if maintenance record already exists for given flat, month and year"""
        self.cursor.execute("""
        SELECT COUNT(*) FROM maintenance 
        WHERE flat_number = %s AND month = %s AND year = %s
        """, (flat_number, month, year))
        return self.cursor.fetchone()[0] > 0

    # Basic maintenance methods
    def add_maintenance(self, flat_number, amount, month, year):
        self.cursor.execute("""
        INSERT INTO maintenance (flat_number, amount, month, year)
        VALUES (%s, %s, %s, %s)
        """, (flat_number, amount, month, year))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_maintenance(self, flat_number=None):
        if flat_number:
            self.cursor.execute("SELECT * FROM maintenance WHERE flat_number = %s", (flat_number,))
        else:
            self.cursor.execute("SELECT * FROM maintenance")
        return self.cursor.fetchall()

    def get_maintenance_filtered(self, month=None, year=None):
        query = "SELECT * FROM maintenance WHERE 1=1"
        params = []
        
        if month:
            query += " AND month = %s"
            params.append(month)
        
        if year:
            query += " AND year = %s"
            params.append(year)
        
        query += " ORDER BY year DESC, FIELD(month, 'January', 'February', 'March', 'April', 'May', " + \
                "'June', 'July', 'August', 'September', 'October', 'November', 'December')"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update_maintenance_status(self, record_id, status):
        try:
            self.cursor.execute("""
            UPDATE maintenance SET status = %s
            WHERE id = %s
            """, (status, record_id))
            self.conn.commit()
            return True
        except:
            return False

    def pay_maintenance(self, maintenance_id):
        try:
            self.cursor.execute("""
            UPDATE maintenance 
            SET status = 'paid' 
            WHERE id = %s
            """, (maintenance_id,))
            self.conn.commit()
            return True
        except:
            return False
