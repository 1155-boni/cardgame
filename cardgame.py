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

def get_card_colors(card):
    # Returns (foreground, background) tuple based on suit
    suit = card[-1]
    if suit == '♥' or suit == '♦':
        return ("red", "white")    # Red suits
    else:
        return ("black", "white")  # Black suits

class CardGameGUI:
    def __init__(self, root, player_names):
        self.root = root
        self.player_names = player_names  # <-- Add this line first!
        self.root.title("Crazy Eights")  # Set window title
        self.deck = create_deck()  # Create a new deck
        random.shuffle(self.deck)  # Shuffle the deck
        self.player_hands = [self.deck[:7], self.deck[7:14]]  # Deal 7 cards to each player
        self.deck = self.deck[14:] # Remove dealt cards from the deck
        self.discard_pile = [self.deck.pop()]  # Start discard pile with one card from deck
        self.current_suit = self.discard_pile[-1][-1]  # Set current suit to suit of top discard
        self.turn = 0              # Start with player 1's turn (index 0)

        self.status = tk.Label(root, text=f"{self.player_names[0]}'s turn")  # Label to show whose turn
        self.status.pack()         # Add label to window

        fg, bg = get_card_colors(self.discard_pile[-1])
        self.top_card_label = tk.Label(
            root, 
            text=f"Top card: {self.discard_pile[-1]}",
            font=("Arial", 32, "bold"),   # Larger font size
            pady=20                       # Extra vertical padding
        )
        self.top_card_label.pack() # Add label to window

        self.top_card_btn = tk.Button(
            root,
            text=self.discard_pile[-1],
            font=("Arial", 18, "bold"),
            width=6,
            height=4,
            state=tk.DISABLED,
            disabledforeground=fg,   # Use suit color for disabled text
            relief=tk.RIDGE,
            bg=bg
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
        self.score_label = tk.Label(root, text=f"Scores - {self.player_names[0]}: {self.scores[0]} | {self.player_names[1]}: {self.scores[1]}")
        self.score_label.pack()

        self.timer_label = tk.Label(root, text="Time left: 20")
        self.timer_label.pack()
        self.time_left = 20
        self.timer_running = False
        self.start_timer()

        self.player_names = player_names
        self.update_status()

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
            fg, bg = get_card_colors(card)
            btn = tk.Button(
                self.hand_frame,
                text=card,
                font=("Arial", 18, "bold"),
                width=6,
                height=4,
                fg=fg,                   # Set text color
                bg=bg,                   # Set background color
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
            self.status.config(text=f"{self.player_names[self.turn]} wins!")
            self.score_label.config(text=f"Scores - {self.player_names[0]}: {self.scores[0]} | {self.player_names[1]}: {self.scores[1]}")
            self.hand_frame.destroy()
            self.timer_running = False
            return
        self.turn = 1 - self.turn
        self.status.config(text=f"Player {self.turn + 1}'s turn")
        self.top_card_label.config(text=f"Top card: {self.discard_pile[-1]}")
        self.top_card_btn.config(text=self.discard_pile[-1])
        self.update_hand()
        self.timer_running = False         # Stop any previous timer
        self.start_timer()                 # Start a new timer for the new turn

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
        fg, bg = get_card_colors(self.discard_pile[-1])
        self.top_card_btn.config(
    text=self.discard_pile[-1],
    disabledforeground=fg,
    bg=bg
)
        self.hand_frame.destroy()
        self.hand_frame = tk.Frame(self.root)
        self.hand_frame.pack()
        self.update_hand()

    def start_timer(self):
        self.time_left = 20
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.timer_label.config(text=f"Time left: {self.time_left}")
            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(2000, self.update_timer)
            else:
                self.status.config(text=f"Player {self.turn + 1} ran out of time! Turn passes.")
                self.timer_running = False
                self.next_turn()
                self.start_timer()

    def get_player_names(self):
        name_win = tk.Tk()
        name_win.title("Enter Player Names")
        tk.Label(name_win, text="Player 1 Name:").grid(row=0, column=0)
        tk.Label(name_win, text="Player 2 Name:").grid(row=1, column=0)
        p1_entry = tk.Entry(name_win)
        p2_entry = tk.Entry(name_win)
        p1_entry.grid(row=0, column=1)
        p2_entry.grid(row=1, column=1)
        names = []

        def submit():
            names.append(p1_entry.get() or "Player 1")
            names.append(p2_entry.get() or "Player 2")
            name_win.destroy()

        tk.Button(name_win, text="Start Game", command=submit).grid(row=2, column=0, columnspan=2)
        name_win.mainloop()
        return names

    def update_status(self):
        self.status.config(text=f"{self.player_names[self.turn]}'s turn")
        self.score_label.config(text=f"Scores - {self.player_names[0]}: {self.scores[0]} | {self.player_names[1]}: {self.scores[1]}")

if __name__ == "__main__":
    def get_player_names():
        name_win = tk.Tk()
        name_win.title("Enter Player Names")
        tk.Label(name_win, text="Player 1 Name:").grid(row=0, column=0)
        tk.Label(name_win, text="Player 2 Name:").grid(row=1, column=0)
        p1_entry = tk.Entry(name_win)
        p2_entry = tk.Entry(name_win)
        p1_entry.grid(row=0, column=1)
        p2_entry.grid(row=1, column=1)
        names = []

        def submit():
            names.append(p1_entry.get() or "Player 1")
            names.append(p2_entry.get() or "Player 2")
            name_win.destroy()

        tk.Button(name_win, text="Start Game", command=submit).grid(row=2, column=0, columnspan=2)
        name_win.mainloop()
        return names

    player_names = get_player_names()
    root = tk.Tk()
    app = CardGameGUI(root, player_names)
    root.mainloop()