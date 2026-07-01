# ♟️ AI Chess — Flask Web Application

An interactive web-based Chess application built with **Flask** and **python-chess**, featuring multiple AI difficulty levels, legal move validation, move history, pawn promotion, captured piece tracking and an intuitive user interface.

## 🚀 Features

* ♟️ Interactive chessboard with click-to-move controls
* ✅ Legal move highlighting
* 🤖 AI opponent with three difficulty levels:

  * Easy
  * Intermediate
  * Hard (Minimax-based)
* 📜 Move history in Standard Algebraic Notation (SAN)
* ♛ Pawn promotion support
* 💀 Captured pieces tracker
* 🔄 Flip board functionality
* 🏁 Automatic game-over detection
* 🎨 Responsive and user-friendly interface

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* python-chess

### Frontend

* HTML5
* CSS3
* JavaScript
* Chessboard.js

---

## 📂 Project Structure

```text
AI-Chess/
│
├── app.py                  # Flask backend and AI logic
├── requirements.txt        # Python dependencies
│
├── templates/
│   └── index.html          # Frontend UI
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone  https://github.com/Vinay-Stack51/temp
cd AI-Chess
```

### 2. Create a virtual environment (Optional)

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the Flask server:

```bash
python app.py
```

Open your browser and navigate to:

```text
http://localhost:5000
```

---

## 🎮 Gameplay

1. Launch the application.
2. Select the desired AI difficulty.
3. Click a piece to view its legal moves.
4. Click a highlighted square to make your move.
5. The AI automatically responds after each valid move.
6. Continue until the game ends by checkmate, stalemate, or another valid game-ending condition.

---

## 📦 Dependencies

* Flask
* python-chess

Install them using:

```bash
pip install -r requirements.txt
```

---

## 📌 Future Enhancements

* Opening book support
* Position evaluation bar
* PGN import/export
* Undo/Redo moves
* Move timer
* Online multiplayer
* AI vs AI mode
* Game analysis with engine evaluation
* Save and load completed games

---

## 👨‍💻 Author

Developed as an AI-powered Chess web application using Flask and Python.
