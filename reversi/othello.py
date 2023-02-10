#!/usr/bin/env python3
"""
Othello, also known as Reversi, is a game between two players, denoted by black
and white.

Play happens on an 8x8 grid. Game pieces are discs with a black side and a
white side. The face-up side of a piece indicates its current owner.

The game begins with two black pieces and two white pieces, as shown:

  a b c d e f g h 
1                
2                
3                
4       W B       
5       B W       
6                
7                
8                

Players alternate turns, beginning with black.

A player's turn consists of placing a new piece of their color on an empty space
and then flipping the opponent's pieces.

A player flips lines of one or more opposing pieces when they are bookended
(surrounded) by the newly placed piece and one of their existing pieces. The line
including the bookends must be contiguous (no gaps). Lines of flipped pieces
can be othogonal or diagonal. Multiple lines may be flipped in a single turn.
(Note: One of the two surrounding pieces MUST be the newly placed piece.)

For example, in the following game, black plays g6. This move flips the white
pieces at c6, d6, e6, f5, and f6 to black.

  a b c d e f g h       a b c d e f g h       a b c d e f g h
1                     1                     1                
2                     2                     2                
3       W B W         3       W B W         3       W B W    
4     W B B W B       4     W B B W B       4     W B B W B  
5   W B W B W         5   W B W B *         5   W B W B B    
6   B W W W W         6   B * * * * B       6   B B B B B B  
7                     7                     7                
8                     8                     8                

Every move must flip at least one piece. If a player cannot move, their turn is
skipped.

For example, in the following game, white has no legal move:

  a b c d e f g h
1       W W W   W
2     W W W W   W
3   W W W B W W W
4     W B B W B W
5 W W W W W W B W
6   W W W W W W W
7     W W W W W W
8 B B B B B B B W

When neither player can move, the game ends.

At the end of the game, the player with the most pieces wins. If players have
the same number of pieces, the game is a tie.

Write a program that two people can use to play a game of Othello.

A fully working program should:
  * validate attempted moves
  * execute moves
  * skip turns
  * end the game
  * display the winner

If you have extra time, create a simple AI to play the game.

Pace your development such that the program works as much as possible by the
end of the alloted time; i.e. it should not be in a "broken" state.

The beginnings of a program are provided. Feel free to modify the program as desired.
"""

import enum
import io
import re
import sys
import typing


class Color(enum.Enum):
    BLACK = "B"
    WHITE = "W"


class Coordinate:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return (
            isinstance(other, Coordinate)
            and self.row == other.row
            and self.col == other.col
        )

    def __hash__(self):
        return hash((self.row, self.col))

    def __str__(self):
        return "Coordinate(row={}, col={})".format(self.row, self.col)


Coordinate = typing.Tuple[int, int]
Board = typing.List[typing.List[Color]]
directions = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
SIZE = 8


class CoordinateParseError(Exception):
    pass


def parse_coordinate(str: str) -> Coordinate:
    str = str.lower().strip()
    if len(str) != 2:
        raise CoordinateParseError("Input must be length 2")
    row = ord(str[1]) - ord("1")
    if not (0 <= row < SIZE):
        raise CoordinateParseError("Row out of bounds")
    col = ord(str[0]) - ord("a")
    if not (0 <= col < SIZE):
        raise CoordinateParseError("Col out of bounds")
    return (row, col)


def board_str(board: Board, nexts: list = []) -> str:
    result = f"|   {' '.join(chr(ord('a') + i) for i in range(SIZE))} |\n"
    # for i, row in enumerate(board):
    #     result += f"{i + 1} {' '.join(position.value if position else ' ' for position in row)}\n"

    for i in range(SIZE):
        temp = []
        for j in range(SIZE):
            if board[i][j]:
                temp.append(board[i][j].value)
            elif (i,j) in nexts:
                temp.append('#')
            else:
                temp.append(' ')
        result += f"| {i + 1} {' '.join(temp)} |\n"     
    return result


def is_valid_move(row, col, turn, board):
    # in range already done
    # empty place
    if board[row][col] != None:
        # print ('################ you can only place on empty block! ################')
        return False
    # have element to check
    for direction in directions:
        cnt = 0
        dx, dy = direction
        newx, newy = row + dx, col + dy
        while 0 <= newx < SIZE and 0 <= newy < SIZE:
            if board[newx][newy] == None:
                break
            else:
                if cnt == 0:
                    if board[newx][newy] == turn:
                        break
                    else:
                        newx += dx
                        newy += dy
                        cnt += 1
                else:
                    if board[newx][newy] == turn:
                        return True
                    else:
                        newx += dx
                        newy += dy
                        cnt += 1

    return False

def next_steps(turn, board):
    next_step_candidate = []
    for i in range(SIZE):
        for j in range(SIZE):
            if is_valid_move(i, j, turn, board):
                next_step_candidate.append((i,j))
    return next_step_candidate

def take_action(row, col, turn, board, b_cnt, w_cnt, t_cnt, move):
    # nonlocal b_cnt
    # nonlocal w_cnt
    # nonlocal t_cnt
    board[move[0]][move[1]] = turn
    if turn == Color.BLACK:
        b_cnt += 1
    else:
        w_cnt += 1
    t_cnt += 1

    for direction in directions:
        cnt = 0
        dx, dy = direction
        newx, newy = row + dx, col + dy

        # find the directions
        valid = False
        
        while 0 <= newx < SIZE and 0 <= newy < SIZE:
            if board[newx][newy] == None:
                break
            else:
                if cnt == 0:
                    if board[newx][newy] == turn:
                        break
                    else:
                        newx += dx
                        newy += dy
                        cnt += 1
                else:
                    if board[newx][newy] == turn:
                        valid = True
                        break
                    else:
                        newx += dx
                        newy += dy
                        cnt += 1

        # take actions on valid directions
        if valid:
            for i in range(0,cnt):
                newx, newy = row + dx*(i+1), col + dy*(i+1) 
                # print ('change: ',newx, newy,board[newx][newy], turn)
                board[newx][newy] = turn
                if turn == Color.BLACK:
                    b_cnt += 1
                    w_cnt -= 1
                else:
                    w_cnt += 1
                    b_cnt -= 1
    return b_cnt, w_cnt, t_cnt

def check_end_status(turn, b_cnt, w_cnt, t_cnt):
    # if one of them empty
    if b_cnt == 0 or w_cnt == 0:
        print ('one lose')
        return True
    # if all the board full
    if t_cnt == SIZE*SIZE:
        print ('full the board')
        return True

    return False

def play_game(input):
    board = [[None] * SIZE for _ in range(SIZE)]
    board[3][3] = Color.WHITE
    board[3][4] = Color.BLACK
    board[4][3] = Color.BLACK
    board[4][4] = Color.WHITE

    turn = Color.BLACK

    end_status = False

    b_cnt = 2
    w_cnt = 2
    t_cnt = 4

    while True:
        print ('')
        
        next_step_candidates = next_steps(turn, board)
        
        if not next_step_candidates:
            print ("no valid move, switch user")
            turn = Color.BLACK if turn != Color.BLACK else Color.WHITE
            continue
        # print (next_step_candidates)

        print (f"Score --> black: {b_cnt}, white: {w_cnt}, total: {t_cnt}")
        print ("|-------------------|")
        # print ("|                   |")
        print(board_str(board, next_step_candidates), end = '')
        # print ("|                   |")
        print ("|-------------------|")

        try:
            print('')
            print(f"Enter move for {turn.name.lower()}: ")
            str = next(input)
            move = parse_coordinate(str)
        except CoordinateParseError as e:
            print(f"Invalid move: {e}")
            print()
            continue
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            break     

        
        # valid the move
        if is_valid_move(move[0], move[1], turn, board):
            pass
        else:
            print ('############ not vaild move ################')
            continue

        # take the action
        b_cnt, w_cnt, t_cnt = take_action(move[0], move[1], turn, board, b_cnt, w_cnt, t_cnt, move)


        # check the status of end
        end_status = check_end_status(turn, b_cnt, w_cnt, t_cnt)
        if end_status:
            print ("*********** game_end ***********")
            print (f"Score --> black: {b_cnt}, white: {w_cnt}, total: {t_cnt}")
            break        

        # switch user
        turn = Color.BLACK if turn != Color.BLACK else Color.WHITE

    return


def main():
    input = sys.stdin
    play_game(input)


main()