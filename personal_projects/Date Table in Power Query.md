## updated 2025-11-02

sql
```
select *
, right(EpYear, 2) + 'F' + format(ceiling(WeekNoCurrentYear/2), '00') as FortnightLabel
, 'Week ' + cast(WeekNoCurrentYear as varchar(2)) as WeekNum
from [Ben].[dbo].[DateTable]
where EpYear = 2025
order by DateID
```


Dax
```
let
    Source = Sql.Database("legion", "Ben", [Query="select *#(lf), right(EpYear, 2) + 'F' + format(ceiling(WeekNoCurrentYear/2), '00') as FortnightLabel#(lf), 'Week ' + cast(WeekNoCurrentYear as varchar(2)) as WeekNum#(lf)from [Ben].[dbo].[DateTable]#(lf)where EpYear = 2025#(lf)order by DateID"]),
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Date", type date}, {"DateID", Int64.Type}, {"DaysBorn", Int64.Type}, {"EpYearID", Int64.Type}, {"EpYear", Int64.Type}, {"YearDayNumber", Int64.Type}, {"QuarterID", Int64.Type}, {"QuarterNoCurrentYear", Int64.Type}, {"QuarterDayNumber", Int64.Type}, {"FortnightID", Int64.Type}, {"FortnightDayNumber", Int64.Type}, {"WeekID", Int64.Type}, {"WeekNoCurrentYear", Int64.Type}, {"WeekdayNumber", Int64.Type}})
in
    #"Changed Type"
```
