using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using System.Text;

if (args.Length < 2) throw new ArgumentException("Usage: FMAPI.PeProbe <trusted PE file> <RTTI fragment | xref hex-rva...>");
var bytes = File.ReadAllBytes(args[0]);
using var pe = new PEReader(new MemoryStream(bytes, writable: false));
var headers = pe.PEHeaders;
var imageBase = headers.PEHeader!.ImageBase;
Console.WriteLine($"SHA256 {Convert.ToHexString(SHA256.HashData(bytes))} ImageBase 0x{imageBase:X}");
int Rva(int offset)
{
    foreach (var s in headers.SectionHeaders)
        if (offset >= s.PointerToRawData && offset < s.PointerToRawData + s.SizeOfRawData)
            return offset - s.PointerToRawData + s.VirtualAddress;
    return -1;
}
int Offset(int rva)
{
    foreach (var s in headers.SectionHeaders)
        if (rva >= s.VirtualAddress && rva < s.VirtualAddress + s.SizeOfRawData)
            return rva - s.VirtualAddress + s.PointerToRawData;
    return -1;
}
var functions = new List<(int Begin, int End)>();
var exception = headers.PEHeader.ExceptionTableDirectory;
var exceptionOffset = Offset(exception.RelativeVirtualAddress);
if (exceptionOffset >= 0)
    for (var p = exceptionOffset; p + 12 <= exceptionOffset + exception.Size; p += 12)
        functions.Add((BitConverter.ToInt32(bytes, p), BitConverter.ToInt32(bytes, p + 4)));
functions.Sort((a,b) => a.Begin.CompareTo(b.Begin));
int Function(int rva)
{
    var low = 0; var high = functions.Count - 1;
    while (low <= high)
    {
        var mid = (low + high) / 2; var f = functions[mid];
        if (rva < f.Begin) high = mid - 1;
        else if (rva >= f.End) low = mid + 1;
        else return f.Begin;
    }
    return -1;
}
if (args[1] == "xref")
{
    var targets=args.Skip(2).Select(a=>Convert.ToInt32(a,16)).ToHashSet();
    foreach(var s in headers.SectionHeaders.Where(s=>(s.SectionCharacteristics & SectionCharacteristics.ContainsCode)!=0))
        for(var p=s.PointerToRawData;p+4<=s.PointerToRawData+s.SizeOfRawData;p++)
        {
            var source=Rva(p); var target=(long)source+4+BitConverter.ToInt32(bytes,p);
            if(target>=0 && target<=int.MaxValue && targets.Contains((int)target))
                Console.WriteLine($"XREF_CANDIDATE displacement=0x{source:X} function=0x{Function(source):X} target=0x{target:X}");
        }
    return;
}
var types = new Dictionary<int,string>();
for (var i = 16; i + 6 < bytes.Length; i++)
{
    if (bytes[i] != '.' || bytes[i+1] != '?' || bytes[i+2] != 'A' || (bytes[i+3] != 'V' && bytes[i+3] != 'U')) continue;
    var end = i;
    while (end < bytes.Length && end-i < 512 && bytes[end] is >= 32 and <= 126) end++;
    if (end == bytes.Length || bytes[end] != 0) continue;
    var name = Encoding.ASCII.GetString(bytes, i, end-i);
    if (name.Contains(args[1], StringComparison.OrdinalIgnoreCase))
    {
        var rva = Rva(i-16);
        types[rva] = name;
        Console.WriteLine($"TYPE 0x{rva:X} {name}");
    }
    i = end;
}
if (types.Count > 100) { Console.WriteLine("Too many types; narrow fragment before locating vtables."); return; }
var locators = new Dictionary<int,string>();
foreach (var s in headers.SectionHeaders.Where(s => (s.SectionCharacteristics & SectionCharacteristics.ContainsCode) == 0))
    for (var p = s.PointerToRawData; p + 24 <= s.PointerToRawData + s.SizeOfRawData; p += 4)
        if (BitConverter.ToInt32(bytes,p) == 1 && types.TryGetValue(BitConverter.ToInt32(bytes,p+12),out var name) && BitConverter.ToInt32(bytes,p+20) == Rva(p))
        { locators[Rva(p)] = name; Console.WriteLine($"COL 0x{Rva(p):X} {name}"); }
var tables = new Dictionary<int,string>();
foreach (var s in headers.SectionHeaders.Where(s => (s.SectionCharacteristics & SectionCharacteristics.ContainsCode) == 0))
    for (var p = s.PointerToRawData; p + 24 <= s.PointerToRawData + s.SizeOfRawData; p += 8)
    {
        var pointer = BitConverter.ToUInt64(bytes,p);
        if (pointer < imageBase || pointer-imageBase > int.MaxValue || !locators.TryGetValue((int)(pointer-imageBase),out var name)) continue;
        var table = Rva(p+8); tables[table] = name;
        var slots = Enumerable.Range(0,Math.Min(12,(s.PointerToRawData+s.SizeOfRawData-p-8)/8)).Select(k => BitConverter.ToUInt64(bytes,p+8+k*8)).Select(a => a >= imageBase ? $"0x{a-imageBase:X}" : "invalid");
        Console.WriteLine($"VTABLE 0x{table:X} {name} slots={string.Join(',',slots)}");
    }

// Candidate RIP-relative references only. A disassembler must confirm instruction boundaries.
foreach (var s in headers.SectionHeaders.Where(s => (s.SectionCharacteristics & SectionCharacteristics.ContainsCode) != 0))
    for (var p = s.PointerToRawData; p + 4 <= s.PointerToRawData+s.SizeOfRawData; p++)
    {
        var source = p-s.PointerToRawData+s.VirtualAddress;
        var target = (long)source+4+BitConverter.ToInt32(bytes,p);
        if (target <= int.MaxValue && target >= 0 && tables.TryGetValue((int)target,out var name))
            Console.WriteLine($"RIP_CANDIDATE displacement=0x{source:X} function=0x{Function(source):X} target=0x{target:X} {name}");
    }

