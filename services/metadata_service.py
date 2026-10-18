import re


def detect_metadata(question):

    question = question.lower().strip()

    metadata = {}


    # ============================================================
    # DURATION
    # ============================================================

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(month|months|year|years|week|weeks|day|days)",
        question
    )


    if match:

        number = match.group(1)

        unit = match.group(2)


        if unit.startswith("month"):

            duration = f"{number} month"


        elif unit.startswith("year"):

            duration = f"{number} year"


        elif unit.startswith("week"):

            duration = f"{number} week"


        else:

            duration = f"{number} day"


        metadata["duration"] = duration


    # ============================================================
    # TRAINER
    # ============================================================

    trainers = [
        "batool",
        "sajidda",
        "fatima",
        "teacher",
        "admin",
        "sawera"
    ]


    for trainer in trainers:

        if trainer in question:

            metadata["trainer"] = trainer.title()

            break


    # ============================================================
    # PRICE
    # ============================================================

    price_match = re.search(
        r"(?:\$|rs\.?|pkr)\s*(\d+(?:\.\d+)?)",
        question
    )


    # Also allow:
    # courses under 100
    # courses below 500

    if not price_match:

        price_match = re.search(
            r"(?:under|below|less than|cheaper than|above|over|more than|greater than)\s+(\d+(?:\.\d+)?)",
            question
        )


    if price_match:

        price = float(
            price_match.group(
                price_match.lastindex
            )
        )


        if any(
            word in question
            for word in [
                "under",
                "below",
                "less than",
                "cheaper than"
            ]
        ):

            metadata["price"] = {
                "$lt": price
            }


        elif any(
            word in question
            for word in [
                "above",
                "more than",
                "greater than",
                "over"
            ]
        ):

            metadata["price"] = {
                "$gt": price
            }


        elif any(
            word in question
            for word in [
                "price",
                "cost",
                "costs",
                "worth"
            ]
        ):

            metadata["price"] = price


    return metadata