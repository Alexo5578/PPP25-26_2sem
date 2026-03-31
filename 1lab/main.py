import tkinter as tk
from copy import deepcopy
import json
import random

TILE_SIZE = 64

class Piece:
    def __init__(self, color):
        self.color = color

    def enemy(self, other):
        return other and other.color != self.color

    def get_moves(self, board, x, y):
        return []

class Pawn(Piece):
    def symbol(self): return "♙" if self.color=="white" else "♟"

    def get_moves(self,b,x,y):
        m=[]; d=-1 if self.color=="white" else 1
        if 0<=x+d<8 and b[x+d][y] is None: m.append((x+d,y))
        for dy in [-1,1]:
            nx,ny=x+d,y+dy
            if 0<=nx<8 and 0<=ny<8 and self.enemy(b[nx][ny]): m.append((nx,ny))
        return m

class Rook(Piece):
    def symbol(self): return "♖" if self.color=="white" else "♜"
    def get_moves(self,b,x,y):
        m=[]
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx,ny=x,y
            while True:
                nx+=dx; ny+=dy
                if not(0<=nx<8 and 0<=ny<8): break
                if b[nx][ny] is None: m.append((nx,ny))
                else:
                    if self.enemy(b[nx][ny]): m.append((nx,ny))
                    break
        return m

class Bishop(Piece):
    def symbol(self): return "♗" if self.color=="white" else "♝"
    def get_moves(self,b,x,y):
        m=[]
        for dx,dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx,ny=x,y
            while True:
                nx+=dx; ny+=dy
                if not(0<=nx<8 and 0<=ny<8): break
                if b[nx][ny] is None: m.append((nx,ny))
                else:
                    if self.enemy(b[nx][ny]): m.append((nx,ny))
                    break
        return m

class Knight(Piece):
    def symbol(self): return "♘" if self.color=="white" else "♞"
    def get_moves(self,b,x,y):
        m=[]
        for dx,dy in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nx,ny=x+dx,y+dy
            if 0<=nx<8 and 0<=ny<8 and (b[nx][ny] is None or self.enemy(b[nx][ny])):
                m.append((nx,ny))
        return m

class Queen(Piece):
    def symbol(self): return "♕" if self.color=="white" else "♛"
    def get_moves(self,b,x,y): return Rook.get_moves(self,b,x,y)+Bishop.get_moves(self,b,x,y)

class King(Piece):
    def symbol(self): return "♔" if self.color=="white" else "♚"

    def get_moves(self,b,x,y):
        m=[]
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx==0 and dy==0: continue
                nx,ny=x+dx,y+dy
                if 0<=nx<8 and 0<=ny<8 and (b[nx][ny] is None or self.enemy(b[nx][ny])):
                    m.append((nx,ny))
        return m

class Game:
    def __init__(self):
        self.board=[[None]*8 for _ in range(8)]
        self.turn="white"
        self.history=[]
        self.selected=None
        self.moves=[]
        self.setup()

    def setup(self):
        for i in range(8):
            self.board[6][i]=Pawn("white")
            self.board[1][i]=Pawn("black")

        self.board[7][0]=self.board[7][7]=Rook("white")
        self.board[0][0]=self.board[0][7]=Rook("black")

        self.board[7][1]=self.board[7][6]=Knight("white")
        self.board[0][1]=self.board[0][6]=Knight("black")

        self.board[7][2]=self.board[7][5]=Bishop("white")
        self.board[0][2]=self.board[0][5]=Bishop("black")

        self.board[7][3]=Queen("white")
        self.board[0][3]=Queen("black")

        self.board[7][4]=King("white")
        self.board[0][4]=King("black")

    def ai_move(self):
        moves=[]
        for i in range(8):
            for j in range(8):
                p=self.board[i][j]
                if p and p.color==self.turn:
                    for m in self.valid_moves(i,j):
                        moves.append((i,j,m[0],m[1]))
        if moves:
            move=random.choice(moves)
            self.move(*move)

    def save(self):
        data=[[p.symbol() if p else None for p in row] for row in self.board]
        with open("save.json","w") as f:
            json.dump(data,f)

    def load(self):
        with open("save.json") as f:
            data=json.load(f)
        symbol_map={"♙":Pawn,"♟":Pawn,"♖":Rook,"♜":Rook,
                    "♘":Knight,"♞":Knight,"♗":Bishop,"♝":Bishop,
                    "♕":Queen,"♛":Queen,"♔":King,"♚":King}
        self.board=[[None]*8 for _ in range(8)]
        for i in range(8):
            for j in range(8):
                s=data[i][j]
                if s:
                    color="white" if s.isupper() else "black"
                    self.board[i][j]=symbol_map[s](color)

    def find_king(self,color):
        for i in range(8):
            for j in range(8):
                if isinstance(self.board[i][j],King) and self.board[i][j].color==color:
                    return i,j

    def is_check(self,color):
        kx,ky=self.find_king(color)
        for i in range(8):
            for j in range(8):
                p=self.board[i][j]
                if p and p.color!=color:
                    if (kx,ky) in p.get_moves(self.board,i,j): return True
        return False

    def valid_moves(self,x,y):
        p=self.board[x][y]
        if not p: return []
        valid=[]
        for m in p.get_moves(self.board,x,y):
            temp=deepcopy(self.board)
            temp[m[0]][m[1]]=temp[x][y]
            temp[x][y]=None
            g=Game(); g.board=temp
            if not g.is_check(p.color): valid.append(m)
        return valid

    def is_checkmate(self,color):
        if not self.is_check(color): return False
        for i in range(8):
            for j in range(8):
                p=self.board[i][j]
                if p and p.color==color and self.valid_moves(i,j): return False
        return True

    def move(self,x1,y1,x2,y2):
        p=self.board[x1][y1]
        if p and (x2,y2) in self.valid_moves(x1,y1):
            self.history.append(deepcopy(self.board))
            self.board[x2][y2]=p
            self.board[x1][y1]=None
            if isinstance(p,Pawn) and (x2==0 or x2==7):
                self.board[x2][y2]=Queen(p.color)
            self.turn="black" if self.turn=="white" else "white"
            return True
        return False

    def undo(self):
        if self.history: self.board=self.history.pop()

class GUI:
    def __init__(self,root):
        self.root=root
        self.game=Game()

        self.canvas=tk.Canvas(root,width=512,height=512)
        self.canvas.pack()
        self.canvas.bind("<Button-1>",self.click)

        tk.Button(root,text="Отменить",command=self.undo).pack()
        tk.Button(root,text="Сохранить",command=self.save).pack()
        tk.Button(root,text="Загрузить",command=self.load).pack()
        tk.Button(root,text="Ход ИИ",command=self.ai).pack()

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for i in range(8):
            for j in range(8):
                c="#EEEED2" if (i+j)%2==0 else "#769656"
                self.canvas.create_rectangle(j*64,i*64,j*64+64,i*64+64,fill=c)

                if (i,j) in self.game.moves:
                    self.canvas.create_oval(j*64+20,i*64+20,j*64+44,i*64+44,fill="yellow")

                p=self.game.board[i][j]
                if p:
                    self.canvas.create_text(j*64+32,i*64+32,text=p.symbol(),font=("Arial",32))

    def click(self,event):
        x,y=event.y//64,event.x//64

        if self.game.selected:
            x1,y1=self.game.selected
            self.game.move(x1,y1,x,y)
            self.game.selected=None; self.game.moves=[]
        else:
            p=self.game.board[x][y]
            if p and p.color==self.game.turn:
                self.game.selected=(x,y)
                self.game.moves=self.game.valid_moves(x,y)
        self.draw()

    def undo(self): self.game.undo(); self.draw()
    def save(self): self.game.save()
    def load(self): self.game.load(); self.draw()
    def ai(self): self.game.ai_move(); self.draw()

root=tk.Tk()
root.title("FULL CHESS PROJECT")
GUI(root)
root.mainloop()
