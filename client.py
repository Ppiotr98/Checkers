import fcntl, os
import pygame
import sys
import logging
import select
from pygame.locals import *
pygame.init()

from threading import Thread, Lock
from time import sleep
import socket
import errno

from tags import *

###

PORT = 1234 #server port
IP = '127.0.0.1' #server ip

FONT = pygame.font.SysFont(None, 40) #font

WIDTH, HEIGHT = 1000, 600 #window dimensions
ROWS, COLS = 8, 8 #rows and columns on board
SQUARE_SIZE = HEIGHT//ROWS #size of a single board square
FPS = 60 #frames per second

WHITE = (255, 255, 255) #white color
BLACK = (0, 0, 0) #black color
WINDOW_BG = (55, 30, 25) #window background
OUTLINE_WHITE = (210, 210, 210) #white piece outline
OUTLINE_BLACK = (30, 30, 30) #black piece outline
BG1 = (90, 50, 40) #additional background #1
BG2 = (130, 80, 60) #additional background #2
BLUE = (120, 150, 200) #blue color #1
BLUE2 = (60, 75, 100) #blue color #2

CROWN = pygame.transform.scale(pygame.image.load("crown.png"), (36, 27)) #crown icon for queen

EMPTY = 0 #empty messege tag - no data available from teh server after server.read()

WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #display window
pygame.display.set_caption("Sooper Kool Checkers") #window caption

clock = pygame.time.Clock() #clock
click = False #checks if mouse button was clicked
nick = "Player" #player nick

###

def is_int(s): #checks if s is integer
    try: 
        int(s)
        return True
    except ValueError:
        return False

###

class Messege: #messeges from and to server; tag determines what type of messege was sent/received and data is additional information
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data

###

class Server: #server class. it contains client's socket and handles sending and receiving data to/from the server, as well as connecting
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.readable = []
        self.writable = []
        self.errors = []

    def connect_to_server(self, ip, port):
        self.sock.connect((ip, port))
        #fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
        self.sock.setblocking(False)

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def read(self):
        self.readable, self.writable, self.errors = select.select([self.sock], [self.sock], [self.sock], 0.5)

        if not self.readable:
            #print(EMPTY)
            messege = Messege(EMPTY, [])
            return messege 

        #print("COS!")
        
        messege = self.sock.recv(64)
        messege = messege.decode("utf-8")

        messege = messege.split(';')

        if len(messege) == 1:
            return Messege(int(messege[0]), [])

        messege = Messege(int(messege[0]), messege[1:])
        for i in range(len(messege.data)):
            if is_int(messege.data[i]):
                messege.data[i] = int(messege.data[i])

        return messege

    def write(self, tag, data):
        messege = str(tag)
        for d in data:
            messege = messege + ';' + str(d)
        self.sock.send(bytes(messege, "utf-8"))

server = Server() #global Server class object

###

class Game(): #this class handles the game. What square/piece was selected, what board is supposed to do and so on...
    def __init__(self, win, my_color):
        self._init()
        self.win = win
        self.my_color = my_color
        
    def _init(self):
        self.selected = None #currenly selected piece
        self.board = Board() #board
        self.turn = BLACK #whose turn is now
        self.valid_moves = {} #list of valid moves for selected piece
        self.selected_piece = None #additional selected
        self.prev_moved = None #previously moved piece
        self.prev_turn = WHITE #whose was the previous turn
        self.jump_again = False #False if current player's turn is done, True if there are more jumping moves to be made by that player
        self.additional_moves = {} #potential moves that could be made by already moved piece
        self.move_made = False
        
    def update(self):
        self.board.draw(self.win)
        self.board.draw_valid_moves(self.win, self.valid_moves)
        pygame.display.update()
        
    def reset(self):
        self._init()

    def select(self, row, col): #called when played clicked the board. If player has nothing selected and clicks an empty square or square with rival's piece - nothing happens. If playes has nothing selected and clicks his own piece it illuminates it and show possible moves, also this piece becomes selected. If player has a piece selected and clicks on nothing, the state is reset. If player has a piece selected and clicks a square where player can move it moves the piece there using _move method. Actually _move is always called when a piece is selected, it checks if the click encodes a possible move and if yes - it makes that move.

        self.move_made = False

        if self.jump_again == True: #if jump_again is True it means that player has to do some additional jumps, player cannot 'unselect' piece in that state. the 'if' block checks if player clicked a square with possible move and if not - it returns False.
            if (row, col) not in self.additional_moves:
                return False
    
        if self.selected: 
            rowp = self.selected_piece.row
            colp = self.selected_piece.col
            spiece = self.board.get_piece(rowp, colp)
            spiece.selected = False
            
            result = self._move(row, col)
            if not result:
                #print("if not result")
                self.selected = None
                self.valid_moves = {}
                #self.select(row, col) #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!??????
        
        piece = self.selected_piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            #print("if piece != 0 and piece.color == self.turn:")
            #if self.prev_turn == self.turn:
                
            
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            piece.selected = True
            return True
            
        return False

    def rival_move(self, row_from, col_from, row_to, col_to):
        self.move_made = False
        self.select(row_from, col_from)
        self.select(row_to, col_to)
        if not self.move_made:
            return False
        return True
    
    def _move(self, row, col):
        move_to = self.board.get_piece(row, col)
        if self.selected and move_to == 0 and (row, col) in self.valid_moves:
            row_moved_from = self.selected.row
            col_moved_from = self.selected.col
            self.board.move(self.selected, row, col)
            self.move_made = True           
            self.prev_moved = self.selected
            self.prev_turn = self.prev_moved.color
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            #self.change_turn()
            
            self.additional_moves = {}
            self.additional_moves = self.board.get_valid_moves(self.selected)
            self.jump_again = False
            
            for move in self.additional_moves:
                if abs(move[0] - self.selected.row) == 2 and skipped:
                    self.jump_again = True
                    break
            
            if self.jump_again == False:
                self.additional_moves = {}
                self.change_turn()

            #SEND MOVE TO SERVER: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            global server
            if self.turn == self.my_color:
                server.write(TAG_PAWN_MOVED, [row_moved_from, col_moved_from, row, col, not self.jump_again])
            
        else:
            return False
            
        return True
        
    def change_turn(self):
        self.valid_moves = {}
        if self.turn == WHITE:
            self.turn = BLACK
        else:
            self.turn = WHITE

###

class Piece:
    PADDING = 16
    OUTLINE = 4

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.queen = False
        self.selected = False
        
        #if self.color == WHITE:
            #self.direction = -1
        #else:
            #self.direction = 1
            
        self.x = 0
        self.y = 0
        self.calculate_position()
        
    def calculate_position(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2
        
    def make_queen(self):
        self.queen = True
        
    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        if self.selected:
            pygame.draw.rect(win, BLUE, (self.col * SQUARE_SIZE, self.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        if self.color == WHITE:
            pygame.draw.circle(win, OUTLINE_WHITE, (self.x, self.y), radius + self.OUTLINE)
        else:
            pygame.draw.circle(win, OUTLINE_BLACK, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        
        if self.queen:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calculate_position()

    def __repr__(self):
        return str(self.color)

###

class Board:
    def __init__(self):
        self.board = []
        #self.selected_piece = None
        self.white_left = self.black_left = 12
        self.white_queens = self.black_queens = 0
        self.create_board()
        
    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == BLACK:
                    self.black_left -= 1
                if piece.color == WHITE:
                    self.white_left -= 1
                    
    def winner(self):
        if self.black_left <= 0:
            return WHITE
        if self.white_left <= 0:
            return BLACK
            
        return None
        
    def draw_valid_moves(self, win, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 10)
        
    def get_valid_moves(self, piece):
        moves = {}
        moves = self._get_all_moves(piece)
        
        must_jump = False
        for r in self.board:
            if must_jump == True:
                break
            for p in r:
                if p != 0:
                    if p.color == piece.color:
                        p_moves = self._get_all_moves(p)
                        for move in p_moves:
                            if abs(move[0] - p.row) == 2:
                                must_jump = True
                                break
        
        if must_jump == True:
            for move in list(moves):
                move_row = move[0]
                if abs(piece.row - move_row) == 1:
                    moves.pop(move)
        
        #print(moves)
        return moves
        
    def _get_all_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row
        #col = piece.col

        #if piece.color == BLACK or piece.queen:
        moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
        moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        #if piece.color == WHITE or piece.queen:
        moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
        moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
    
        if piece.color == BLACK and piece.queen == False:
            for move in list(moves):
                move_row = move[0]
                if row - move_row == -1:
                    moves.pop(move)
            
        if piece.color == WHITE and piece.queen == False:
            for move in list(moves):
                move_row = move[0]
                if row - move_row == 1:
                    moves.pop(move)
                    
        return moves
            
    def _traverse_left(self, start, stop, step, color, left, skipped = []):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    #moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped = last))
                    #moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped = last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        
        return moves
            
    def _traverse_right(self, start, stop, step, color, right, skipped = []):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    #moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped = last))
                    #moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped = last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves
        
    def draw_squares(self, win):
        mx, my = pygame.mouse.get_pos()
        m_col, m_row = get_row_col_from_mouse(mx, my)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                square_bg = BG1
                if row == m_row and col == m_col:
                    square_bg = BLUE2
                pygame.draw.rect(win, square_bg, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            for col in range((row % 2) - 1, ROWS, 2):
                square_bg = BG2
                if row == m_row and col == m_col:
                    square_bg = BLUE2
                pygame.draw.rect(win, square_bg, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, BLACK))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
                    
    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)
                    #print(row, col, piece.x, piece.y, piece.row, piece.col)
                
    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        
        if (row == ROWS - 1 and piece.color == WHITE) or (row == 0 and piece.color == BLACK):
            piece.make_queen()
            if piece.color == WHITE:
                self.white_queens += 1
            else:
                self.black_queens += 1
            
    def get_piece(self, row, col):
        return self.board[row][col]
   
###

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    
###

def get_row_col_from_mouse(x, y): #takes mouse position and returns row and column within that position
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

###

def gameplay(rival, color): #contains main game loop
    global WIN
    global click
    global server

    game = Game(WIN, color)
    
    run = True

    show_accept_draw = False

    while run:
        clock.tick(FPS)
        WIN.fill(WINDOW_BG)
        
        if game.board.winner() != None:
            if game.board.winner() == game.my_color:
                won()
                return
            else:
                lost()
                return
        
        draw_text('Playing with: ' + rival, FONT, WHITE, WIN, 620, 20)
                
        mx, my = pygame.mouse.get_pos()
        
        button_offer_draw = pygame.Rect(650, 100, 300, 50)
        button_surrender = pygame.Rect(650, 200, 300, 50)
        button_accept_draw = pygame.Rect(650, 300, 300, 50)
        
        button_offer_draw_bg = BG1
        button_surrender_bg = BG1
        button_accept_draw_bg = BG1
        
        if button_offer_draw.collidepoint((mx, my)):
            button_offer_draw_bg = BG2
            if click:
                offer_draw()
        if button_surrender.collidepoint((mx, my)):
            button_surrender_bg = BG2
            if click:
                surrender()
                return
        if button_accept_draw.collidepoint((mx, my)) and show_accept_draw:
            button_accept_draw_bg = BG2
            if click:
                accept_draw()
                return
                
        pygame.draw.rect(WIN, button_offer_draw_bg, button_offer_draw)
        pygame.draw.rect(WIN, button_surrender_bg, button_surrender)
        if show_accept_draw:
            pygame.draw.rect(WIN, button_accept_draw_bg, button_accept_draw)
        
        draw_text('OFFER DRAW', FONT, WHITE, WIN, 655, 105)
        draw_text('SURRENDER', FONT, WHITE, WIN, 655, 205)
        if show_accept_draw:
            draw_text('ACCEPT DRAW', FONT, WHITE, WIN, 655, 305)
        
        if game.turn == BLACK and game.my_color == BLACK:
            draw_text('TURN: BLACK (YOU)', FONT, BLACK, WIN, 620, 555)
        if game.turn == BLACK and game.my_color != BLACK:
            draw_text('TURN: BLACK (RIVAL)', FONT, BLACK, WIN, 620, 555)
        if game.turn == WHITE and game.my_color == WHITE:
            draw_text('TURN: WHITE (YOU)', FONT, WHITE, WIN, 620, 555)
        if game.turn == WHITE and game.my_color != WHITE:
            draw_text('TURN: WHITE (RIVAL)', FONT, WHITE, WIN, 620, 555)

        rival_move = []
        rival_done = False

        messege = server.read()
        if messege.tag == TAG_PAWN_MOVED:
            rival_move.append(messege.data[0])
            rival_move.append(messege.data[1])
            rival_move.append(messege.data[2])
            rival_move.append(messege.data[3])
            rival_done = messege.data[4]
        elif messege.tag == TAG_SURRENDER:
            won()
            return
        elif messege.tag == TAG_OFFER_DRAW:
            show_accept_draw = True
        elif messege.tag == TAG_DRAW_ACCEPTED:
            accept_draw()
            return
        elif messege.tag == TAG_GAME_WON:
            won()
        elif messege.tag == TAG_GAME_LOST:
            lost()
        elif messege.tag == TAG_GAME_DRAWN:
            drawn()
        elif messege.tag != EMPTY:
            print("ERROR_gameplay(): ", messege.tag)
            error()
            return
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                surrender()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    run = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                if mx <= 600 and my <= 600:
                    row, col = get_row_col_from_mouse(mx, my)
                    if game.turn == game.my_color:
                        game.select(row, col)
        
        if rival_move and game.turn != game.my_color:
            if not game.rival_move(rival_move[0], rival_move[1], rival_move[2], rival_move[3]):
                error()
                return

        game.update()

###

def won():
    global server
    server.write(TAG_GAME_WON, [])
    server.disconnect()
    print("WON")

def lost():
    global server
    server.write(TAG_GAME_LOST, [])
    server.disconnect()
    print("LOST")

def drawn():
    global server
    server.write(TAG_GAME_DRAWN, [])
    server.disconnect()
    print("DRAWN")

def error():
    global server
    server.disconnect()
    print("ERROR OCCURED")

###

def offer_draw():
    global server
    server.write(TAG_OFFER_DRAW, [])

###

def surrender():
    global server
    server.write(TAG_SURRENDER, [])
    lost()

###

def accept_draw():
    global server
    server.write(TAG_ACCEPT_DRAW, [])
    drawn()

###

def host_game():
    global WIN
    global server

    server.connect_to_server(IP, PORT)

    server.write(TAG_HOST_GAME, [nick])

    while True:
        WIN.fill(WINDOW_BG)
        draw_text('...', FONT, WHITE, WIN, 20, 20)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                server.disconnect()
                pygame.quit()
                sys.exit()
        messege = server.read()
        if messege.tag == EMPTY:
            continue
        if messege.tag == TAG_GAME_HOSTED:
            ip = messege.data[0]
            break
        else:
            print("ERROR_00")
            server.disconnect()
            return

    rival = None
    color = None
    
    while True:
        WIN.fill(WINDOW_BG)
        draw_text('YOUR IP IS: ' + str(ip) + '. WAITING FOR THE OPPONENT...', FONT, WHITE, WIN, 20, 20)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                server.disconnect()
                pygame.quit()
                sys.exit()
        messege = server.read()
        if messege.tag == EMPTY:
            continue
        if messege.tag == TAG_GAME_STARTED:
            rival = messege.data[0]
            color = messege.data[1]
            if color == 0:
                color = WHITE
            else:
                color = BLACK
            break
        else:
            print("ERROR_host_game()")
            server.disconnect()
            return

    wait = True
    wait_time = 1000
    
    start = pygame.time.get_ticks()
    
    while wait:
        WIN.fill(WINDOW_BG)
        draw_text('STARTING THE GAME...', FONT, WHITE, WIN, 20, 20)
            
        now = pygame.time.get_ticks()
        if now - start >= wait_time:
            gameplay(rival, color)
            wait = False     

        pygame.display.update()
        clock.tick(FPS)
        
###

def join_game():
    global WIN
    global server

    server.connect_to_server(IP, PORT)

    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 16, 140, 40)
    color_inactive = pygame.Color(BG2)
    color_active = pygame.Color(BLUE)
    ip_correct = False
    
    while not ip_correct:
        active = False
        text = ''
        done = False
        color = color_inactive
        ip = 0

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    server.disconnect()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box rect.
                    if input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                    # Change the current color of the input box.
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        server.disconnect()
                        return
                    if active:
                        if event.key == pygame.K_RETURN:
                            if not is_int(ip):
                                return
                            ip = int(text)
                            text = ''
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
                            
            WIN.fill(WINDOW_BG)
            draw_text('TYPE THE IP: ', FONT, WHITE, WIN, WIDTH // 2 - 100, HEIGHT // 2 - 50)
            # Render the current text.
            txt_surface = FONT.render(text, True, color)
            # Resize the box if the text is too long.
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            # Blit the text.
            WIN.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            # Blit the input_box rect.
            pygame.draw.rect(WIN, color, input_box, 2)

            pygame.display.update()
            clock.tick(FPS)

        server.write(TAG_JOIN_GAME, [ip, nick])      

        ip_correct = True
        rival = None
        color = None
        while True:
            WIN.fill(WINDOW_BG)
            draw_text('...', FONT, WHITE, WIN, 20, 20)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    server.disconnect()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        server.disconnect()
                        return
            messege = server.read()
            if messege.tag == EMPTY:
                continue
            if messege.tag == TAG_WRONG_IP:
                ip_correct = False
                break
            if messege.tag == TAG_GAME_STARTED:
                rival = messege.data[0]
                color = messege.data[1]
                if color == 0:
                    color = WHITE
                else:
                    color = BLACK
                break
            else:
                print("ERROR_join_game()")
                server.disconnect()
                return
        
        #print(rival, color, BLACK)

        wait = True
        wait_time = 1000
        
        start = pygame.time.get_ticks()
        
        if ip_correct:
            while wait:
                WIN.fill(WINDOW_BG)
                draw_text('STARTING THE GAME...', FONT, WHITE, WIN, 20, 20)
                
                now = pygame.time.get_ticks()
                if now - start >= wait_time:
                    gameplay(rival, color)
                    wait = False     

                pygame.display.update()
                clock.tick(FPS)
        else:
            while wait:
                WIN.fill(WINDOW_BG)
                draw_text('WRONG IP!', FONT, WHITE, WIN, 20, 20)
                
                now = pygame.time.get_ticks()
                if now - start >= wait_time:
                    wait = False     

                pygame.display.update()
                clock.tick(FPS)
        
###

def join_random_game():
    global WIN
    global server

    server.connect_to_server(IP, PORT)

    server.write(TAG_JOIN_GAME, [nick])

    rival = None
    color = None
    
    while True:
        WIN.fill(WINDOW_BG)
        draw_text('WAITING FOR THE OPPONENT...', FONT, WHITE, WIN, 20, 20)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                server.disconnect()
                pygame.quit()
                sys.exit()
        messege = server.read()
        if messege.tag == EMPTY:
            continue
        if messege.tag == TAG_GAME_STARTED:
            rival = messege.data[0]
            color = messege.data[1]
            if color == 0:
                color = WHITE
            else:
                color = BLACK
            break
        else:
            print("ERROR_join_random_game()")
            server.disconnect()
            return

    wait = True
    wait_time = 1000
    
    start = pygame.time.get_ticks()
    
    while wait:
        WIN.fill(WINDOW_BG)
        draw_text('STARTING THE GAME...', FONT, WHITE, WIN, 20, 20)
            
        now = pygame.time.get_ticks()
        if now - start >= wait_time:
            gameplay(rival, color)
            wait = False     

        pygame.display.update()
        clock.tick(FPS)
    
###

def change_nick():
    global WIN
    global nick
    
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 16, 140, 40)
    color_inactive = pygame.Color(BG2)
    color_active = pygame.Color(BLUE)
    color = color_inactive
    
    active = False
    text = ''
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    continue
                if active:
                    if event.key == pygame.K_RETURN:
                        nick = text
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                        
        WIN.fill(WINDOW_BG)
        draw_text('YOUR CURRENT NICK IS: ' + nick, FONT, WHITE, WIN, 20, 20)
        draw_text('NEW NICK: ', FONT, WHITE, WIN, WIDTH // 2 - 100, HEIGHT // 2 - 50)
        # Render the current text.
        txt_surface = FONT.render(text, True, color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        # Blit the text.
        WIN.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        # Blit the input_box rect.
        pygame.draw.rect(WIN, color, input_box, 2)

        pygame.display.update()
        clock.tick(FPS)
    
###

def quit():
    pygame.quit()
    sys.exit()
    
###

def main_menu():
    global WIN
    global click
    
    while True:
        WIN.fill(WINDOW_BG)
        draw_text('SOOPER KOOL CHECKERS', FONT, WHITE, WIN, 20, 20)
        
        mx, my = pygame.mouse.get_pos()
        
        button_host_game = pygame.Rect(50, 100, 400, 50)
        button_join_game = pygame.Rect(50, 200, 400, 50)
        button_join_random_game = pygame.Rect(50, 300, 400, 50)
        button_change_nick = pygame.Rect(50, 400, 400, 50)
        button_quit = pygame.Rect(50, 500, 400, 50)
        
        button_host_game_bg = BG1
        button_join_game_bg = BG1
        button_join_random_game_bg = BG1
        button_change_nick_bg = BG1
        button_quit_bg = BG1
        
        if button_host_game.collidepoint((mx, my)):
            button_host_game_bg = BG2
            if click:
                host_game()
        if button_join_game.collidepoint((mx, my)):
            button_join_game_bg = BG2
            if click:
                join_game()
        if button_join_random_game.collidepoint((mx, my)):
            button_join_random_game_bg = BG2
            if click:
                join_random_game()
        if button_change_nick.collidepoint((mx, my)):
            button_change_nick_bg = BG2
            if click:
                change_nick()
        if button_quit.collidepoint((mx, my)):
            button_quit_bg = BG2
            if click:
                quit()
                
        pygame.draw.rect(WIN, button_host_game_bg, button_host_game)
        pygame.draw.rect(WIN, button_join_game_bg, button_join_game)
        pygame.draw.rect(WIN, button_join_random_game_bg, button_join_random_game)
        pygame.draw.rect(WIN, button_change_nick_bg, button_change_nick)
        pygame.draw.rect(WIN, button_quit_bg, button_quit)
        
        draw_text('HOST GAME', FONT, WHITE, WIN, 55, 105)
        draw_text('JOIN GAME', FONT, WHITE, WIN, 55, 205)
        draw_text('JOIN RANDOM GAME', FONT, WHITE, WIN, 55, 305)
        draw_text('CHANGE NICK', FONT, WHITE, WIN, 55, 405)
        draw_text('QUIT', FONT, WHITE, WIN, 55, 505)
        
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True   
                    
        pygame.display.update()
        clock.tick(FPS)
    
###
 
def main():
    main_menu()
   
###
   
main()
