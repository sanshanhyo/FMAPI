// Existing message-record date encoding; not a current-game-date detector.
static class GameDate
{
    public static string? Decode(uint raw)
    {
        int year=(int)(raw>>16),day=(int)(raw&0x1FF);
        if(year<1 || year>9999 || day<1 || day>(DateTime.IsLeapYear(year)?366:365) || year==1900 && day==1)return null;
        return new DateOnly(year,1,1).AddDays(day-1).ToString("yyyy-MM-dd",System.Globalization.CultureInfo.InvariantCulture);
    }
}
