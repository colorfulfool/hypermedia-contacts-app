import sqlite3
import re
from flask import flash

class Contact:
    db_path = 'contacts.db'

    def __init__(self, id=None, first_name='', last_name='', phone='', email=''):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.errors = {}

    def validate(self):
        self.errors = {}
        
        if not self.email:
            self.errors['email'] = "Email is required"
        elif '@' not in self.email:
            self.errors['email'] = "Email is invalid"

        if self.phone and not re.match(r'^\d{10,}$', self.phone):
            self.errors['phone'] = "Phone must be 10+ digits"
            
        return len(self.errors) == 0

    def save(self):
        if not self.validate():
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if self.id is None:  # Insert new contact
                cursor.execute('''
                    INSERT INTO contacts (first_name, last_name, phone, email)
                    VALUES (?, ?, ?, ?)
                ''', (self.first_name, self.last_name, self.phone, self.email))
                self.id = cursor.lastrowid
            else:  # Update existing contact
                cursor.execute('''
                    UPDATE contacts
                    SET first_name=?, last_name=?, phone=?, email=?
                    WHERE id=?
                ''', (self.first_name, self.last_name, self.phone, self.email, self.id))
            
            conn.commit()
            return True
            
        except sqlite3.Error:
            self.errors['db'] = ["Database error"]
            return False
        finally:
            conn.close()

    def delete(self):
        """Delete the current contact instance from the database."""
        if self.id is None:
            return False
            
        try:
            success = Contact.delete_by_id(self.id)
            if success:
                self.id = None  # Mark as deleted
            return success
        except Exception:
            return False

    @classmethod
    def delete_by_id(cls, contact_id):
        """Delete a contact by ID. Returns True on success, False on failure."""
        try:
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return affected_rows > 0
        except sqlite3.Error:
            return False

    @classmethod
    def all(cls):
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, first_name, last_name, phone, email FROM contacts')
        rows = cursor.fetchall()
        conn.close()
        return [cls(*row) for row in rows]

    @classmethod
    def search(cls, query):
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        search_term = f'%{query}%'
        cursor.execute('''
            SELECT id, first_name, last_name, phone, email 
            FROM contacts
            WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
        ''', (search_term, search_term, search_term))
        rows = cursor.fetchall()
        conn.close()
        return [cls(*row) for row in rows]

    @classmethod
    def find(cls, contact_id):
        try:
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, first_name, last_name, phone, email 
                FROM contacts 
                WHERE id = ?
            ''', (contact_id,))
            row = cursor.fetchone()
            conn.close()
            return cls(*row) if row else None
        except sqlite3.Error:
            return None

    @classmethod
    def create_table(cls):
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                email TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
