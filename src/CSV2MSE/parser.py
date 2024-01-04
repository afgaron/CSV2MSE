import datetime as dt
import html


def fix_card_type(card: dict[str, str], column_mapping: dict[str, str]) -> None:
    """
    Combine the card type and supertype into one string.
    """
    if card.get(column_mapping.get("card_type")):
        super_type = card.get(column_mapping.get("super_type"), "")
        card_type = card.get(column_mapping.get("card_type"), "")
        card[column_mapping.get("super_type")] = f"{super_type} {card_type}".strip()

    if card.get(column_mapping.get("card_type_2")):
        super_type = card.get(column_mapping.get("super_type_2"), "")
        card_type = card.get(column_mapping.get("card_type_2"), "")
        card[column_mapping.get("super_type_2")] = f"{super_type} {card_type}".strip()


def fix_stylesheet(card: dict[str, str], column_mapping: dict[str, str]) -> None:
    """
    Set alternate stylesheet when easily detectable. Can handle planeswalkers, battles,
    two-faced cards (e.g. DFCs, adventures) and tokens.
    """
    # Make sure `stylesheet` is defined
    column_mapping["stylesheet"] = column_mapping.get("stylesheet", "stylesheet")

    # Uses `or` instead of second parameter to `get` to replace empty string as well
    if "planeswalker" in card.get(column_mapping.get("super_type"), "").lower():
        card[column_mapping.get("stylesheet")] = (
            card.get(column_mapping.get("stylesheet")) or "m15-mainframe-planeswalker"
        )

    if "battle" in card.get(column_mapping.get("super_type"), "").lower():
        card[column_mapping.get("stylesheet")] = (
            card.get(column_mapping.get("stylesheet")) or "m15-battle"
        )

    if (
        "token" in card.get(column_mapping.get("super_type"), "").lower()
        or "emblem" in card.get(column_mapping.get("super_type"), "").lower()
    ):
        card[column_mapping.get("stylesheet")] = (
            card.get(column_mapping.get("stylesheet")) or "m15-mainframe-tokens"
        )

    if card.get(column_mapping.get("name_2")):
        card[column_mapping.get("stylesheet")] = (
            card.get(column_mapping.get("stylesheet")) or "m15-mainframe-dfc"
        )


def fix_planeswalker_rule_text(
    card: dict[str, str], column_mapping: dict[str, str]
) -> None:
    """
    Planeswalkers get their own field for rules text instead of `rule_text`.
    """
    # Make sure `level_1_text` is defined
    column_mapping["level_1_text"] = column_mapping.get("level_1_text", "level_1_text")

    super_type = card.get(column_mapping.get("super_type"), "").lower()
    if "planeswalker" in super_type:
        card["level_1_text"] = card.pop(column_mapping.get("rule_text"), "")


def needs_power_toughness_loyalty(
    col: str, card: dict[str, str], column_mapping: dict[str, str]
) -> bool:
    """
    Check that only creatures have power/toughness and planeswalkers/battles have loyalty.
    """
    has_col = (
        (
            col == "power"
            and "creature" in card.get(column_mapping.get("super_type"), "").lower()
        )
        or (
            col == "power_2"
            and "creature" in card.get(column_mapping.get("super_type_2"), "").lower()
        )
        or (
            col == "toughness"
            and "creature" in card.get(column_mapping.get("super_type"), "").lower()
        )
        or (
            col == "toughness_2"
            and "creature" in card.get(column_mapping.get("super_type_2"), "").lower()
        )
        or (
            col == "loyalty"
            and (
                "planeswalker" in card.get(column_mapping.get("super_type"), "").lower()
                or "battle" in card.get(column_mapping.get("super_type"), "").lower()
            )
        )
        or (
            col == "loyalty_2"
            and (
                "planeswalker"
                in card.get(column_mapping.get("super_type_2"), "").lower()
                or "battle" in card.get(column_mapping.get("super_type_2"), "").lower()
            )
        )
    )

    return has_col


def fix_rarity(rarity: str) -> str:
    """
    Coerce the provided rarity description into something accepted by MSE if possible.
    """
    rarity = rarity.lower()
    if rarity in [
        "basic land",
        "common",
        "uncommon",
        "rare",
        "mythic rare",
        "special",
        "masterpiece",
    ]:
        return rarity
    elif "basic" in rarity:
        return "basic land"
    elif "token" in rarity:
        return "commmon"
    elif "mythic" in rarity:
        return "mythic rare"
    elif "timeshifted" in rarity or "purple" in rarity:
        return "special"
    elif "expedition" in rarity:
        return "masterpiece"
    else:
        return ""


def fix_multiline_text(text: str) -> str:
    """
    Fix newlines in rule and flavor text so it doesn't break MSE.
    """
    mse_text = ""
    for line in text.split("\n"):
        mse_text += f"\n\t\t" + line.strip()
    return mse_text


def fix_symbols(text: str) -> str:
    """
    Replace encoded mana symbols and HTML characters into plaintext versions.
    """
    # Ensure string exists, even if its empty
    text = text or ""

    # Remove syntax for mana symbols since MSE does that automatically
    for letter in ["W", "U", "R", "B", "G", "C", "S", "T", "X"]:
        text = text.replace(f"{{{letter}}}", letter)
        text = text.replace(f"{{{letter.lower()}}}", letter)
    for number in range(10):
        text = text.replace(f"{{{number}}}", str(number))

    # Unescape HTML characters
    text = text.replace("&quot;&quot;", "&quot;")
    text = text.replace("&mdash;", "--")
    text = html.unescape(text)

    return text


def get_current_timestamp() -> str:
    """
    Get the current time as a formatted string.
    """
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
