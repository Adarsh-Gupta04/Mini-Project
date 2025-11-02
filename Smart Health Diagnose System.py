import tkinter as tk
from tkinter import messagebox
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

 
symptoms = [
    "fever cough cold",
    "chest pain short breath",
    "headache blurred vision",
    "stomach pain nausea",
    "fever fatigue body ache",
    "sneezing runny nose cough"
]

diseases = ["Flu", "Heart Disease", "Migraine", "Food Poisoning", "Flu", "Cold"]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(symptoms)

model = MultinomialNB()
model.fit(X, diseases)

 
# Precautions for diseases
 
precautions = {
    "Flu": [
        "Rest well and stay hydrated",
        "Avoid close contact with others",
        "Take antiviral medication if prescribed"
    ],
    "Cold": [
        "Drink warm fluids",
        "Use tissues and dispose properly",
        "Rest and avoid cold exposure"
    ],
    "Heart Disease": [
        "Follow prescribed medications",
        "Avoid heavy exercise without doctor approval",
        "Maintain a healthy diet"
    ],
    "Migraine": [
        "Avoid triggers like loud lights or strong smells",
        "Take pain relief medication as advised",
        "Rest in a dark, quiet room"
    ],
    "Food Poisoning": [
        "Drink plenty of fluids",
        "Avoid solid foods until recovery",
        "See a doctor if symptoms are severe"
    ]
}

 
# Tkinter GUI
 
def submit():
    user_input = entry.get().strip()
    if not user_input:
        messagebox.showwarning("Input Error", "Please enter your symptoms!")
        return
    
    # Predict disease
    X_new = vectorizer.transform([user_input])
    prediction = model.predict(X_new)[0]

    # Get precautions
    disease_precautions = precautions.get(prediction, ["No precautions available."])


# GUI setup
root = tk.Tk()
root.title("Smart Health Diagnosis")
root.geometry("550x350")

tk.Label(root, text="Enter your symptoms (comma separated or space separated):", font=("Arial", 12)).pack(pady=10)
entry = tk.Entry(root, width=60)
entry.pack(pady=5)
tk.Button(root, text="Predict Disease", command=submit, bg="lightblue").pack(pady=10)
result_label = tk.Label(root, text="", font=("Arial", 11), wraplength=520, justify="left")
result_label.pack(pady=10)

root.mainloop()
