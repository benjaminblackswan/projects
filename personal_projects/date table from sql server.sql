select *, right(EpYearName, 2) + 'F' + format(ceiling(WeekNoCurrentYear/2), '00') as FortnightLabel
from [Ben].[dbo].[DateTable]
where EpYearName = 2025
order by DateID
