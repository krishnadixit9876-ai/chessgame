#   python chess_game.py

import pygame
import sys

pygame.init()
BOARD_SIZE = 640
UI_WIDTH = 300
WIDTH, HEIGHT = BOARD_SIZE + UI_WIDTH, BOARD_SIZE + 100
ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_SIZE // COLS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.current_player = 'white'
        self.selected_piece = None
        self.selected_pos = None
        self.king_moved = {'white': False, 'black': False}
        self.rook_moved = {'white': [False, False], 'black': [False, False]}
    
    def setup_board(self):
        # Black pieces
        self.board[0] = [Piece('black', 'rook'), Piece('black', 'knight'), Piece('black', 'bishop'), Piece('black', 'queen'),
                        Piece('black', 'king'), Piece('black', 'bishop'), Piece('black', 'knight'), Piece('black', 'rook')]
        self.board[1] = [Piece('black', 'pawn') for _ in range(8)]
        
        # White pieces
        self.board[6] = [Piece('white', 'pawn') for _ in range(8)]
        self.board[7] = [Piece('white', 'rook'), Piece('white', 'knight'), Piece('white', 'bishop'), Piece('white', 'queen'),
                        Piece('white', 'king'), Piece('white', 'bishop'), Piece('white', 'knight'), Piece('white', 'rook')]
    
    def reset(self):
        self.__init__()
    
    def is_valid_move(self, start_row, start_col, end_row, end_col):
        if end_row < 0 or end_row >= 8 or end_col < 0 or end_col >= 8:
            return False
        
        piece = self.board[start_row][start_col]
        if not piece:
            return False
            
        target = self.board[end_row][end_col]
        
        if target and target.color == piece.color:
            return False
        
        if piece.piece_type == 'pawn':
            direction = -1 if piece.color == 'white' else 1
            if start_col == end_col:
                if start_row + direction == end_row and not target:
                    return True
                if ((start_row == 6 and piece.color == 'white') or (start_row == 1 and piece.color == 'black')) and start_row + 2 * direction == end_row and not target:
                    return True
            elif abs(start_col - end_col) == 1 and start_row + direction == end_row and target:
                return True
        
        elif piece.piece_type == 'rook':
            if start_row == end_row or start_col == end_col:
                return self.is_path_clear(start_row, start_col, end_row, end_col)
        
        elif piece.piece_type == 'bishop':
            if abs(start_row - end_row) == abs(start_col - end_col):
                return self.is_path_clear(start_row, start_col, end_row, end_col)
        
        elif piece.piece_type == 'queen':
            if start_row == end_row or start_col == end_col or abs(start_row - end_row) == abs(start_col - end_col):
                return self.is_path_clear(start_row, start_col, end_row, end_col)
        
        elif piece.piece_type == 'king':
            if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:
                return True
            # Castling
            if not self.king_moved[piece.color] and start_row == end_row and abs(start_col - end_col) == 2:
                if end_col == 6:  # Kingside castling
                    if not self.rook_moved[piece.color][1] and self.board[start_row][7] and self.board[start_row][7].piece_type == 'rook':
                        if self.is_path_clear(start_row, start_col, start_row, 7):
                            return not self.is_in_check(piece.color)
                elif end_col == 2:  # Queenside castling
                    if not self.rook_moved[piece.color][0] and self.board[start_row][0] and self.board[start_row][0].piece_type == 'rook':
                        if self.is_path_clear(start_row, start_col, start_row, 0):
                            return not self.is_in_check(piece.color)
        
        elif piece.piece_type == 'knight':
            row_diff = abs(start_row - end_row)
            col_diff = abs(start_col - end_col)
            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                return True
        
        return False
    
    def is_path_clear(self, start_row, start_col, end_row, end_col):
        row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        
        current_row, current_col = start_row + row_step, start_col + col_step
        
        while current_row != end_row or current_col != end_col:
            if self.board[current_row][current_col]:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def make_move(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            piece = self.board[start_row][start_col]
            captured = self.board[end_row][end_col]
            
            # Handle castling
            if piece.piece_type == 'king' and abs(start_col - end_col) == 2:
                # Move king
                self.board[end_row][end_col] = self.board[start_row][start_col]
                self.board[start_row][start_col] = None
                
                # Move rook
                if end_col == 6:  # Kingside
                    self.board[start_row][5] = self.board[start_row][7]
                    self.board[start_row][7] = None
                elif end_col == 2:  # Queenside
                    self.board[start_row][3] = self.board[start_row][0]
                    self.board[start_row][0] = None
            else:
                # Normal move
                self.board[end_row][end_col] = self.board[start_row][start_col]
                self.board[start_row][start_col] = None
            
            # Check if move leaves king in check
            if self.is_in_check(self.current_player):
                # Undo move
                self.board[start_row][start_col] = piece
                self.board[end_row][end_col] = captured
                
                # Undo castling rook move if needed
                if piece.piece_type == 'king' and abs(start_col - end_col) == 2:
                    if end_col == 6:
                        self.board[start_row][7] = self.board[start_row][5]
                        self.board[start_row][5] = None
                    elif end_col == 2:
                        self.board[start_row][0] = self.board[start_row][3]
                        self.board[start_row][3] = None
                return False
            
            # Update castling flags
            if piece.piece_type == 'king':
                self.king_moved[piece.color] = True
            elif piece.piece_type == 'rook':
                if start_col == 0:
                    self.rook_moved[piece.color][0] = True
                elif start_col == 7:
                    self.rook_moved[piece.color][1] = True
            
            self.current_player = 'black' if self.current_player == 'white' else 'white'
            return True
        return False
    
    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color and piece.piece_type == 'king':
                    return row, col
        return None
    
    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        king_row, king_col = king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if self.is_valid_move(row, col, king_row, king_col):
                        return True
        return False
    
    def get_all_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.is_valid_move(row, col, end_row, end_col):
                                moves.append((row, col, end_row, end_col))
        return moves
    
    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        
        moves = self.get_all_moves(color)
        for move in moves:
            start_row, start_col, end_row, end_col = move
            captured = self.board[end_row][end_col]
            
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            
            still_in_check = self.is_in_check(color)
            
            self.board[start_row][start_col] = self.board[end_row][end_col]
            self.board[end_row][end_col] = captured
            
            if not still_in_check:
                return False
        return True
    
    def get_game_status(self):
        white_king = self.find_king('white')
        black_king = self.find_king('black')
        
        if not white_king or not black_king:
            return 'game_over'
        
        if self.is_checkmate(self.current_player):
            return 'checkmate'
        elif self.is_in_check(self.current_player):
            return 'check'
        
        # Check for stalemate
        moves = self.get_all_moves(self.current_player)
        legal_moves = []
        for move in moves:
            start_row, start_col, end_row, end_col = move
            captured = self.board[end_row][end_col]
            
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            
            if not self.is_in_check(self.current_player):
                legal_moves.append(move)
            
            self.board[start_row][start_col] = self.board[end_row][end_col]
            self.board[end_row][end_col] = captured
        
        if not legal_moves:
            return 'game_over'
        
        return 'normal'
    
    def evaluate_position(self):
        piece_values = {'pawn': 1, 'knight': 3, 'bishop': 3, 'rook': 5, 'queen': 9, 'king': 100}
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    value = piece_values[piece.piece_type]
                    if piece.color == 'black':
                        score += value
                        if 2 <= row <= 5 and 2 <= col <= 5:
                            score += 0.1
                        if piece.piece_type == 'pawn' and row > 3:
                            score += 0.2
                    else:
                        score -= value
                        if 2 <= row <= 5 and 2 <= col <= 5:
                            score -= 0.1
                        if piece.piece_type == 'pawn' and row < 4:
                            score -= 0.2
        return score
    
    def minimax(self, depth, maximizing, alpha=-float('inf'), beta=float('inf')):
        if depth == 0:
            return self.evaluate_position(), None
        
        moves = self.get_all_moves('black' if maximizing else 'white')
        if not moves:
            return self.evaluate_position(), None
        
        best_move = None
        
        if maximizing:
            max_eval = -float('inf')
            for move in moves[:15]:
                start_row, start_col, end_row, end_col = move
                captured = self.board[end_row][end_col]
                
                self.board[end_row][end_col] = self.board[start_row][start_col]
                self.board[start_row][start_col] = None
                
                eval_score, _ = self.minimax(depth - 1, False, alpha, beta)
                
                self.board[start_row][start_col] = self.board[end_row][end_col]
                self.board[end_row][end_col] = captured
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves[:15]:
                start_row, start_col, end_row, end_col = move
                captured = self.board[end_row][end_col]
                
                self.board[end_row][end_col] = self.board[start_row][start_col]
                self.board[start_row][start_col] = None
                
                eval_score, _ = self.minimax(depth - 1, True, alpha, beta)
                
                self.board[start_row][start_col] = self.board[end_row][end_col]
                self.board[end_row][end_col] = captured
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            return min_eval, best_move
    
    def ai_move(self):
        _, best_move = self.minimax(2, True)
        if best_move:
            start_row, start_col, end_row, end_col = best_move
            self.make_move(start_row, start_col, end_row, end_col)
            return True
        return False

def draw_piece(piece, x, y):
    center_x = x + SQUARE_SIZE // 2
    center_y = y + SQUARE_SIZE // 2
    piece_color = WHITE if piece.color == 'white' else BLACK
    outline_color = BLACK if piece.color == 'white' else WHITE
    
    if piece.piece_type == 'pawn':
        pygame.draw.circle(screen, piece_color, (center_x, center_y - 8), 10)
        pygame.draw.circle(screen, outline_color, (center_x, center_y - 8), 10, 2)
        pygame.draw.rect(screen, piece_color, (center_x - 6, center_y - 2, 12, 15))
        pygame.draw.rect(screen, outline_color, (center_x - 6, center_y - 2, 12, 15), 2)
    
    elif piece.piece_type == 'rook':
        pygame.draw.rect(screen, piece_color, (center_x - 12, center_y - 8, 24, 20))
        pygame.draw.rect(screen, outline_color, (center_x - 12, center_y - 8, 24, 20), 2)
        pygame.draw.rect(screen, piece_color, (center_x - 12, center_y - 18, 6, 10))
        pygame.draw.rect(screen, piece_color, (center_x - 3, center_y - 18, 6, 10))
        pygame.draw.rect(screen, piece_color, (center_x + 6, center_y - 18, 6, 10))
    
    elif piece.piece_type == 'knight':
        points = [(center_x - 8, center_y + 12), (center_x - 12, center_y + 5), 
                 (center_x - 10, center_y - 8), (center_x - 2, center_y - 12), 
                 (center_x + 8, center_y - 8), (center_x + 12, center_y + 2),
                 (center_x + 8, center_y + 12)]
        pygame.draw.polygon(screen, piece_color, points)
        pygame.draw.polygon(screen, outline_color, points, 2)
        pygame.draw.circle(screen, outline_color, (center_x + 2, center_y - 4), 2)
    
    elif piece.piece_type == 'bishop':
        pygame.draw.rect(screen, piece_color, (center_x - 8, center_y + 5, 16, 8))
        pygame.draw.rect(screen, outline_color, (center_x - 8, center_y + 5, 16, 8), 2)
        pygame.draw.ellipse(screen, piece_color, (center_x - 10, center_y - 10, 20, 20))
        pygame.draw.ellipse(screen, outline_color, (center_x - 10, center_y - 10, 20, 20), 2)
        pygame.draw.circle(screen, piece_color, (center_x, center_y - 12), 4)
        pygame.draw.circle(screen, outline_color, (center_x, center_y - 12), 4, 2)
        pygame.draw.line(screen, outline_color, (center_x - 2, center_y - 12), (center_x + 2, center_y - 12), 2)
    
    elif piece.piece_type == 'queen':
        pygame.draw.rect(screen, piece_color, (center_x - 10, center_y + 5, 20, 8))
        pygame.draw.rect(screen, outline_color, (center_x - 10, center_y + 5, 20, 8), 2)
        pygame.draw.ellipse(screen, piece_color, (center_x - 12, center_y - 5, 24, 15))
        pygame.draw.ellipse(screen, outline_color, (center_x - 12, center_y - 5, 24, 15), 2)
        crown_points = [(center_x - 10, center_y - 8), (center_x - 5, center_y - 15),
                       (center_x, center_y - 18), (center_x + 5, center_y - 15),
                       (center_x + 10, center_y - 8)]
        for i, point in enumerate(crown_points):
            height = 8 if i % 2 == 0 else 12
            pygame.draw.rect(screen, piece_color, (point[0] - 2, point[1], 4, height))
    
    elif piece.piece_type == 'king':
        pygame.draw.rect(screen, piece_color, (center_x - 12, center_y + 5, 24, 8))
        pygame.draw.rect(screen, outline_color, (center_x - 12, center_y + 5, 24, 8), 2)
        pygame.draw.ellipse(screen, piece_color, (center_x - 14, center_y - 5, 28, 15))
        pygame.draw.ellipse(screen, outline_color, (center_x - 14, center_y - 5, 28, 15), 2)
        pygame.draw.line(screen, outline_color, (center_x - 6, center_y - 15), (center_x + 6, center_y - 15), 3)
        pygame.draw.line(screen, outline_color, (center_x, center_y - 20), (center_x, center_y - 10), 3)

def draw_board(board):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            if board.selected_pos and board.selected_pos == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
            
            piece = board.board[row][col]
            if piece:
                draw_piece(piece, col * SQUARE_SIZE, row * SQUARE_SIZE)

def draw_ui(game_mode, board, paused, ai_thinking):
    # UI Background
    pygame.draw.rect(screen, LIGHT_GRAY, (BOARD_SIZE, 0, UI_WIDTH, HEIGHT))
    pygame.draw.line(screen, BLACK, (BOARD_SIZE, 0), (BOARD_SIZE, HEIGHT), 2)
    
    # Title
    font = pygame.font.Font(None, 36)
    title = font.render("CHESS GAME", True, BLACK)
    screen.blit(title, (BOARD_SIZE + 20, 20))
    
    # Game Mode
    mode_font = pygame.font.Font(None, 24)
    mode_text = "vs AI" if game_mode == "ai" else "vs Friend"
    mode_surface = mode_font.render(f"Mode: {mode_text}", True, BLACK)
    screen.blit(mode_surface, (BOARD_SIZE + 20, 60))
    
    # Score
    if game_mode == "ai":
        score = board.evaluate_position()
        score_text = mode_font.render(f"Score: {score:.1f}", True, BLACK)
        screen.blit(score_text, (BOARD_SIZE + 20, 90))
        
        if score > 2:
            leader_text = mode_font.render("Black Leading", True, BLACK)
        elif score < -2:
            leader_text = mode_font.render("White Leading", True, BLACK)
        else:
            leader_text = mode_font.render("Even Game", True, BLACK)
        screen.blit(leader_text, (BOARD_SIZE + 20, 115))
    
    # Current Player
    player_text = f"Turn: {board.current_player.capitalize()}"
    if ai_thinking:
        player_text = "AI Thinking..."
    elif paused:
        player_text = "PAUSED"
    
    player_surface = mode_font.render(player_text, True, BLACK)
    screen.blit(player_surface, (BOARD_SIZE + 20, 150))
    
    # Game Status
    game_status = board.get_game_status()
    if game_status == 'check':
        status_surface = mode_font.render("CHECK!", True, RED)
        screen.blit(status_surface, (BOARD_SIZE + 20, 175))
    elif game_status in ['checkmate', 'game_over']:
        if game_status == 'checkmate':
            winner = 'Black' if board.current_player == 'white' else 'White'
            status_surface = mode_font.render(f"{winner} Wins!", True, RED)
        else:
            status_surface = mode_font.render("Game Over!", True, RED)
        screen.blit(status_surface, (BOARD_SIZE + 20, 175))

def draw_menu_chessboard():
    # Draw a decorative chessboard background
    board_x = 50
    board_y = 50
    square_size = 60
    
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            x = board_x + col * square_size
            y = board_y + row * square_size
            pygame.draw.rect(screen, color, (x, y, square_size, square_size))
    
    # Add some decorative pieces
    pieces_pos = [(0, 0, 'black', 'rook'), (0, 7, 'black', 'rook'), 
                  (7, 0, 'white', 'rook'), (7, 7, 'white', 'rook'),
                  (0, 4, 'black', 'king'), (7, 4, 'white', 'king')]
    
    for row, col, color, piece_type in pieces_pos:
        x = board_x + col * square_size + square_size // 2
        y = board_y + row * square_size + square_size // 2
        piece_color = WHITE if color == 'white' else BLACK
        outline_color = BLACK if color == 'white' else WHITE
        
        if piece_type == 'rook':
            pygame.draw.rect(screen, piece_color, (x - 15, y - 10, 30, 20))
            pygame.draw.rect(screen, outline_color, (x - 15, y - 10, 30, 20), 2)
        elif piece_type == 'king':
            pygame.draw.circle(screen, piece_color, (x, y), 18)
            pygame.draw.circle(screen, outline_color, (x, y), 18, 2)
            pygame.draw.line(screen, outline_color, (x - 6, y - 20), (x + 6, y - 20), 2)
            pygame.draw.line(screen, outline_color, (x, y - 25), (x, y - 15), 2)

def draw_main_menu():
    screen.fill(WHITE)
    
    # Draw decorative chessboard
    draw_menu_chessboard()
    
    # Semi-transparent overlay for better text readability
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(WHITE)
    screen.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.Font(None, 72)
    title = title_font.render("CHESS GAME", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 180))
    screen.blit(title, title_rect)
    
    # Custom message
    message_font = pygame.font.Font(None, 32)
    message1 = message_font.render("Falit's First Game,", True, (50, 50, 150))
    message2 = message_font.render("Support Guys.", True, (50, 50, 150))
    
    message1_rect = message1.get_rect(center=(WIDTH//2, HEIGHT//2 - 130))
    message2_rect = message2.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
    
    screen.blit(message1, message1_rect)
    screen.blit(message2, message2_rect)
    
    # Buttons
    ai_button = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50, "Play vs AI", GREEN)
    friend_button = Button(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50, "Play vs Friend", GREEN)
    quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 110, 200, 50, "Quit", RED)
    
    ai_button.draw(screen)
    friend_button.draw(screen)
    quit_button.draw(screen)
    
    return ai_button, friend_button, quit_button

def get_square_from_mouse(pos):
    x, y = pos
    if x >= BOARD_SIZE:
        return None, None
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    clock = pygame.time.Clock()
    state = "menu"  # menu, game
    game_mode = None  # ai, friend
    board = ChessBoard()
    ai_thinking = False
    paused = False
    
    # UI Buttons
    new_game_btn = Button(BOARD_SIZE + 20, 220, 120, 40, "New Game")
    pause_btn = Button(BOARD_SIZE + 150, 220, 120, 40, "Pause")
    resign_btn = Button(BOARD_SIZE + 20, 270, 120, 40, "Resign", RED)
    menu_btn = Button(BOARD_SIZE + 150, 270, 120, 40, "Main Menu")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                if state == "menu":
                    ai_btn, friend_btn, quit_btn = draw_main_menu()
                    
                    if ai_btn.is_clicked(pos):
                        state = "game"
                        game_mode = "ai"
                        board.reset()
                    elif friend_btn.is_clicked(pos):
                        state = "game"
                        game_mode = "friend"
                        board.reset()
                    elif quit_btn.is_clicked(pos):
                        pygame.quit()
                        sys.exit()
                
                elif state == "game":
                    game_status = board.get_game_status()
                    
                    # UI Button clicks
                    if new_game_btn.is_clicked(pos):
                        board.reset()
                        paused = False
                    elif pause_btn.is_clicked(pos):
                        paused = not paused
                    elif resign_btn.is_clicked(pos):
                        # Switch winner
                        board.current_player = 'white' if board.current_player == 'black' else 'black'
                        # Force game over by removing king
                        for row in range(8):
                            for col in range(8):
                                piece = board.board[row][col]
                                if piece and piece.piece_type == 'king' and piece.color == board.current_player:
                                    board.board[row][col] = None
                                    break
                    elif menu_btn.is_clicked(pos):
                        state = "menu"
                        paused = False
                    
                    # Board clicks
                    elif not paused and game_status not in ['checkmate', 'game_over']:
                        row, col = get_square_from_mouse(pos)
                        if row is not None and col is not None:
                            # Player move logic
                            if game_mode == "friend" or (game_mode == "ai" and board.current_player == 'white'):
                                if not ai_thinking:
                                    if board.selected_piece is None:
                                        piece = board.board[row][col]
                                        if piece and piece.color == board.current_player:
                                            board.selected_piece = piece
                                            board.selected_pos = (row, col)
                                    else:
                                        start_row, start_col = board.selected_pos
                                        if board.make_move(start_row, start_col, row, col):
                                            board.selected_piece = None
                                            board.selected_pos = None
                                        else:
                                            piece = board.board[row][col]
                                            if piece and piece.color == board.current_player:
                                                board.selected_piece = piece
                                                board.selected_pos = (row, col)
                                            else:
                                                board.selected_piece = None
                                                board.selected_pos = None
        
        # AI Move
        if (state == "game" and game_mode == "ai" and board.current_player == 'black' 
            and not ai_thinking and not paused and board.get_game_status() not in ['checkmate', 'game_over']):
            ai_thinking = True
            board.ai_move()
            ai_thinking = False
        
        # Drawing
        if state == "menu":
            draw_main_menu()
        elif state == "game":
            screen.fill(WHITE)
            draw_board(board)
            draw_ui(game_mode, board, paused, ai_thinking)
            
            # Draw buttons
            new_game_btn.draw(screen)
            pause_btn.color = RED if paused else LIGHT_GRAY
            pause_btn.text = "Resume" if paused else "Pause"
            pause_btn.draw(screen)
            resign_btn.draw(screen)
            menu_btn.draw(screen)
            
            # Game over overlay
            game_status = board.get_game_status()
            if game_status in ['checkmate', 'game_over']:
                overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                big_font = pygame.font.Font(None, 72)
                if game_status == 'checkmate':
                    winner = 'BLACK' if board.current_player == 'white' else 'WHITE'
                    winner_text = big_font.render(f"{winner} WINS!", True, (255, 255, 0))
                    checkmate_text = big_font.render("CHECKMATE!", True, (255, 0, 0))
                    
                    winner_rect = winner_text.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2 - 40))
                    checkmate_rect = checkmate_text.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2 + 40))
                    
                    screen.blit(checkmate_text, checkmate_rect)
                    screen.blit(winner_text, winner_rect)
                else:
                    game_over_text = big_font.render("GAME OVER!", True, (255, 0, 0))
                    game_over_rect = game_over_text.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2))
                    screen.blit(game_over_text, game_over_rect)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()