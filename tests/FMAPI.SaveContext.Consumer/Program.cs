using FMAPI.Sdk;
var snapshot = new SaveContextSnapshot("s", "fixture", new DateOnly(2026, 1, 1), "m", "t", true);
var result = new SaveContextResult(Status: SaveContextStatus.Available, Reason: "fixture", Snapshot: snapshot);
var (status, reason, value) = result;
if (status != SaveContextStatus.Available || reason != "fixture" || value != snapshot) throw new Exception("contract");
Console.WriteLine("PASS: legacy binary constructor, properties and deconstruction on " + System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription);
