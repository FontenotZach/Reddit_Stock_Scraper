# Reddit_Stock_Scraper
Scrapes WSB and Investing hot posts and streams new comments to track market trends.

Quick info:
  > Highly threaded reddit scraper which runs indefinitely and collects stock mention data from r/wallstreetbets and r/investing
  > Optimized algorithm cleans comments to avoid use of slow regular expressions
  > Hardy to manipulation (could be hardier though)
  > Modular design allows new subs to be added with just a few lines of code
  > Optimized data storage unit which can store a year's worth of data in ~150 MB
  > Capable of processing ~600 thousand comments per hour on a Intel i7 8th gen processor
  
 Future plans:
  > Build React dashboard to display data
  > Integrate algorithm to find trending tickers and report them
  > Integrate real time stock market data to overlay with mention data
  > Plug into deep learning robo investor
