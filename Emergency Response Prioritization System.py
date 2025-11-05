import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

def merge_sort(arr, key):
    if len(arr) > 1:
        mid = len(arr)//2
        L = arr[:mid]
        R = arr[mid:]

        merge_sort(L, key)
        merge_sort(R, key)

        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i][key] > R[j][key]:  # Descending order
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1

 
class EmergencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Response System")
        self.root.geometry("750x500")
        self.root.config(bg="#EAF6F6")

        self.emergencies = []

        # Title Label
        tk.Label(
            root, text=" Emergency Response Prioritization System",
            font=("Arial", 18, "bold"), bg="#EAF6F6", fg="#003366"
        ).pack(pady=15)

        # Frame for input fields
        frame = tk.Frame(root, bg="#EAF6F6")
        frame.pack(pady=10)

        tk.Label(frame, text="Emergency ID:", bg="#EAF6F6").grid(row=0, column=0, padx=5, pady=5)
        self.id_entry = tk.Entry(frame)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Severity (1-10):", bg="#EAF6F6").grid(row=1, column=0, padx=5, pady=5)
        self.severity_entry = tk.Entry(frame)
        self.severity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Distance (km):", bg="#EAF6F6").grid(row=2, column=0, padx=5, pady=5)
        self.distance_entry = tk.Entry(frame)
        self.distance_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(root, text="Add Emergency", command=self.add_emergency,
                  bg="#0077B6", fg="white", font=("Arial", 11, "bold")).pack(pady=10)

        tk.Button(root, text="Sort & Show Priority Order", command=self.sort_emergencies,
                  bg="#00B4D8", fg="white", font=("Arial", 11, "bold")).pack(pady=5)

        self.output_text = tk.Text(root, height=10, width=70, bg="#F0F8FF", fg="#003366")
        self.output_text.pack(pady=10)

    # Add emergency data
    def add_emergency(self):
        try:
            ID = self.id_entry.get().strip()
            severity = float(self.severity_entry.get())
            distance = float(self.distance_entry.get())

            if not ID:
                raise ValueError("ID cannot be empty")

            priority = (severity * 2) - distance
            self.emergencies.append({"ID": ID, "Severity": severity, "Distance": distance, "Priority": priority})

            messagebox.showinfo("Success", f"Emergency {ID} added successfully!")
            self.id_entry.delete(0, tk.END)
            self.severity_entry.delete(0, tk.END)
            self.distance_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for Severity and Distance.")

    # Sort and visualize
    def sort_emergencies(self):
        if not self.emergencies:
            messagebox.showwarning("No Data", "Please add emergencies first.")
            return

        merge_sort(self.emergencies, "Priority")

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Emergency Response Order (High → Low Priority):\n\n")
        for e in self.emergencies:
            self.output_text.insert(tk.END, f"{e['ID']} --> Priority: {e['Priority']:.2f}\n")

        # Visualize using matplotlib
        ids = [e['ID'] for e in self.emergencies]
        priorities = [e['Priority'] for e in self.emergencies]

        plt.figure(figsize=(8, 5))
        plt.bar(ids, priorities, color="crimson")
        plt.xlabel("Emergency Case ID")
        plt.ylabel("Priority Value")
        plt.title("Emergency Priority Visualization (Merge Sort Output)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.show()

 
# Run the program
 
if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyApp(root)
    root.mainloop()
