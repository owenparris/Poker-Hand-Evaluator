from random import shuffle
from itertools import combinations

RANKS = range(2,15)
SUITS = range(4)

DECK = tuple((rank-2) * 4 + suit for rank in RANKS for suit in SUITS)
CARD_RANK = [(c >> 2) + 2 for c in range(52)]
CARD_SUIT = [c & 3 for c in range(52)]

FULL_DECK_SET = set(DECK)


def flush_checker(cards_by_suit):
    for suit_cards in cards_by_suit:
        if len(suit_cards) >= 5:
            suit_cards.sort(reverse=True)
            return True, tuple(suit_cards), tuple(suit_cards[:5])
    return False, (), ()

def straight_finder(ranks_lst):
    for i in range(len(ranks_lst) - 4):
        window = ranks_lst[i:i+5]
        if window[0] - window[4] == 4 and len(set(window)) == 5:
            return window[0]
    return 0

def straight_checker(rank_counts):
    ranks = [r for r in range(14,1,-1) if rank_counts[r]]

    if 14 in ranks:
        ranks.append(1)

    for i in range(len(ranks)-4):
        if ranks[i] - ranks[i+4] == 4:
            return True, ranks[i]

    return False,0

def straight_flush_checker(flush):
    if flush[0]:
        flush_ranks = list(flush[1])
        if 14 in flush_ranks:
            flush_ranks.append(1)
        sf = straight_finder(flush_ranks)
        if sf:
            return True, sf
    return False, 0

def kicker_finder(rank_counts, exclude_ranks, n):
    kickers = []
    for rank in range(14,1,-1):
        if rank not in exclude_ranks and rank_counts[rank] != 0:
            kickers.append(rank)
            if len(kickers) == n:
                break
    return tuple(kickers)

def analyze_hand(hand):
    rank_counts = [0]*15
    cards_by_suit = [[],[],[],[]]

    for card in hand:
        rnk = CARD_RANK[card]
        idx = CARD_SUIT[card]
        rank_counts[rnk] += 1
        cards_by_suit[idx].append(rnk)

    return rank_counts, cards_by_suit

def hand_strength(hand):

    rank_counts, cards_by_suit = analyze_hand(hand)
    pairs_lst = []
    trips_lst = []
    quads_lst = []

    for rank in range(14, 1, -1):
        if rank_counts[rank] == 2: pairs_lst.append(rank)
        elif rank_counts[rank] == 3: trips_lst.append(rank)
        elif rank_counts[rank] == 4: quads_lst.append(rank)

    pairs_count = len(pairs_lst)
    trips_count = len(trips_lst)
    quads_count = len(quads_lst)

    flush = flush_checker(cards_by_suit)

    if flush[0]:
        straight_flush = straight_flush_checker(flush)
        if straight_flush[0]:
            return (8, straight_flush[1])

    if quads_count == 1:
        return (7, quads_lst[0], kicker_finder(rank_counts, quads_lst, 1))

    if trips_count >=2:
        return (6, trips_lst[0], max(trips_lst[1:] + pairs_lst))
    elif trips_count == 1 and pairs_count >= 1:
        return (6, trips_lst[0], pairs_lst[0])

    if flush[0]:
        return (5, flush[2])

    straight = straight_checker(rank_counts)
    if straight[0]:
        return (4, straight[1])

    if trips_count == 1:
        return (3, trips_lst[0], kicker_finder(rank_counts, trips_lst, 2))

    if pairs_count >= 2:
        return (2, pairs_lst[0], pairs_lst[1], kicker_finder(rank_counts, pairs_lst, 1))

    if pairs_count == 1:
        return (1, pairs_lst[0], kicker_finder(rank_counts, pairs_lst, 3))

    return (0, kicker_finder(rank_counts, [], 5))
        
def hand_comparison(hand_1, hand_2):
    strength_1 = hand_strength(hand_1)
    strength_2 = hand_strength(hand_2)
    if strength_1 == strength_2:
        return 0
    elif strength_1[0] > strength_2[0]:
        return 1
    elif strength_1[0] < strength_2[0]:
        return -1
    else:
        if strength_1 > strength_2:
            return 1
        else:
            return -1
        
def two_way_equity(hand_1, hand_2, board):
    print(f"Evaluating hand 1: {print_hand(hand_1)}, hand 2: {print_hand(hand_2)}, board: {print_hand(board)}")
    hand_1_wins = 0
    hand_2_wins = 0
    ties = 0
    if len(board) == 5:
        result = hand_comparison(hand_1, hand_2)
        if result == 1:
            return (1, 0, 0)
        elif result == -1:
            return (0, 1, 0)
        else:
            return (0, 0, 1)
    elif len(board) == 4:
        used = set(hand_1 + hand_2 + board)
        deck = list(FULL_DECK_SET - used)
        hand1_eval = [None]*7
        hand2_eval = [None]*7

        hand1_eval[0:6] = hand_1 + board
        hand2_eval[0:6] = hand_2 + board
        for card in deck:
            hand1_eval[6] = card
            hand2_eval[6] = card
            result = hand_comparison(hand1_eval, hand2_eval)
            if result == 1:
                hand_1_wins += 1
            elif result == -1:
                hand_2_wins += 1
            else:
                ties += 1
        total = hand_1_wins + hand_2_wins + ties
        return (hand_1_wins/total, hand_2_wins/total, ties/total)
    elif len(board) == 3:
        used = [False] * 52
        for c in hand_1 + hand_2 + board:
            used[c] = True
        deck = [c for c in range(52) if not used[c]]

        hand1_eval = [None]*7
        hand2_eval = [None]*7

        hand1_eval[0:5] = hand_1 + board
        hand2_eval[0:5] = hand_2 + board
        for card1, card2 in combinations(deck, 2):
            hand1_eval[5] = card1
            hand1_eval[6] = card2

            hand2_eval[5] = card1
            hand2_eval[6] = card2

            result = hand_comparison(hand1_eval, hand2_eval)
            if result == 1:
                hand_1_wins += 1
            elif result == -1:
                hand_2_wins += 1
            else:
                ties += 1
        total = hand_1_wins + hand_2_wins + ties
        return (hand_1_wins/total, hand_2_wins/total, ties/total)
    
    elif len(board) == 0:
        used = set(hand_1 + hand_2)
        deck = list(FULL_DECK_SET - used)
        hand1_eval = [None]*7
        hand2_eval = [None]*7

        hand1_eval[0:2] = hand_1
        hand2_eval[0:2] = hand_2
        for card1, card2, card3, card4, card5 in combinations(deck, 5):
                    
            hand1_eval[2] = card1
            hand1_eval[3] = card2
            hand1_eval[4] = card3
            hand1_eval[5] = card4
            hand1_eval[6] = card5

            hand2_eval[2] = card1
            hand2_eval[3] = card2
            hand2_eval[4] = card3
            hand2_eval[5] = card4
            hand2_eval[6] = card5

            result = hand_comparison(hand1_eval, hand2_eval)
            if result == 1:
                hand_1_wins += 1
            elif result == -1:
                hand_2_wins += 1
            else:
                ties += 1
        total = hand_1_wins + hand_2_wins + ties
        return (hand_1_wins/total, hand_2_wins/total, ties/total)

def print_hand(hand):
    rank_str = {10: 'T', 11:'J', 12:'Q', 13:'K', 14:'A'}
    suit_str = {0:'h', 1:'d', 2:'c', 3:'s'}
    hand_str = []
    for card in hand:
        rank = CARD_RANK[card]
        suit = CARD_SUIT[card]
        rank_display = rank_str.get(rank, str(rank))
        suit_display = suit_str[suit]
        hand_str.append(f"{rank_display}{suit_display}")
    return ' '.join(hand_str)

def main():
    new_deck = list(DECK)
    shuffle(new_deck)
    hand_1, hand_2 = [], []
    for _ in range(2):
        hand_1.append(new_deck.pop(-1))
        hand_2.append(new_deck.pop(-1))
    print(f'Hand 1: {print_hand(hand_1)}, Hand 2: {print_hand(hand_2)}')
    equity = two_way_equity(hand_1, hand_2, board=[])
    print(f"Hand 1 wins {equity[0] * 100:.2f}%, Hand 2 wins {equity[1]*100:.2f}%, Tie {equity[2]*100:.2f}%")

main()
    