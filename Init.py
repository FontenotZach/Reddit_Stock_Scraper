import os

# /////////////////////////////////////////////////////////////////
#   Method: initialize
#   Purpose: Initializes the program by ensuring proper folder layout exists
# /////////////////////////////////////////////////////////////////
def initialize():

    # Set this to True to print whenever a folder/file is tested
    debug = True

    # Check for proper folder layout
    folders = ['Log', 'Data/hot', 'Data/stream']

    for folder in folders:
        if not os.path.isdir(folder):
            if debug:
                print(f'Creating folder {folder}.')

            os.makedirs(folder, mode=0o755, exist_ok=True)

    # Ensure we have write permissions in the necessary folders
    for folder in folders:
        # Create a temporary file in each folder
        name = os.path.join(folder, 'tmp')

        try:
            # Try to open it with write permissions, then delete it
            file = open(name, 'w')
            file.close()
            os.remove(name)

        except PermissionError as e:
            # If it fails because of permissions, exit with an error
            print(f'Permissions error: {e}.')
            exit(1);

        else:
            # Otherwise, print the success
            if debug:
                print(f'Successfully opened, closed, and deleted {name}.')

            pass

    return
