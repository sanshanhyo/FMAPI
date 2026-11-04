namespace FMAPI.Core.Tests;

public sealed class MessageDateTests
{
    [Theory]
    [InlineData(2024, 60, "2024-02-29")]
    [InlineData(2025, 60, "2025-03-01")]
    [InlineData(2024, 366, "2024-12-31")]
    [InlineData(2025, 366, null)]
    [InlineData(1900, 1, null)]
    [InlineData(2025, 0, null)]
    public void ExistingMessageEncodingPreservesCalendarAndSentinel(int year, int day, string? expected)
    {
        Assert.Equal(expected, GameDate.Decode(((uint)year << 16) | (uint)day));
    }

    [Fact]
    public void NonDayLowWordFlagsAreIgnoredByExistingDecoder()
    {
        Assert.Equal("2024-02-29", GameDate.Decode((2024u << 16) | 0xFE00 | 60));
        Assert.Null(GameDate.Decode(0));
    }
}
