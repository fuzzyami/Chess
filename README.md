This repo contains a simplified Chess simulation I wrote for a company as part of my job interview process. 
The task at hand was to write a Chess simulator that would receive two players and their respective moves,
and would determine which of them has won.


the exercise called for an implementation of a simulator that does the following things:
1. determines which user won the game, which implies being able to detect Check-mate (end of game). 
    This is actually the hardest problem, as discussed below.
    
2. validating user input, which implies the following:
    for every turn, get a Move from the player: 
    
    * taking care to handle exceptions that might arise from the Player's code
    
    * taking care to limit the Player's runtime (protect against sleeps or unterminated processes)
    
    * validating the move against the rules of Chess
    
There's a world of difference between (1) and (2):

validating a a move is not a simple task, but its a fairly closed problem: 

    given a move: determine its valid in the following respects:
    1. the move is valid globally (right color, sensible coordinates)
    2. the move is valid for the moved piece (right movement pattern for this piece)
    3. the move is valid for the piece AND the current state of the board: for example, 
        pieces cant jump over other pieces.
    4. (if in Check) the move is valid in the context of Check - it must resolve the check.
    
On the other hand, detecting check-mate requires:

    1. detecting check has happened, and then:
    2. carefully considering EVERY POSSIBLE MOVE by the checked side, 
        and ensuring none of them will resolve the check.
        
### Detecting Check-mate and validating moves during Check using a temporary board:
during Check, a move is only valid if it resolves the Check. To calculate whether a move is valid during Check,
I do the following:
1. create a copy of the board with its state,
2. run the move and ignore the restrictions imposed by the Check,
3. determine whether the player is still under Check after the move
4. dispose of the copy

If board is still in Check, the move was invalid. Otherwise, its a valid move and it can be applied.

A similar trick is used for detecting Check-mate: in order to determine whether there is a valid
move that would resolve the Check, I run all the possible moves, each on a copy of the current board
and determine whether the check was resolved.


### What I did not implement, Chess-wise:

I did not implement all the rules of check, but rather, a limited version of the logic:
* crowning, castling and 'en passent' were not implemented.
* pawns are not allowed to jump 2 pieces ahead
* rules like 50 turns or 3-repetitions were not implemented
* check-detection is limited to pawns and knights.
* check-mate detection is limited to the King's options, only. In other words, if the king is checked
but has no way to resolve the check itself, its check-mate, even if another piece could have resolved it.

### OOP considerations:
This is a classic OOP problem. Modelling the various pieces naturally lends itself to the following:
* an abstract piece with color, position, and type (like King, Queen etc)
* a set of concrete pieces, each with its specific movement rules.
* a board (8X8) rubrics which I modeled as a 2-dim array the holds the various pieces. 
* "empty" rubrics hold a special "Placeholder" piece.

the above is sufficient to effectively determine whether a move is valid, but is NOT sufficient to 
efficiently determine whether a check-mate has happened. For that you need to have reverse lookup on the pieces,
or else you need to scan the entire board on every move for the right pieces. To avoid that, 
I added a dictionary that maps (for each side) the list of pieces that are still on the bord:

    black pieces:
        left-horse ("LH") -> its object, which knows its position.
        right-horse ("RH") -> its object
        ...
    white pieces:
        ...
        
I also added a dictionary for the pieces that were removed and under some scenarios, it makes sense
to have a list of previous moves.

### Malicious code considerations:
When getting the next move by a player, I chose to call that function in a separate thread and limit its run time with
a timeout. If the player does not return the move within 1 second, that thread is stopped.  

### Things I'd do differently, the next time:
To correctly handle check-mate, I would need to consider all the pieces on the board (which I dont do now).
It would make sense to compute, for each piece, at every turn, the following: 
    
    * list of pieces under attack by that piece
    * list of coordinates that can be moved to, by that piece. 

this is computationally heavy, though. 
