These are the back end functions that will data 
scarpe the deck lists and filter out the data to 
be stored in the database. This code will be 
copied over to AWS lambda functions that get 
called by cron jobs from an EC2 instance that
host a MongoDB database. 

The MongoDB will be the source of truth for an S3
bucket that contains the data for the most popular
pages. Caching the most popular page data in an S3
ensures scaleability for common pages. Less common
data can still be fetched and generated, it will 
be a different process. 
