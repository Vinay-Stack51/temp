from flask import Flask, render_template, request, jsonify, session
import chess
import chess.pgn
import random
import time

app = Flask(__name__)
app.secret_key = "chess_secret_2024"

# Global game state
board = chess.Board()
difficulty = "easy"
move_history = []
captured_white = []
captured_black = []

# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-square tables for positional evaluation
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_TABLE_MG = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

PIECE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE_MG
}


def get_piece_square_value(piece_type, square, color):
    table = PIECE_TABLES.get(piece_type, [0] * 64)
    if color == chess.WHITE:
        idx = (7 - chess.square_rank(square)) * 8 + chess.square_file(square)
    else:
        idx = chess.square_rank(square) * 8 + chess.square_file(square)
    return table[idx]


def evaluate_board(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return 99999
        else:
            return -99999

    score = 0
    for piece_type in PIECE_VALUES:
        for sq in board.pieces(piece_type, chess.WHITE):
            score += PIECE_VALUES[piece_type]
            score += get_piece_square_value(piece_type, sq, chess.WHITE)
        for sq in board.pieces(piece_type, chess.BLACK):
            score -= PIECE_VALUES[piece_type]
            score -= get_piece_square_value(piece_type, sq, chess.BLACK)

    # Mobility bonus
    score += len(list(board.legal_moves)) * 0.1
    return score


def order_moves(board, moves):
    """Sort moves: captures first, then checks, then others"""
    def move_priority(move):
        priority = 0
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker:
                priority += PIECE_VALUES.get(victim.piece_type, 0) - PIECE_VALUES.get(attacker.piece_type, 0) / 10
        board.push(move)
        if board.is_check():
            priority += 50
        board.pop()
        return -priority
    return sorted(moves, key=move_priority)


def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)
    legal_moves = order_moves(board, legal_moves)

    if maximizing:
        max_eval = -99999
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 99999
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def easy_ai():
    legal_moves = list(board.legal_moves)
    # Easy: random but prefers captures
    captures = [m for m in legal_moves if board.is_capture(m)]
    if captures and random.random() < 0.5:
        board.push(random.choice(captures))
    else:
        board.push(random.choice(legal_moves))


def intermediate_ai():
    best_move = None
    best_score = -99999
    legal_moves = list(board.legal_moves)
    legal_moves = order_moves(board, legal_moves)

    for move in legal_moves:
        board.push(move)
        score = evaluate_board(board)
        board.pop()
        if score > best_score:
            best_score = score
            best_move = move

    if best_move:
        board.push(best_move)


def hard_ai():
    best_move = None
    best_score = -99999
    legal_moves = list(board.legal_moves)
    legal_moves = order_moves(board, legal_moves)

    for move in legal_moves:
        board.push(move)
        score = minimax(board, 3, -99999, 99999, False)
        board.pop()
        if score > best_score:
            best_score = score
            best_move = move

    if best_move:
        board.push(best_move)


def ai_move():
    global difficulty
    if not board.legal_moves:
        return
    if difficulty == "easy":
        easy_ai()
    elif difficulty == "intermediate":
        intermediate_ai()
    else:
        hard_ai()


def get_game_status():
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return "checkmate", "🤖 AI wins by Checkmate!"
        else:
            return "checkmate", "🎉 You win by Checkmate!"
    elif board.is_stalemate():
        return "draw", "🤝 Draw by Stalemate"
    elif board.is_insufficient_material():
        return "draw", "🤝 Draw by Insufficient Material"
    elif board.is_seventyfive_moves():
        return "draw", "🤝 Draw by 75-Move Rule"
    elif board.is_check():
        return "check", "⚠️ Check!"
    return "ongoing", None


def get_captured_pieces():
    white_captures = []
    black_captures = []
    temp_board = chess.Board()
    for move in board.move_stack:
        if temp_board.is_capture(move):
            captured_sq = move.to_square
            piece = temp_board.piece_at(captured_sq)
            if piece:
                if piece.color == chess.WHITE:
                    black_captures.append(piece.symbol().upper())
                else:
                    white_captures.append(piece.symbol().upper())
        temp_board.push(move)
    return white_captures, black_captures


@app.route("/")
def home():
    return render_template("index.html", fen=board.fen(), difficulty=difficulty)


@app.route("/set_difficulty", methods=["POST"])
def set_difficulty():
    global difficulty
    data = request.json
    difficulty = data["difficulty"]
    return jsonify({"status": "ok"})


@app.route("/move", methods=["POST"])
def move():
    data = request.json
    uci = data["move"]

    # Handle promotion
    promotion = data.get("promotion", None)

    try:
        if promotion:
            promo_map = {"q": chess.QUEEN, "r": chess.ROOK, "b": chess.BISHOP, "n": chess.KNIGHT}
            chess_move = chess.Move.from_uci(uci + promotion)
        else:
            chess_move = chess.Move.from_uci(uci)
            # Auto-promote to queen
            if chess_move not in board.legal_moves:
                chess_move = chess.Move.from_uci(uci + "q")

        if chess_move in board.legal_moves:
            board.push(chess_move)

            if not board.is_game_over():
                ai_move()

            status, message = get_game_status()
            white_cap, black_cap = get_captured_pieces()

            return jsonify({
                "status": "ok",
                "fen": board.fen(),
                "game_status": status,
                "message": message,
                "white_captures": white_cap,
                "black_captures": black_cap,
                "move_count": len(list(board.move_stack))
            })

    except Exception as e:
        print(e)
        return jsonify({
            "status": "error",
            "message": str(e)
        })

    return jsonify({"status": "error", "message": "Illegal move"})


@app.route("/get_legal_moves", methods=["POST"])
def get_legal_moves():
    data = request.json
    square_name = data["square"]
    try:
        square = chess.parse_square(square_name)
        legal = [move.uci()[2:4] for move in board.legal_moves if move.from_square == square]
        return jsonify({"moves": legal})
    except:
        return jsonify({"moves": []})


@app.route("/reset")
def reset():
    global board
    board = chess.Board()
    return jsonify({"fen": board.fen(), "status": "ok"})


@app.route("/state")
def state():
    white_cap, black_cap = get_captured_pieces()
    status, message = get_game_status()
    return jsonify({
        "fen": board.fen(),
        "difficulty": difficulty,
        "white_captures": white_cap,
        "black_captures": black_cap,
        "move_count": len(list(board.move_stack)),
        "game_status": status,
        "message": message,
        "turn": "white" if board.turn == chess.WHITE else "black"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
