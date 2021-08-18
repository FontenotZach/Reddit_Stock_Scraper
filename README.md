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
  - This project requires Docker and Docker Compose.

  - These are both installed with the Docker Desktop (Windows, MacOS), but must be installed individually on Linux.

  - The container must first be built with `# docker build -t reddit-scraper .`

  - To run, simply use `# SQL_PASSWORD='[YOUR UNIQUE PASSWORD]' docker-compose up -d`, where [YOUR UNIQUE PASSWORD] is the password to use for the SQL server, in this case postgresql.

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
