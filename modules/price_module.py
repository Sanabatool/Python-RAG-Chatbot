from config import fetch_price_info


def process(question, tokens):

    # Cheapest course
    if any(word in tokens for word in ["cheapest", "lowest", "affordable", "cheap"]):

        cheapest = fetch_price_info()[0]

        return f"""
            <h3>💲 Cheapest Course</h3>
            <ul>
                <li><b>{cheapest['course_name']}</b> (${cheapest['course_price']})</li>
                <li><b>Trainer:</b> {cheapest['trainer']}</li>
            </ul>
        """

    # Most expensive course
    if any(word in tokens for word in ["expensive", "highest", "premium"]):

        expensive = fetch_price_info()[1]

        return f"""
            <h3>💎 Premium Course</h3>
            <ul>
                <li><b>{expensive['course_name']}</b> (${expensive['course_price']})</li>
                <li><b>Trainer:</b> {expensive['trainer']}</li>
            </ul>
        """

    return None