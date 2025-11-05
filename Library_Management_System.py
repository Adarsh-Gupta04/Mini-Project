import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import date

# Database setup
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    quantity INTEGER NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS issued_books (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    student_name TEXT,
    issue_date TEXT,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
)''')

conn.commit()

# GUI setup
root = tk.Tk()
root.title("Library Management System")
root.geometry("750x550")
root.config(bg="#E3F2FD")

# Functions
def add_book():
    title = title_entry.get()
    author = author_entry.get()
    quantity = quantity_entry.get()
    if title and author and quantity:
        cursor.execute("INSERT INTO books(title, author, quantity) VALUES (?, ?, ?)",
                       (title, author, int(quantity)))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully!")
        title_entry.delete(0, tk.END)
        author_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "All fields are required!")

def view_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Available Books:\n\n")
    for book in books:
        output_text.insert(tk.END, f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} | Qty: {book[3]}\n")

def issue_book():
    book_id = issue_book_id_entry.get()
    student_name = student_name_entry.get()
    cursor.execute("SELECT quantity FROM books WHERE book_id=?", (book_id,))
    book = cursor.fetchone()
    if book and book[0] > 0:
        cursor.execute("INSERT INTO issued_books(book_id, student_name, issue_date) VALUES (?, ?, ?)",
                       (book_id, student_name, date.today()))
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE book_id=?", (book_id,))
        conn.commit()
        messagebox.showinfo("Issued", f"Book ID {book_id} issued to {student_name}")
        issue_book_id_entry.delete(0, tk.END)
        student_name_entry.delete(0, tk.END)
        view_issued_books()
    else:
        messagebox.showerror("Error", "Book not available or invalid ID!")

def return_book():
    book_id = return_book_id_entry.get()
    cursor.execute("SELECT * FROM issued_books WHERE book_id=?", (book_id,))
    issued = cursor.fetchone()
    if issued:
        cursor.execute("DELETE FROM issued_books WHERE book_id=?", (book_id,))
        cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE book_id=?", (book_id,))
        conn.commit()
        messagebox.showinfo("Returned", f"Book ID {book_id} returned successfully!")
        return_book_id_entry.delete(0, tk.END)
        view_issued_books()
    else:
        messagebox.showerror("Error", "This book is not currently issued!")

def view_issued_books():
    cursor.execute("SELECT * FROM issued_books")
    records = cursor.fetchall()
    issued_text.delete("1.0", tk.END)
    issued_text.insert(tk.END, "Issued Books:\n\n")
    for rec in records:
        issued_text.insert(
            tk.END,
            f"Issue ID: {rec[0]} | Book ID: {rec[1]} | Student: {rec[2]} | Date: {rec[3]}\n"
        )

# Widgets
tk.Label(root, text="Library Management System", font=("Arial", 18, "bold"), bg="#E3F2FD").pack(pady=10)

frame = tk.Frame(root, bg="#BBDEFB", padx=10, pady=10)
frame.pack(pady=5)

tk.Label(frame, text="Title:").grid(row=0, column=0)
title_entry = tk.Entry(frame)
title_entry.grid(row=0, column=1)

tk.Label(frame, text="Author:").grid(row=1, column=0)
author_entry = tk.Entry(frame)
author_entry.grid(row=1, column=1)

tk.Label(frame, text="Quantity:").grid(row=2, column=0)
quantity_entry = tk.Entry(frame)
quantity_entry.grid(row=2, column=1)

tk.Button(frame, text="Add Book", command=add_book, bg="#64B5F6").grid(row=3, column=0, pady=5)
tk.Button(frame, text="View Books", command=view_books, bg="#64B5F6").grid(row=3, column=1, pady=5)

# Issue section
tk.Label(root, text="Issue Book", font=("Arial", 13, "bold"), bg="#E3F2FD").pack(pady=5)
tk.Label(root, text="Book ID:").pack()
issue_book_id_entry = tk.Entry(root)
issue_book_id_entry.pack()
tk.Label(root, text="Student Name:").pack()
student_name_entry = tk.Entry(root)
student_name_entry.pack()
tk.Button(root, text="Issue Book", command=issue_book, bg="#4FC3F7").pack(pady=5)

# Return section
tk.Label(root, text="Return Book", font=("Arial", 13, "bold"), bg="#E3F2FD").pack(pady=5)
tk.Label(root, text="Book ID:").pack()
return_book_id_entry = tk.Entry(root)
return_book_id_entry.pack()
tk.Button(root, text="Return Book", command=return_book, bg="#4FC3F7").pack(pady=5)

# Display areas
output_text = tk.Text(root, height=6, width=90)
output_text.pack(pady=5)

issued_text = tk.Text(root, height=6, width=90)
issued_text.pack(pady=5)

tk.Button(root, text="View Issued Books", command=view_issued_books, bg="#81D4FA").pack(pady=5)
tk.Button(root, text="Exit", command=root.quit, bg="#E57373").pack(pady=5)

root.mainloop()
