from sqlalchemy import create_engine, text

# Connect to the database
db_engine = create_engine("mysql+pymysql://root:@localhost/lmsys")

def fetch_courses():
    query = """
    SELECT 
        courses.id, courses.package_id, courses.name AS course_name, courses.description AS course_description,
        courses.image, courses.trainer, courses.duration, courses.content_type, courses.price AS course_price,
        courses.rating, packages.name AS package_name, packages.price AS package_price,
        packages.description AS package_description
    FROM courses
    JOIN packages ON courses.package_id = packages.id
    """
    with db_engine.connect() as connection:
        result = connection.execution_options(stream_results=True).execute(text(query))
        return [
            {
                "id": row.id,
                "package_id": row.package_id,
                "course_name": row.course_name,
                "course_description": row.course_description,
                "image": row.image,
                "trainer": row.trainer,
                "duration": row.duration,
                "content_type": row.content_type,
                "course_price": row.course_price,
                "rating": row.rating,
                "package_name": row.package_name,
                "package_price": row.package_price,
                "package_description": row.package_description,
            }
            for row in result
        ]

def fetch_courses_count():
    query = "SELECT COUNT(*) FROM courses"
    with db_engine.connect() as connection:
        result = connection.execute(text(query)).fetchone()
        if result and result[0] is not None:
            return result[0]  # Return the count directly
        return 0  # Return 0 if no courses found



def fetch_price_info(price_limit=None):
    with db_engine.connect() as connection:
        # If user asks for courses under a certain price
        if price_limit:
            query = "SELECT name, price, trainer, description FROM courses WHERE price <= :price ORDER BY price ASC"
            params = {"price": price_limit}
            result = connection.execute(text(query), params).fetchall()

            if result:
                return [
                    {
                        "course_name": row.name,
                        "course_price": row.price,
                        "trainer": row.trainer,
                        "description": row.description,
                    }
                    for row in result
                ]
            return []  # No courses found under the price limit

        # Fetch both cheapest and most expensive courses
        cheapest_query = "SELECT name, price, trainer, description FROM courses ORDER BY price ASC LIMIT 1"
        expensive_query = "SELECT name, price, trainer, description FROM courses ORDER BY price DESC LIMIT 1"

        cheapest_result = connection.execute(text(cheapest_query)).fetchone()
        expensive_result = connection.execute(text(expensive_query)).fetchone()

        return [
            {
                "course_name": cheapest_result.name,
                "course_price": cheapest_result.price,
                "trainer": cheapest_result.trainer,
                "description": cheapest_result.description,
            } if cheapest_result else None,

            {
                "course_name": expensive_result.name,
                "course_price": expensive_result.price,
                "trainer": expensive_result.trainer,
                "description": expensive_result.description,
            } if expensive_result else None,
        ]

def fetch_top_rated_courses(limit=3):
    query = """
    SELECT c.name, c.trainer, c.price, AVG(r.rating) AS avg_rating
    FROM courses c
    JOIN reviews r ON c.id = r.course_id
    GROUP BY c.id
    ORDER BY avg_rating DESC
    LIMIT :limit
    """
    with db_engine.connect() as conn:
        result = conn.execute(text(query), {"limit": limit}).fetchall()
        return [
            {
                "course_name": row.name,
                "trainer": row.trainer,
                "price": row.price,
                "rating": round(row.avg_rating, 2)
            } for row in result
        ]

def fetch_quiz_info():
    query = """
    SELECT COUNT(*) FROM questions
    """
    with db_engine.connect() as conn:
        count = conn.execute(text(query)).fetchone()[0]
        return count


# Test the connection
if __name__ == "__main__":
    try:
        courses = fetch_courses()
        print("Courses:", courses)
    except Exception as e:
        print("Error fetching courses:", e)
