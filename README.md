# Reddit_Stock_Scraper
Scrapes Reddit posts and streams new comments to track market trends.
Runs on most Linux distibutions

Quick info:
  > Highly threaded reddit scraper which runs indefinitely and collects stock mention data from r/wallstreetbets, r/investing, r/stocks, and r/pennystocks
  
  > Optimized algorithm cleans comments to avoid use of slow regular expressions
  
  > Hardy to manipulation
  
  > Modular design allows new subs to be added with just a few lines of code
  
  > Optimized data storage unit which can store a year's worth of data in ~150 MB
  
  > Capable of processing ~600 thousand comments per hour on a Intel i7 8th gen processor
  
Usage:
  > To run standalone, simply run `$ python3 WSB_Scraper.py`
  > For a safer, screen session, run `$ sh run.sh`
  > To create a Docker container:
    > Run `# docker build --name reddit-scraper .` to build the Docker image
    > Then run `# docker create --name reddit-scraper` to create a Docker container from the image.
    > Logs and Data can be viewed with the command `# docker exec reddit-scraper cat [Data or Log]/[filename]`

Future plans:
  > Integrate robust algorithm to find trending tickers and report them
  
  > Integrate with dev website
  
  > Plug in to deep learning robo investor
  
  > Implement twitter and stockwits scraping
