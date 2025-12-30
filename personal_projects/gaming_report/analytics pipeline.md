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


## Problem 1: Address the various types of games bundles, editions and collections.

A single title can have many DLCs, are these DLCs its own title or should they be classified part of the title? There are many versions (eg Ultimate edition, Gold edition etc) and future remaster of the same title. It can be bundled together as a collection, and different platform may sell different version of the same title etc

### Type 1: True Collection (one Steam ID for the collection only)

A True Collection (TC) is a package with multiple game titles, usually from the same game series, with or without their expansions sold as a single Steam App ID. Buying individual titles with or without expansions is NOT possible. It requires only one single install and installs all the constituent game titles, it can be remastered.

Example: Mass Effect Legendary Edition, app ID 1328670, it contains three titles Mass Effect 1, 2 and 3 with all their DLC/expansion.

<img width="371" height="146" alt="image" src="https://github.com/user-attachments/assets/a181da75-2f3d-407f-9be1-ecd8061f2c3b" />

If I simply input 1328670 and Mass Effect Legendary Edition and its related data such as relaese date, metacritic scores, developer into the Games table, I can only input data related to Mass Effect Legendary Edition as a collection. I won't have the granularity for its constituent games.

The issue becomes obvious, what if Mass Effect 1, 2 and 3 are made by different developer? What if I am only interested in playing say Mass Effect 2 because the other two are shit? I won't be able to aggregate Mass Effect's data because I only have data for the Legendary Edition. So my statistics will not be accurate.

So is it one game or three games? IMO, ME legendary is obviously three separate games, the constituent games data should override the Collection's data.

### Solution to True Collection

I created two tables, a **Packages table**, which lists all the packages with their Steam app ID as the primary key, which must be unique.
And I created an **Expansions table**, which is used to keep all DLC, expansions and constituent game that does not have its own Steam app ID.
I will add a letter after the Steam app ID to indicate this is an constituent game within a True Collection. I will also mark it as "Constiuent" in the Expansion Type column.
In this example, I list Mass Effect 1, 2 and 3 with 1328670A, 1328670B and 1328670C respectively.
These two tables are then loaded into Power BI and Merged using the Steam ID.

<img width="2004" height="308" alt="image" src="https://github.com/user-attachments/assets/49417279-97ab-4eb8-a01f-a308c2e90b52" />

Using the following M script, I create a new column called **Game Label**

```
= Table.AddColumn(
    #"Removed ID columns",
    "Game Label",
    each
        if [Expansion Type] = null then
            [Package Title]
        else if [Expansion Type] = "Constituent" then
            [Expansion Title]
        else
            Text.Combine({[Package Title], [Expansion Title]}, ": "),
    type text
)
```

I also created a new primary key column called **Game GUID**, based on the Steam app ID and the Expansion ID with the following script.

```
= Table.AddColumn(
    #"Expanded Expansions Table",
    "Game GUID",
    each if [Expansion ID] is null then [Steam ID] else [Expansion ID],
    type text
)
```

The end result in the Combined Games table in Power Query is

<img width="1153" height="226" alt="image" src="https://github.com/user-attachments/assets/d0666b44-64f4-4caf-83a6-f1640e0535c7" />

I am keeping both Package Label and Expansion Label as these can be used to control granularity.

Type 2: Pseudo Collection

Example: Halo: The Master Chief Collection


Type 3: True Full Editions

Example: Control Ultimate Edition

Type 4: Pseudo Full Editions

Problem 2: Calculating unit cost of each game.
