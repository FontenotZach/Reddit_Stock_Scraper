# /////////////////////////////////////////////////////////////////
#   Method: storage_manager
#   Purpose: Manages file output
#   Inputs:
#           'tickers' - list of scraped tickers
#           'set' - the set the comments belong to
#               > TODO: convert to enum
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def storage_manager(tickers, set, sub_name):

    # Write each ticker score to appropriate SymbolDirectory
    for ticker in tickers:
        file_name = f'Data/{set}/{ticker.symbol}_data_{set}.csv'
        file_path = pathlib.Path(file_name)
        if file_path.exists():
            file = open(file_name, 'r')
        else:
            file = open(file_name, 'x')
            file.close()
            file = open(file_name, 'r')

        try:
            reader = csv.reader(file)
            values = list(reader)
            updated_values = []
            for value in values:
                updated_values.append(value[0])
            index = int(get_index())

            current_length = len(values)

            while len(updated_values) <= index:
                updated_values.append(0)

            updated_values[index] = float(updated_values[index]) + ticker.score
            #new_values = values[current_length:]
            file.close()
            file = open(file_name, 'w')
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(map(lambda x: [x], updated_values))

            file.close()

                #write_to_excel(tickers, set, sub_name)
            write_to_csv(tickers, set, sub_name)
        except:
            print(updated_values)
            raise Exception('Error in file I/O')
