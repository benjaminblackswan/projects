## updated 2025-11-02

### In Power Query

New Source > Blank Query

<img width="200" height="553" alt="image" src="https://github.com/user-attachments/assets/c84397d7-7858-4290-8ba3-7b31d2998554" />

Click **Advanced Editor**

<img width="401" height="159" alt="image" src="https://github.com/user-attachments/assets/7ba099ab-7672-415a-942f-9e02dc89ed89" />


Then paste in the following M code

```
let
    Source = Sql.Database("legion", "Ben", [Query="select *#(lf), right(EpYear, 2) + 'F' + format(ceiling(WeekNoCurrentYear/2), '00') as FortnightLabel#(lf), 'Week ' + cast(WeekNoCurrentYear as varchar(2)) as WeekNum#(lf)from [Ben].[dbo].[DateTable]#(lf)where EpYear = 2025#(lf)order by DateID"]),
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Date", type date}, {"DateID", Int64.Type}, {"DaysBorn", Int64.Type}, {"EpYearID", Int64.Type}, {"EpYear", Int64.Type}, {"YearDayNumber", Int64.Type}, {"QuarterID", Int64.Type}, {"QuarterNoCurrentYear", Int64.Type}, {"QuarterDayNumber", Int64.Type}, {"FortnightID", Int64.Type}, {"FortnightDayNumber", Int64.Type}, {"WeekID", Int64.Type}, {"WeekNoCurrentYear", Int64.Type}, {"WeekdayNumber", Int64.Type}}),
    #"Removed Columns" = Table.RemoveColumns(#"Changed Type",{"DateID", "DaysBorn"}),
    #"Sorted Rows" = Table.Sort(#"Removed Columns",{{"Date", Order.Ascending}})
in
    #"Sorted Rows"
```

Then rename the query to **Date Table**

<img width="161" height="278" alt="image" src="https://github.com/user-attachments/assets/2401e1cc-5443-431c-a058-8823b672bdd3" />
