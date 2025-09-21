from bet import Bet, str2bet
from betgroup import BetGroup
from tqdm import tqdm


jake_bet_tuples = {
    "locks": [
        ("Oregon Ducks TTP O 43.5", -150, 20.00, "20250920"),
        ("Florida State Seminoles -44.5", -130, 20.00, "20250920"),
    ],
    "leans": [
        ("Baylor Bears vs Arizona State Sun Devils O 59.5", -110, 20.00, "20250920"),
        ("Vanderbilt Commodores -25.5", -135, 20.00, "20250920"),
    ],
    "dogs": [
        ("Maryland Terrapins ML", 295, 20.00, "20250920"),
        ("Illinois Fighting Illini ML", 195, 20.00, "20250920"),
    ],
}

david_bet_tuples = {
    "locks": [
        ("Michigan Wolverines -2.5", -108, 20.00, "20250920"),
        ("Rutgers Scarlet Knights vs Iowa Hawkeyes U 47.5", -127, 20.0, "20250919"),
    ],
    "leans": [
        ("SMU Mustangs vs TCU Horned Frogs O 64.5", -108, 20.00, "20250920"),
        ("Texas Tech Red Raiders vs Utah Utes O 57.5", -110, 20.00, "20250920"),
    ],
    "dogs": [
        ("Illinois Fighting Illini ML", 195, 20.00, "20250920"),
        ("Army Black Knights ML", 110, 20.00, "20250920"),
    ],
}

blain_bet_tuples = {
    "locks": [
        ("UNLV Rebels -2.5", -110, 20.00, "20250920"),
        ("Missouri Tigers -9.5", -122, 20.00, "20250920"),
    ],
    "leans": [
        (
            "Kent State Golden Flashes vs Florida State Seminoles O 55.5",
            -110,
            20.00,
            "20250920",
        ),
        ("Baylor Bears vs Arizona State Sun Devils O 59.5", -110, 20.00, "20250920"),
    ],
    "dogs": [
        ("Auburn Tigers ML", 202, 20.00, "20250920"),
        ("Illinois Fighting Illini ML", 195, 20.00, "20250920"),
    ],
}

print("JAKE:")
jake_betgroups = []
for bet_tuple_name in jake_bet_tuples:
    bet_tuples = jake_bet_tuples[bet_tuple_name]

    bets = []

    for bet_str, odds, wager, date in tqdm(bet_tuples):
        bet = str2bet(bet_str, odds, wager, date)
        bets.append(bet)

    betgroup = BetGroup(
        bettor="Jake", description=bet_tuple_name, bets=bets
    )
    jake_betgroups.append(betgroup)
    print(betgroup.as_dict())
jake_betgroups.append(BetGroup.merge_betgroups("Jake", "Locks, Leans, & Dogs", jake_betgroups))
print("\n")
print(jake_betgroups[3].as_dict())
print("\n")

print("DAVID:")
david_betgroups = []
for bet_tuple_name in david_bet_tuples:
    bet_tuples = david_bet_tuples[bet_tuple_name]

    bets = []

    for bet_str, odds, wager, date in tqdm(bet_tuples):
        bet = str2bet(bet_str, odds, wager, date)
        bets.append(bet)

    betgroup = BetGroup(
        bettor="David", description=bet_tuple_name, bets=bets
    )
    david_betgroups.append(betgroup)
    print(betgroup.as_dict())
david_betgroups.append(BetGroup.merge_betgroups("David", "Locks, Leans, & Dogs", david_betgroups))
print("\n")
print(david_betgroups[3].as_dict())
print("\n")

print("BLAIN:")
blain_betgroups = []
for bet_tuple_name in blain_bet_tuples:
    bet_tuples = blain_bet_tuples[bet_tuple_name]

    bets = []

    for bet_str, odds, wager, date in tqdm(bet_tuples):
        bet = str2bet(bet_str, odds, wager, date)
        bets.append(bet)

    betgroup = BetGroup(
        bettor="Blain", description=bet_tuple_name, bets=bets
    )
    blain_betgroups.append(betgroup)
    print(betgroup.as_dict())
blain_betgroups.append(BetGroup.merge_betgroups("Blain", "Locks, Leans, & Dogs", blain_betgroups))
print("\n")
print(blain_betgroups[3].as_dict())
print("\n")

print("CRAIN & CO OVERALL:")
print(BetGroup.merge_betgroups("C&C", "Locks, Leans & Dogs", [jake_betgroups[3], david_betgroups[3], blain_betgroups[3]]).as_dict())