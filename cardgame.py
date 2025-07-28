import tkinter as tk
import random
import os

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]

def valid_play(card, top_card, current_suit):
    if card[:-1] == '8':
        return True
    return card[-1] == current_suit or card[:-1] == top_card[:-1]

def get_card_colors(card):
    suit = card[-1]
    if suit == '♥' or suit == '♦':
        return ("red", "white")
    else:
        return ("black", "white")

def get_game_mode():
    mode_win = tk.Tk()
    mode_win.title("Choose Game Mode")
    mode = tk.StringVar(value="pvp")

    tk.Label(mode_win, text="Select Game Mode:").pack(padx=10, pady=10)
    tk.Radiobutton(mode_win, text="Player vs Player", variable=mode, value="pvp").pack(anchor="w", padx=20)
    tk.Radiobutton(mode_win, text="Player vs Computer", variable=mode, value="pvc").pack(anchor="w", padx=20)

    def submit():
        mode_win.destroy()
    tk.Button(mode_win, text="Continue", command=submit).pack(pady=10)
    mode_win.mainloop()
    return mode.get()

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

class CardGameGUI:
    def __init__(self, root, player_names, mode):
        self.root = root
        self.player_names = player_names
        self.mode = mode  # "pvp" or "pvc"
        self.root.title("Crazy Eights")
        self.deck = create_deck()
        random.shuffle(self.deck)
        self.player_hands = [self.deck[:7], self.deck[7:14]]
        self.deck = self.deck[14:]
        self.discard_pile = [self.deck.pop()]
        self.current_suit = self.discard_pile[-1][-1]
        self.turn = 0

        self.top_card_label = tk.Label(
            root,
            text=f"Top card: {self.discard_pile[-1]}",
            font=("Arial", 32, "bold"),
            pady=20,
            bg="#b3e0ff"
        )
        self.top_card_label.pack()
        fg, bg = get_card_colors(self.discard_pile[-1])
        self.top_card_btn = tk.Button(
            root,
            text=self.discard_pile[-1],
            font=("Arial", 24, "bold"),
            width=8,
            height=2,
            state=tk.DISABLED,
            disabledforeground=fg,
            relief=tk.RIDGE,
            bg=bg
        )
        self.top_card_btn.pack(pady=20)

        self.hand_frame = tk.Frame(root, bg="#b3e0ff")
        self.hand_frame.pack()
        self.draw_button = tk.Button(root, text="Draw Card", command=self.draw_card)
        self.draw_button.pack()
        self.card_images = {}
        self.load_card_images()
        self.update_hand()

        self.restart_button = tk.Button(root, text="Restart Game", command=self.restart_game)
        self.restart_button.pack()

        self.scores = [0, 0]
        self.status = tk.Label(root, text=f"{self.player_names[0]}'s turn", bg="#b3e0ff")
        self.status.pack()

        self.score_label = tk.Label(root, text=f"Scores - {self.player_names[0]}: {self.scores[0]} | {self.player_names[1]}: {self.scores[1]}", bg="#b3e0ff")
        self.score_label.pack()

        self.timer_label = tk.Label(root, text="Time left: 20", bg="#b3e0ff")
        self.timer_label.pack()
        self.time_left = 20
        self.timer_running = False
        self.start_timer()

        self.update_status()
        self.root.configure(bg="#b3e0ff")

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
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        hand = self.player_hands[self.turn]
        for card in hand:
            fg, bg = get_card_colors(card)
            btn = tk.Button(
                self.hand_frame,
                text=card,
                font=("Arial", 18, "bold"),
                width=8,
                height=2,
                fg=fg,
                bg=bg,
                command=lambda c=card: self.play_card(c)
            )
            btn.pack(side=tk.LEFT)
        self.draw_button.config(state=tk.NORMAL if self.deck else tk.DISABLED)

    def play_card(self, card):
        top_card = self.discard_pile[-1]
        if valid_play(card, top_card, self.current_suit):
            self.player_hands[self.turn].remove(card)
            self.discard_pile.append(card)
            if card[:-1] == '8':
                self.choose_suit(card)
                return
            self.current_suit = card[-1]
            self.next_turn()
        else:
            self.status.config(text="Invalid play! Try again.")

    def choose_suit(self, card):
        suit_win = tk.Toplevel(self.root)
        suit_win.title("Choose Suit")
        tk.Label(suit_win, text="Choose a suit for the wild eight:").pack()
        for suit in SUITS:
            tk.Button(suit_win, text=suit, command=lambda s=suit: self.set_suit(s, suit_win)).pack()

    def set_suit(self, suit, win):
        self.current_suit = suit
        win.destroy()
        self.next_turn()

    def next_turn(self):
        if not self.player_hands[self.turn]:
            self.scores[self.turn] += 1
            self.status.config(text=f"{self.player_names[self.turn]} wins!")
            self.score_label.config(text=f"Scores - {self.player_names[0]}: {self.scores[0]} | {self.player_names[1]}: {self.scores[1]}")
            self.hand_frame.destroy()
            self.timer_running = False
            return
        self.turn = 1 - self.turn
        self.status.config(text=f"{self.player_names[self.turn]}'s turn")
        self.top_card_label.config(text=f"Top card: {self.discard_pile[-1]}")
        fg, bg = get_card_colors(self.discard_pile[-1])
        self.top_card_btn.config(text=self.discard_pile[-1], disabledforeground=fg, bg=bg)
        self.update_hand()
        self.timer_running = False
        self.start_timer()
        if self.mode == "pvc" and self.turn == 1:
            self.root.after(1000, self.computer_move)

    def computer_move(self):
        hand = self.player_hands[1]
        top_card = self.discard_pile[-1]
        for card in hand:
            if valid_play(card, top_card, self.current_suit):
                self.play_card(card)
                return
        self.draw_card()

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
            self.status.config(text=f"{self.player_names[self.turn]} drew a card.")
            self.update_hand()

    def restart_game(self):
        self.deck = create_deck()
        random.shuffle(self.deck)
        self.player_hands = [self.deck[:7], self.deck[7:14]]
        self.deck = self.deck[14:]
        self.discard_pile = [self.deck.pop()]
        self.current_suit = self.discard_pile[-1][-1]
        self.turn = 0
        self.status.config(text=f"{self.player_names[0]}'s turn")
        fg, bg = get_card_colors(self.discard_pile[-1])
        self.top_card_btn.config(
            text=self.discard_pile[-1],
            disabledforeground=fg,
            bg=bg
        )
        self.hand_frame.destroy()
        self.hand_frame = tk.Frame(self.root, bg="#b3e0ff")
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
                self.root.after(1000, self.update_timer)
            else:
                self.status.config(text=f"{self.player_names[self.turn]} ran out of time! Turn passes.")
                self.timer_running = False
                self.next_turn()
                self.start_timer()

    def update_status(self):
        self.status.config(text=f"{self.player_names[self.turn]}'s turn")
        self.score_label.config(text=f"Scores - {self.player_names[0]}: {self.scores[0]} | {self.player_names[1]}: {self.scores[1]}")

if __name__ == "__main__":
    mode = get_game_mode()
    player_names = get_player_names()
    root = tk.Tk()
    app = CardGameGUI(root, player_names, mode)
    root.mainloop()