from datetime import datetime as dt
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
    Set alternate stylesheet for planeswalker and battle cards.
    """
    # Uses `or` instead of second parameter to `get` to replace empty string as well
    if "planeswalker" in card.get(column_mapping.get("super_type"), "").lower():
        card[column_mapping.get("stylesheet")] = (
            card.get(column_mapping.get("stylesheet")) or "m15-mainframe-planeswalker"
        )

    if "battle" in card.get(column_mapping.get("super_type"), "").lower():
        card[column_mapping.get("stylesheet")] = (
            card.get(column_mapping.get("stylesheet")) or "m15-battle"
        )


def fix_planeswalker_rule_text(
    card: dict[str, str], column_mapping: dict[str, str]
) -> None:
    """
    Planeswalkers get their own field for rules text instead of `rule_text`.
    """
    super_type = card.get(column_mapping.get("super_type"), "").lower()
    if "planeswalker" in super_type:
        card["level_1_text"] = card.pop(column_mapping.get("rule_text"), "")


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
    mana symbols and punctuation unicode
    """
    # Remove syntax for mana symbols since MSE does that automatically
    text = text.replace("{w}", "W").replace("{W}", "W")
    text = text.replace("{u}", "U").replace("{U}", "U")
    text = text.replace("{b}", "B").replace("{B}", "B")
    text = text.replace("{r}", "R").replace("{R}", "R")
    text = text.replace("{g}", "G").replace("{G}", "G")
    text = text.replace("{c}", "C").replace("{C}", "C")
    text = text.replace("{t}", "T").replace("{T}", "T")

    # Unescape HTML characters
    text = html.unescape(text)

    return text


def get_current_timestamp() -> str:
    """
    Get the current time as a formatted string.
    """
    return dt.now().strftime("%Y-%m-%d %H:%M:%S")
