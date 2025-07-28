import tkinter as tk                # Import the tkinter library for GUI
import random                      # Import random for shuffling the deck
import os

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

        self.top_card_label = tk.Label(
            root,
            text=f"Top card: {self.discard_pile[-1]}",
            font=("Arial", 32, "bold"),   # Larger font size
            pady=20                       # Extra vertical padding
        )
        self.top_card_label.pack() # Add label to window

        self.top_card_btn = tk.Button(
            root,
            text=self.discard_pile[-1],           # Show the top card
            font=("Arial", 24, "bold"),           # Large font for visibility
            width=8,                              # Same width as hand cards
            height=2,                             # Same height as hand cards
            state=tk.DISABLED,                    # Make it non-clickable
            disabledforeground="black",           # Text color when disabled
            relief=tk.RIDGE,                      # Card-like border
            bg="white"                            # Card background
        )
        self.top_card_btn.pack(pady=20)           # Add vertical padding

        self.hand_frame = tk.Frame(root)  # Frame to hold player's hand (buttons)
        self.hand_frame.pack()            # Add frame to window
        self.draw_button = tk.Button(root, text="Draw Card", command=self.draw_card)  # Add draw button
        self.draw_button.pack()
        self.card_images = {}  # Dictionary to store PhotoImage objects
        self.load_card_images()  # Load all card images
        self.update_hand()                # Display player's hand

        self.restart_button = tk.Button(root, text="Restart Game", command=self.restart_game)
        self.restart_button.pack()

        self.scores = [0, 0]
        self.score_label = tk.Label(root, text=f"Scores - Player 1: {self.scores[0]} | Player 2: {self.scores[1]}")
        self.score_label.pack()

        self.timer_label = tk.Label(root, text="Time left: 10")
        self.timer_label.pack()
        self.time_left = 10
        self.timer_running = False
        self.start_timer()

    def load_card_images(self):
        for suit in SUITS:
            for rank in RANKS:
                card_name = f"{rank}{suit}"
                img_path = os.path.join("cards", f"{card_name}.png")
                if os.path.exists(img_path):
                    self.card_images[card_name] = tk.PhotoImage(file=img_path)
                else:
                    self.card_images[card_name] = None  # Or a default image

    def update_hand(self):
        for widget in self.hand_frame.winfo_children():  # Remove old buttons
            widget.destroy()
        hand = self.player_hands[self.turn]              # Get current player's hand
        for card in hand:                               # For each card in hand
            btn = tk.Button(
                self.hand_frame,
                text=card,                              # Only show card text
                font=("Arial", 18, "bold"),             # Slightly smaller font
                width=8,                                # Wider button for text
                height=2,                               # Shorter button for text
                command=lambda c=card: self.play_card(c) # When clicked, play the card
            )
            btn.pack(side=tk.LEFT)                      # Pack button to the left
        # Enable draw button always if deck is not empty
        self.draw_button.config(state=tk.NORMAL if self.deck else tk.DISABLED)

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
        if not self.player_hands[self.turn]:
            self.scores[self.turn] += 1
            self.status.config(text=f"Player {self.turn + 1} wins!")
            self.score_label.config(text=f"Scores - Player 1: {self.scores[0]} | Player 2: {self.scores[1]}")
            self.hand_frame.destroy()
            self.timer_running = False
            return
        self.turn = 1 - self.turn
        self.status.config(text=f"Player {self.turn + 1}'s turn")
        self.top_card_btn.config(text=self.discard_pile[-1])  # <-- update button, not label
        self.update_hand()
        self.start_timer()

    def draw_card(self):
        if not self.deck:
            if len(self.discard_pile) > 1:
                top = self.discard_pile.pop()
                random.shuffle(self.discard_pile)
                self.deck = self.discard_pile
                self.discard_pile = [top]
            else:
                self.status.config(text="No cards left to draw!")
                return
        if self.deck:
            card = self.deck.pop()
            self.player_hands[self.turn].append(card)
            self.status.config(text=f"Player {self.turn + 1} drew a card.")
            self.update_hand()

    def restart_game(self):
        self.deck = create_deck()
        random.shuffle(self.deck)
        self.player_hands = [self.deck[:7], self.deck[7:14]]
        self.deck = self.deck[14:]
        self.discard_pile = [self.deck.pop()]
        self.current_suit = self.discard_pile[-1][-1]
        self.turn = 0
        self.status.config(text="Player 1's turn")
        self.top_card_btn.config(text=self.discard_pile[-1])  # <-- update button, not label
        self.hand_frame.destroy()
        self.hand_frame = tk.Frame(self.root)
        self.hand_frame.pack()
        self.update_hand()

    def start_timer(self):
        self.time_left = 10
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.timer_label.config(text=f"Time left: {self.time_left}")
            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.status.config(text=f"Player {self.turn + 1} ran out of time! Turn passes.")
                self.timer_running = False
                self.next_turn()
                self.start_timer()

if __name__ == "__main__":                              # If running as main program
    root = tk.Tk()                                      # Create main window
    app = CardGameGUI(root)                             # Create game GUI
    root.mainloop()                                     # Start Tkinter