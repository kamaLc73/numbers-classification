import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import tensorflow as tf
import io

# Charger le modèle
model = tf.keras.models.load_model('static/mnist.keras', custom_objects={'softmax': tf.nn.softmax})

class DigitRecognizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reconnaissance de chiffre manuscrit (MNIST)")

        self.canvas_width = 280
        self.canvas_height = 280
        self.brush_size = 20  
        self.total_predictions = 0
        self.correct_predictions = 0         

        self.image = Image.new("L", (self.canvas_width, self.canvas_height), color="white")
        self.draw = ImageDraw.Draw(self.image)

        self.create_widgets()
        self.bind_keys()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack()

        self.canvas = tk.Canvas(frame, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=6, padx=10, pady=10)
        self.canvas.bind("<B1-Motion>", self.paint)

        self.mini_img_label = ttk.Label(frame)
        self.mini_img_label.grid(row=6, column=0, pady=(5, 10))

        self.result_label = ttk.Label(frame, text="Chiffre prédit : ", font=("Arial", 16))
        self.result_label.grid(row=0, column=1, sticky="w")

        self.predict_button = ttk.Button(frame, text="Prédire", command=self.predict)
        self.predict_button.grid(row=1, column=1, sticky="ew")

        self.clear_button = ttk.Button(frame, text="Effacer", command=self.clear)
        self.clear_button.grid(row=2, column=1, sticky="ew")

        self.save_button = ttk.Button(frame, text="Sauvegarder", command=self.save)
        self.save_button.grid(row=3, column=1, sticky="ew")

        # Boutons correct / incorrect
        self.correct_button = ttk.Button(frame, text="✔ Correct", command=self.mark_correct)
        self.correct_button.grid(row=4, column=1, sticky="ew", pady=(10, 0))

        self.incorrect_button = ttk.Button(frame, text="✘ Incorrect", command=self.mark_incorrect)
        self.incorrect_button.grid(row=5, column=1, sticky="ew")

        # Compteur manuel
        self.counter_label = ttk.Label(frame, text="Corrects : 0 / 0")
        self.counter_label.grid(row=6, column=1, sticky="w", pady=(10, 0))

        # Historique
        ttk.Label(frame, text="Historique :").grid(row=7, column=1, sticky="w")
        self.history = tk.Listbox(frame, height=4)
        self.history.grid(row=8, column=1, sticky="ew")

        # Probabilités
        ttk.Label(frame, text="Top 3 probabilités :").grid(row=9, column=1, sticky="w")
        self.top_probs = tk.Listbox(frame, height=3)
        self.top_probs.grid(row=10, column=1, sticky="ew")

    def bind_keys(self):
        self.root.bind("<c>", lambda event: self.clear())
        self.root.bind("<v>", lambda event: self.predict())

    def paint(self, event):
        r = self.brush_size // 2
        x1, y1, x2, y2 = event.x - r, event.y - r, event.x + r, event.y + r
        self.canvas.create_oval(x1, y1, x2, y2, fill='black', outline='black')
        self.draw.ellipse([x1, y1, x2, y2], fill='black')

    def clear(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (self.canvas_width, self.canvas_height), color="white")
        self.draw = ImageDraw.Draw(self.image)

    def save(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image.save(file_path)

    def predict(self):
        img = self.image.resize((28, 28), Image.Resampling.LANCZOS)
        img_array = 255 - np.array(img)
        img_array = img_array / 255.0
        img_array = img_array.reshape(1, 28, 28)

        prediction = model.predict(img_array)[0]
        predicted_digit = np.argmax(prediction)

        self.result_label.config(text=f"Chiffre prédit : {predicted_digit} ({prediction[predicted_digit]*100:.2f}%)")

        # Affichage top 3
        top_3 = sorted([(i, prediction[i]) for i in range(10)], key=lambda x: x[1], reverse=True)[:3]
        self.top_probs.delete(0, tk.END)
        for digit, prob in top_3:
            self.top_probs.insert(tk.END, f"{digit}: {prob*100:.2f}%")

        self.history.insert(0, f"{predicted_digit} ({prediction[predicted_digit]*100:.1f}%)")

        # Générer et afficher la miniature
        mini_img = img.resize((56, 56), Image.NEAREST)
        mini_img_rgb = mini_img.convert("RGB")
        buffer = io.BytesIO()
        mini_img_rgb.save(buffer, format="PNG")
        buffer.seek(0)
        self.mini_img_tk = ImageTk.PhotoImage(data=buffer.read())
        self.mini_img_label.config(image=self.mini_img_tk)

    def mark_correct(self):
        self.total_predictions += 1
        self.correct_predictions += 1
        self.update_counter_label()

    def mark_incorrect(self):
        self.total_predictions += 1
        self.update_counter_label()

    def update_counter_label(self):
        self.counter_label.config(text=f"Corrects : {self.correct_predictions} / {self.total_predictions}")

# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = DigitRecognizerApp(root)
    root.mainloop()
