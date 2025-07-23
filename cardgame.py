import tkinter as tk                # Import the tkinter library for GUI
import random                      # Import random for shuffling the deck

SUITS = ['♠', '♥', '♦', '♣']       # List of card suits
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']  # List of card ranks

def create_deck():
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]  # Create a deck of 52 cards

def valid_play(card, top_card, current_suit):
    if card[:-1] == '8':           # If the card is an eight, it's always valid (wild card)
        return True
    return card[-1] == current_suit or card[:-1] == top_card[:-1]  # Valid if suit matches or rank matches

class CardGameGUI:
    def __init__(self, root):
        self.root = root           # Store the root window
        self.root.title("Crazy Eights")  # Set window title
        self.deck = create_deck()  # Create a new deck
        random.shuffle(self.deck)  # Shuffle the deck
        self.player_hands = [self.deck[:7], self.deck[7:14]]  # Deal 7 cards to each player
        self.deck = self.deck[14:] # Remove dealt cards from the deck
        self.discard_pile = [self.deck.pop()]  # Start discard pile with one card from deck
        self.current_suit = self.discard_pile[-1][-1]  # Set current suit to suit of top discard
        self.turn = 0              # Start with player 1's turn (index 0)

        self.status = tk.Label(root, text="Player 1's turn")  # Label to show whose turn
        self.status.pack()         # Add label to window

        self.top_card_label = tk.Label(root, text=f"Top card: {self.discard_pile[-1]}")  # Show top card
        self.top_card_label.pack() # Add label to window

        self.hand_frame = tk.Frame(root)  # Frame to hold player's hand (buttons)
        self.hand_frame.pack()            # Add frame to window
        self.draw_button = tk.Button(root, text="Draw Card", command=self.draw_card)  # Add draw button
        self.draw_button.pack()
        self.update_hand()                # Display player's hand

    def update_hand(self):
        for widget in self.hand_frame.winfo_children():  # Remove old buttons
            widget.destroy()
        hand = self.player_hands[self.turn]              # Get current player's hand
        for card in hand:                               # For each card in hand
            btn = tk.Button(
                self.hand_frame,                        # Place button in hand_frame
                text=card,                              # Button text is card
                font=("Arial", 24, "bold"),             # Large bold font
                width=4,                                # Button width
                height=2,                               # Button height
                command=lambda c=card: self.play_card(c) # When clicked, play the card
            )
            btn.pack(side=tk.LEFT)                      # Pack button to the left
        # Enable draw button only if no valid play
        top_card = self.discard_pile[-1]
        can_play = any(valid_play(card, top_card, self.current_suit) for card in hand)
        self.draw_button.config(state=tk.NORMAL if not can_play and self.deck else tk.DISABLED)

    def play_card(self, card):
        top_card = self.discard_pile[-1]                # Get top card of discard pile
        if valid_play(card, top_card, self.current_suit): # Check if play is valid
            self.player_hands[self.turn].remove(card)    # Remove card from player's hand
            self.discard_pile.append(card)               # Add card to discard pile
            if card[:-1] == '8':                         # If card is an eight
                self.choose_suit(card)                   # Let player choose new suit
                return                                  # Stop further actions
            self.current_suit = card[-1]                 # Update current suit
            self.next_turn()                             # Move to next turn
        else:
            self.status.config(text="Invalid play! Try again.") # Show invalid play message

    def choose_suit(self, card):
        suit_win = tk.Toplevel(self.root)                # Create popup window
        suit_win.title("Choose Suit")                    # Set popup title
        tk.Label(suit_win, text="Choose a suit for the wild eight:").pack() # Instruction label
        for suit in SUITS:                               # For each suit
            tk.Button(suit_win, text=suit, command=lambda s=suit: self.set_suit(s, suit_win)).pack() # Button for suit

    def set_suit(self, suit, win):
        self.current_suit = suit                         # Set current suit to chosen suit
        win.destroy()                                    # Close popup window
        self.next_turn()                                 # Move to next turn

    def next_turn(self):
        if not self.player_hands[self.turn]:             # If current player has no cards left
            self.status.config(text=f"Player {self.turn + 1} wins!") # Announce winner
            self.hand_frame.destroy()                    # Remove hand frame (end game)
            return                                       # Stop further actions
        self.turn = 1 - self.turn                        # Switch turn (0->1, 1->0)
        self.status.config(text=f"Player {self.turn + 1}'s turn") # Update turn label
        self.top_card_label.config(text=f"Top card: {self.discard_pile[-1]}") # Update top card label
        self.update_hand()                               # Show new player's hand

    def draw_card(self):
        if self.deck:
            card = self.deck.pop()
            self.player_hands[self.turn].append(card)
            self.status.config(text=f"Player {self.turn + 1} drew a card.")
            self.update_hand()
        else:
            self.status.config(text="No cards left to draw!")

if __name__ == "__main__":                              # If running as main program
    root = tk.Tk()                                      # Create main window
    app = CardGameGUI(root)                             # Create game GUI
    root.mainloop()                                     # Start Tkinter