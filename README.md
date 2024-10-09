These are the back end functions that data 
scarpe deck lists from TopDeck.gg

First the last 6 months of commander tournaments
gets fetched. Then this data is stored and filtered
be stored in the database. This code will be 
copied over to AWS lambda functions that get 
called by a React front-end to supply a json file
of card data to display.

The data includes MoxField links to cards played in
5 or less tournament decks of a given commander.
