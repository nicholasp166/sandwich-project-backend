This originally was going to be a web app that lets people discuss sandwich combinations and rank them on a leaderboard. As of now this repo just has the backend, which has some webscraping and database connections made.

The backend was made using fastapi and python with libraries for MongoDB, Playwright, and BeautifulSoup4, I needed to webscrape the data from the publix website and store it. Something to take note of though they use "lazy loading" so my solution is kind of a hack to make sure I cover the entire page, but just one i never got that far.

Used to have have docker but started learning pm2 just to have a better tool for my personal use.
