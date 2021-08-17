import os
import datetime

# Set this to True to print whenever a folder/file is tested
debug = True

def p(s):
    if(debug):
        print(f'Init: {s}')

# /////////////////////////////////////////////////////////////////
#   Method: initialize
#   Purpose: Initializes the program by ensuring proper folder layout exists
# /////////////////////////////////////////////////////////////////
def initialize(subreddits):
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
