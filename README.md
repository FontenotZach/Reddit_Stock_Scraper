# Reddit_Stock_Scraper
Scrapes Reddit posts and streams new comments to track market trends.
Runs on most Linux distibutions

## Quick info:
  - Highly threaded reddit scraper which runs indefinitely and collects stock mention data from r/wallstreetbets, r/investing, r/stocks, and r/pennystocks
  
  - Optimized algorithm cleans comments to avoid use of slow regular expressions
  
  - Hardy to manipulation
  
  - Modular design allows new subs to be added with just a few lines of code
  
  - Optimized data storage unit which can store a year's worth of data in ~150 MB
  
  - Capable of processing ~600 thousand comments per hour on a Intel i7 8th gen processor
  
## Usage:
- To run standalone, simply run `$ python3 WSB_Scraper.py`
- For a safer, screen session, run `$ sh run.sh`
 - To create a Docker container:
	1. Run `# docker build -t reddit-scraper .` to build the Docker image.
	2. Create a folder 'Data' and change the ownership for the docker guest (UID:101,GID:101 (This can be found with the command `# docker run --rm reddit-scraper id wsb`)).
	3. Then run `# docker create --name reddit-scraper --mount type=bind,source="$(pwd)"/Data,target=/scraper/Data reddit-scraper:latest` to create a Docker container from the image.
	4. The container has been created, and can be started with `# docker run reddit-scraper`
	5. The container's status can be viewed with the command `# docker ps -a`, and the data is stored in the Data folder (step 2)
	6. The container can also be tested after building with the command `# docker run -it reddit-scraper`

## Development:
- This program is written in Python, and thus requires Python v3.8 or greater to be installed. Additionally, there are several python dependencies required for proper operation.

- Using a Python virtual environment (venv) is advised. This requires pip (pip3) to be installed.

- ***Debian-based Distros:***
    1. To install pip, run `# apt install python3-pip`
    2. Then, install the Python virtual environment with `$ pip3 install virtualenv`
    3. Ensure you are in the Reddit_Stock_Scraper folder. (the folder with this README!) 
    4. Next, create a new virtual environment in the current directory with `$ python3 -m venv .venv`
    5. Enter the environment with `$ source .venv/bin/activate`
    6. Finally, install all required modules with `$ pip3 install -r requirements.txt`
    
 - ***Alternative:***
    1. Install Docker (desktop, daemon, etc.)
    2. Start Docker
    3. Make changes, then use Docker instructions to run container

## Future plans:
  - Integrate robust algorithm to find trending tickers and report them
  
  - Integrate with dev website
  
  - Plug in to deep learning robo investor
  
  - Implement twitter and stockwits scraping
