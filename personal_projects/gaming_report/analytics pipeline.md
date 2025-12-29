# Gaming Analytics Pipeline (Work in Progress)
Goal: Achieve (almost) full automation, from playing to live Power BI Dashboard with minimal manual input.

current tech stack:
On-prem database: SQL Server
Visualisation: Power BI
ETL: Python, Power Query
Languages: Python, T-SQL, M and DAX

To be added in the future:
Power BI on-premises data gateway between Power BI Service and SQL Server (maybe?)

[​IMG]

Modelling the gaming industry

Terminologies.

Package: A package is an item/application sold on Steam with its own App ID. It can be a base game, a DLC, an expansion, a collection, a bundle etc

Collection: Bundle of multiple games sold under one Steam App ID, usually from the same series or developer.


Problem 1: Address the various types of games bundles, editions and collections.

A single title can have many DLCs, are these DLCs its own title or should they be classified part of the title? There are many versions (eg Ultimate edition, Gold edition etc) and future remaster of the same title. It can be bundled together as a collection, and different platform may sell different version of the same title etc

Type 1: True Collection (one Steam app ID for the collection only)

A True Collection (TC) is a package with multiple game titles, usually from the same series, with or without their expansions sold as a single Steam App ID. Buying individual titles with or without expansions is NOT possible. It requires only one single install and installs all the constituent game titles, it can be remastered.

Example: Mass Effect Legendary Edition, app ID 1328670, it contains three titles Mass Effect 1, 2 and 3 with all their DLC/expansion.

[​IMG]

If I simply input 1328670 and Mass Effect Legendary Edition and its related data such as relaese date, metacritic scores, developer into the Games table, I can only input data related to Mass Effect Legendary Edition as a collection. I won't have the granularity for its constituent games.

The issue becomes obvious, what if Mass Effect 1, 2 and 3 are made by different developer? What if I am only interested in playing say Mass Effect 2 because the other two are shit? I won't be able to aggregate Mass Effect's data because I only have data for the Legendary Edition. So my statistics will not be accurate.

So is it one game or three games? IMO, ME legendary is obviously three separate games, the constituent games data should override the Collection's data.

Solution
I created two tables, a Packages table, which has the Steam app ID as the primary key, which must be unique.


And I created an Expansions table, which is used to keep all DLC, expansions and constituent game titles that does not have its own Steam app ID.


Type 2: Pseudo Collection

Example: Halo: The Master Chief Collection


Type 3: True Full Editions

Example: Control Ultimate Edition

Type 4: Pseudo Full Editions

Problem 2: Calculating unit cost of each game.
