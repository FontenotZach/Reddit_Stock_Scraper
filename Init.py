import os
import psycopg2 as psql

from Util import get_sql_config

# Set this to True to print whenever a folder/file is tested
debug = True

# /////////////////////////////////////////////////////////////////
#   Method: p
#   Purpose: Print something only when debug is set to True
# /////////////////////////////////////////////////////////////////
def p(s):
    if(debug):
        print(f'Init: {s}')


# /////////////////////////////////////////////////////////////////
#   Method: initialize
#   Purpose: Initializes the program by ensuring proper folder layout exists
# /////////////////////////////////////////////////////////////////
def initialize(subreddits):

    test_db_connection(subreddits, get_sql_config())
    #test_file_permissions(subreddits)
    return


# /////////////////////////////////////////////////////////////////
#   Method: test_db
#   Purpose: Ensures all database tables exist on the remote database
# /////////////////////////////////////////////////////////////////
def test_db_connection(subreddits, config):
    #TODO: Move these into a seperate program configuration header
    table_check = '''
    SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE  table_schema = 'public'
    AND    table_name   = '{}'
    );
    '''

    table_create = '''
    CREATE TABLE {} (
    time_ticker_identifier VARCHAR(20) PRIMARY KEY,
    score FLOAT
    );
    '''

    # Build a list of tuples with the necessary SQL commands to create all tables
    command_pairs = []
    for sub in subreddits:
        table_name = f'{sub}_hot'
        command_pairs.append( (table_name, table_check.format(table_name), table_create.format(table_name)) )
        table_name = f'{sub}_stream'
        command_pairs.append( (table_name, table_check.format(table_name), table_create.format(table_name)) )
    
    conn = None
    try:
        p(f'Connecting to SQL server with options: {config}')
        conn = psql.connect(**config)
        cur = conn.cursor()

        # Create all necessary tables
        for command_pair in command_pairs:
            cur.execute(command_pair[1])
            exists = cur.fetchone()[0]

            # Check if a table exists, and if not create it
            if exists:
                p(f'Table {command_pair[0]} exists')
            else:
                p(f'Table {command_pair[0]} does not exist, creating')
                cur.execute(command_pair[2])

        conn.commit()
    except Exception as e:
        p(f'ERROR: {e}')
        exit(1)
    finally:
        if conn is not None:
            conn.close()

    return


# /////////////////////////////////////////////////////////////////
# Method: test_files
# Purpose: Ensures proper folder layout exists
# /////////////////////////////////////////////////////////////////
def test_file_permissions(subreddits):
    # Check for proper folder layout
    full_folders = []
    folders = ['Data/hot', 'Data/stream']

    # Create a seperate folder for each subreddit
    for folder in folders:
        for subreddit in subreddits:
            full_folders.append(f'{folder}/{subreddit}')

    # Then test each folder
    for folder in full_folders:
        # Ensure all the folders exist
        if not os.path.isdir(folder):
            p(f'Creating folder {folder}.')

            os.makedirs(folder, mode=0o755, exist_ok=True)
        
        # Ensure we have write permissions in the necessary folders
        # Create a temporary file in each folder
        name = os.path.join(folder, 'tmp')

        try:
            # Try to open it with write permissions, then delete it
            f = open(name, 'w')
            f.close()
            os.remove(name)

        except PermissionError as e:
            # If it fails because of permissions, exit with an error
            print(f'Permissions error: {e}.')
            exit(1);

        else:
            # Otherwise, print the success
            p(f'Successfully opened, closed, and deleted {name}')
            pass
    
    # Check that there's a starting date/timestamp file
    # If not, then create it
    name = 'Data/start'
    if not os.path.isfile(name):
        p(f'Creating timestamp file {name}')
        f = open(name, 'x')
        f.close()

    return
