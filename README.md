# ao3-network-analysis

Fandom communities surrounding pieces of media are regularly generating and interacting with content and eachother online. One of the most prolific and widespread sources of interaction is the creation and consumption of fanfiction. Fanfiction is an untapped resource for analyses of fandom communities and internet culture. 

One of the main hubs of fanfiction is [Archive of our Own (AO3)](https://archiveofourown.org/). We intend to use data collected from this archive of fanfiction to gain a better understanding of fandom community and culture.

## Team
- [Emily Medema](https://github.com/emedema)
- [Tatiana Urazova](https://github.com/taturazova)

## Research Questions

- What is the nature of fanfiction?
- How does fanfiction relate to the fandom and the piece of media with which it originates?
- What makes a fandom? Are there common elements? What are they?
- What makes a character popular in a fandom? What makes a ship popular in a fandom?
- What effect does fandom have on the longevity of the show?
- What effect do fans have on a show? Is it good or bad?
- If someone likes one fandom, what is the probability they will like a different fandom? Common themes among them and works among them etc.
	
## Features

Due to AO3 not having an offical API, we scraped the data. There are three main marts we were looking for data on with multiple subparts. Using our scraper you can:

- Fandom Data Analysis
  - Tags
    - Most popular tags within a fandom, correlation between popularity of fics and tags, AU prevalence etc.
  - Characters
    - Most popular characters, tags associated with this character etc.
  - Ratings
    - Most popular ratings within fandoms (in association with its canon rating etc.)
  - Relationships
    - Most popular relationships, tags associated with this relationship, comparison of relationships for a singular character or between different pairings etc.
- Author Data Analysis
  - Most popular tags, pairings, fandoms etc.
  - Kudos, Bookmarks, Hits on fics etc.
  - Similarity between authors works and their bookmarks.
- Reader Data Analysis
  - Most popular tags, genre, fandom, pairing, rating etc.
  - Bookmarks vs. history
  - Most opened fic
  - Favourite author
  - and more...

## Graph Representation 

### Nodes
There are a lof of interesting nodes on AO3, these are the ones we will be looking into:
- Stories
- Tags
- Users
- Collections

#### Node Attributes
Some of the nodes have attributes associated with them.
Tags can be of the following types:
- Rating
- Warnings
- Category
- Relationship
- Character
- Fandom
- Freeform Tag

Stories have the following attributes:
- Crossover (boolean)
- Completion (boolean)
- Word count (integer)
- Date updated (date)
- Date Posted (date)
- Kudos (integer)
- Bookmarks (integer)
- Hits (integer)
- Title (string)
- Chapters (integer/integer:string)
- Chapter Titles (string)
- Comment Count (integer)
- Comments (strings)


### Edges
- Stories -> Fandom
- Stories -> Tag
- Users -> Stories
- Stories -> Collections
- Comments -> Users
- Comments -> Chapters
- Chapters -> Stories
