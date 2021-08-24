# Reddit Stock Scraper
Scrapes Reddit posts and streams new comments to track market trends.
Runs on most Linux distibutions

## Quick info:
  - Highly parallel reddit scraper which runs indefinitely and collects stock mention data from r/wallstreetbets, r/investing, r/stocks, and r/pennystocks
  
  - Optimized algorithm cleans comments to avoid use of slow regular expressions
  
  - Hardy to external manipulation
  
  - Modular design allows new subs to be added with just a single new string
  
  - Optimized SQL-based data storage system to allow advanced data analysis
  
  - Capable of processing ~600 thousand comments per hour on a Intel i7 8th gen processor
  
## Usage:
  This project requires Docker and Docker Compose.

  These are both installed with the Docker Desktop (Windows, MacOS), but must be installed individually on Linux.

  The configuration is primarily stored in the file `set-exports.sh` or `set-exports.ps1` for *nix and Windows, respectively. You should store your SQL password and PRAW credentials there.

  1. To use the configuration stored in the file, run `source ./set-exports.sh` on *nix or `.\set-exports.ps1` in Powershell on Windows. (Note: if you get a permissions error on Windows, you likely need to enable custom scripts with the command `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted -Force`. Note that this also allows all scripts downloaded from the internet to run, and so should be used with caution.)
  2. To verify, run `echo $PRAW_CLIENT_ID`. If your ID is printed to the screen, then the settings have been applied for this session.
  3. To create and run the containers, use `# docker-compose -f docker-compose-no-dev.yml up -d`
  4. To stop and remove the containers, use `# docker-compose -f docker-compose-no-dev.yml down`
  5. ***OPTIONAL:*** To also remove the persistent SQL database, instead use `# docker-compose -f docker-compose-no-dev.yml down --volumes` (WARNING: THIS WILL RESULT IN LOSS OF HISTORICAL TICKER DATA)

## Development:
  This program is written in Python, and thus requires Python v3.8 or greater to be installed. Additionally, there are several python dependencies required for proper operation.

  Using a Python virtual environment (venv) is advised. This requires pip (pip3) to be installed.

  ***Docker (Preferred):***
  1. Install and start Docker (desktop, daemon, etc.)
  2. Make changes, then build the Docker container with `# docker build -t reddit-scraper .`
  3. Modify the docker-compose file, changing `johnathanburns/reddit-scraper:latest` to `reddit-scraper:latest`
  4. Follow the Usage instructions to then run the containers

  ***Debian-based Distros:***
  1. To install pip, run ```# apt install python3-pip```
  2. Then, install the Python virtual environment with ```$ pip3 install virtualenv```
  3. Ensure you are in the Reddit_Stock_Scraper folder. (the folder with this README!) 
  4. Next, create a new virtual environment in the current directory with ```$ python3 -m venv .venv```
  5. Enter the environment with ```$ source .venv/bin/activate```
  6. Finally, install all required modules with ```$ pip3 install -r requirements.txt```
    
## Future plans:
  - Integrate robust algorithm to find trending tickers and report them
  
  - Integrate with dev website
  
  - Plug in to deep learning robo investor
  
  - Implement twitter and stockwits scraping
