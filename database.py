from psycopg2.extras import execute_values

CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls
(id SERIAL PRIMARY KEY, title TEXT, owner_username TEXT);"""
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options
(id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER, FOREIGN KEY(poll_id) REFERENCES polls (id));"""
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes
(username TEXT, option_id INTEGER, FOREIGN KEY(option_id) REFERENCES options (id));"""


SELECT_ALL_POLLS = "SELECT * FROM polls;"
SELECT_POLL_WITH_OPTIONS = """SELECT * FROM polls
JOIN options ON polls.id = options.poll_id
WHERE polls.id = %s;"""
SELECT_LASTEST_POLL = """SELECT * FROM polls
JOIN options ON polls.id = options.poll_id
WHERE polls.id = (
    SELECT id FROM polls ORDER BY id DESC LIMIT 1
);"""  #pas de ; at the end of a nested query
SELECT_RANDOM_VOTE = "SELECT id FROM votes WHERE option_id = %s ORDER BY RANDOM() LIMIT 1;"
SELECT_POLL_VOTE_DETAILS="""SELECT  
    option.id,
    option.option_text,
    COUNT(votes.option_id) AS vote_count #alias change the name of the colomn
    COUNT(votes.option_id) / SUM(COUNT(votes.option_id)) OVER() * 100.0 AS vote_percentage
    FROM options
    LEFT JOIN votes ON option.id = votes.option_id
    WHERE option.poll_id = 1 
    GROUP BY option.id;"""


INSERT_POLL_RETURN_ID = "INSERT INTO polls (title, owner_username) VALUES (%s, %s) RETURNING id;"
INSERT_OPTION = "INSERT INTO options (option_text, poll_id) VALUES %s;"
INSERT_VOTE = "INSERT INTO votes (username, option_id) VALUES (%s, %s);"


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_POLLS)
            cursor.execute(CREATE_OPTIONS)
            cursor.execute(CREATE_VOTES)


def get_polls(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_POLLS)
            return cursor.fetchall()


def get_latest_poll(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_LASTEST_POLL)
            return cursor.fetchall()


def get_poll_details(connection, poll_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_WITH_OPTIONS, (poll_id,))
            return cursor.fetchall()


def get_poll_and_vote_results(connection, poll_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_VOTE_DETAILS, (poll_id,))
            return cursor.fetchall()

def get_random_poll_vote(connection, option_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_RANDOM_VOTE, (option_id, ))
            return cursor.fetchone()

def create_poll(connection, title, owner, options):
    with connection:
        with connection.cursor() as cursor:
            # cursor.execute("INSERT INTO polls VALUES (%s, %s);" (title, owner))
            # cursor.execute("SELECT id FROM polls ORDER BY id DESC LIMIT 1;")
            cursor.execute(INSERT_POLL_RETURN_ID, (title, owner))
            
            poll_id = cursor.fetchone()[0]
            option_values = [(option_text, poll_id) for option_text in options]
            
            # for option_value in option_values:
            #     cursor.execute(INSERT_OPTION, option_values)
            execute_values(cursor, INSERT_OPTION, option_values)

def add_poll_vote(connection, username, option_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_VOTE, (username, option_id))