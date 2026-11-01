using System.Diagnostics;
using System.Reflection.PortableExecutable;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

// Research diagnostic only. No game calls, injection, or write access.
try
{
    if (args.Length == 1 && args[0] == "--self-test")
    {
        if (Bounds.Count(16, 40, 48, 8, 8) != 3) throw new Exception("Count");
        foreach (var test in new Action[] {
            () => Bounds.Count(32,16,40,8,8), () => Bounds.Count(16,40,32,8,8),
            () => Bounds.Count(16,25,32,8,8), () => Bounds.Count(16,96,96,8,8) })
        { try { test(); } catch (InvalidDataException) { continue; } throw new Exception("Bounds accepted invalid vector"); }
        if (Text.Decode(new byte[]{3,0,0,0,0xE4,0xB8,0xAD,0}) != "\u4E2D") throw new Exception("UTF8");
        foreach (var sample in new byte[][] { [2,0,0,0,65,0], [1,0,0,0,0xFF,0], [1,0,0,0,65,66] })
        { try { Text.Decode(sample); } catch (Exception e) when(e is InvalidDataException or DecoderFallbackException) { continue; } throw new Exception("Invalid text accepted"); }
        Console.WriteLine("PASS: vector bounds and length-prefixed UTF-8 contracts");
        return 0;
    }
    if(args.Length != 2) throw new ArgumentException("Usage: FMAPI.MessageProbe <pid> <game_plugin.dll path>; or --self-test");
    if(!OperatingSystem.IsWindows()) throw new PlatformNotSupportedException("Windows only");
    using var probe = new Probe(int.Parse(args[0]), Path.GetFullPath(args[1]));
    Console.WriteLine(JsonSerializer.Serialize(probe.Capture(),new JsonSerializerOptions{WriteIndented=true}));
    return 0;
}
catch(Exception error)
{
    Console.Error.WriteLine(JsonSerializer.Serialize(new {status="unavailable",reason=error.Message}));
    return 3;
}

static class Bounds
{
    public static int Count(ulong begin,ulong end,ulong capacity,int stride,int maximum)
    {
        if(end<begin || capacity<end || capacity-begin>(ulong)maximum*(uint)stride || (end-begin)%(uint)stride!=0 || (capacity-begin)%(uint)stride!=0 || (begin==0 && capacity!=0))
            throw new InvalidDataException("Vector bounds failed");
        return checked((int)((end-begin)/(uint)stride));
    }
}
static class Text
{
    public static string Decode(byte[] data)
    {
        if(data.Length<5)throw new InvalidDataException("Truncated string");
        int length=BitConverter.ToInt32(data);
        if(length<0 || length>4096 || data.Length!=length+5 || data[^1]!=0)throw new InvalidDataException("String bounds failed");
        return new UTF8Encoding(false,true).GetString(data,4,length);
    }
}
sealed class Probe : IDisposable
{
    const string Hash="BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F";
    readonly Process process;
    readonly DateTime started;
    readonly IntPtr handle;
    readonly byte[] file;
    readonly PEReader pe;
    readonly ulong moduleBase;
    int budget=65536;
    public Probe(int pid,string path)
    {
        file=File.ReadAllBytes(path);
        if(Convert.ToHexString(SHA256.HashData(file))!=Hash)throw new InvalidDataException("Unsupported game binary hash");
        pe=new PEReader(new MemoryStream(file,false));
        process=Process.GetProcessById(pid);started=process.StartTime;
        var module=process.Modules.Cast<ProcessModule>().Single(m=>string.Equals(m.FileName,path,StringComparison.OrdinalIgnoreCase));
        moduleBase=(ulong)module.BaseAddress;
        handle=Native.OpenProcess(0x1010,false,pid);
        if(handle==IntPtr.Zero)throw new InvalidOperationException("Read-only process handle unavailable");
    }
    byte[] Read(ulong address,int size)
    {
        if(address==0 || size<0 || size>8192 || (budget-=size)<0)throw new InvalidDataException("Read budget/address rejected");
        if(process.HasExited || process.StartTime!=started)throw new InvalidOperationException("Process changed");
        var result=new byte[size];
        if(size>0 && (!Native.ReadProcessMemory(handle,(IntPtr)address,result,(nuint)size,out var count)||count!=(nuint)size))throw new InvalidOperationException("Read incomplete");
        return result;
    }
    ulong Pointer(ulong address)=>BitConverter.ToUInt64(Read(address,8));
    int Offset(int rva)
    {
        foreach(var s in pe.PEHeaders.SectionHeaders)
            if(rva>=s.VirtualAddress && (long)rva+24<=s.VirtualAddress+(long)s.SizeOfRawData)return rva-s.VirtualAddress+s.PointerToRawData;
        throw new InvalidDataException("RVA outside file-backed section");
    }
    string TypeName(ulong address)
    {
        var vt=Pointer(address);
        if(vt<moduleBase+8 || vt-moduleBase>int.MaxValue)throw new InvalidDataException("Vtable outside module");
        var col=BitConverter.ToUInt64(file,Offset((int)(vt-moduleBase)-8));var imageBase=pe.PEHeaders.PEHeader!.ImageBase;
        if(col<imageBase || col-imageBase>int.MaxValue)throw new InvalidDataException("Invalid RTTI locator");
        var name=Offset(BitConverter.ToInt32(file,Offset((int)(col-imageBase))+12))+16;
        if(name+512>file.Length)throw new InvalidDataException("RTTI name bounds");
        var end=Array.IndexOf(file,(byte)0,name,512);
        if(end<name)throw new InvalidDataException("RTTI name termination");
        return Encoding.ASCII.GetString(file,name,end-name);
    }
    public object Capture()
    {
        var root=Pointer(moduleBase+0x56F3008);var rootHeader=Read(root,0x30);
        if(BitConverter.ToUInt64(rootHeader)!=moduleBase+0x4E2D678 || TypeName(root)!=".?AVHUMAN_NON_PLAYER_MANAGER@@")throw new InvalidDataException("Human manager root mismatch");
        var begin=BitConverter.ToUInt64(rootHeader,0x18);
        var owners=Bounds.Count(begin,BitConverter.ToUInt64(rootHeader,0x20),BitConverter.ToUInt64(rootHeader,0x28),8,16);
        if(owners!=1)throw new InvalidDataException("Requires exactly one human manager; active owner selection is not implemented");
        var owner=Pointer(begin);var inbox=Pointer(owner+0x350);var inboxHeader=Read(inbox,24);
        var first=BitConverter.ToUInt64(inboxHeader);
        var count=Bounds.Count(first,BitConverter.ToUInt64(inboxHeader,8),BitConverter.ToUInt64(inboxHeader,16),8,32768);
        var take=Math.Min(count,32);var pointers=take==0?Array.Empty<byte>():Read(first,take*8);
        var messages=new List<object>();bool welcome=false;
        for(int i=0;i<take;i++)
        {
            var item=BitConverter.ToUInt64(pointers,i*8);var type=TypeName(item);var fields=Read(item+0x88,16);
            welcome |= type==".?AVWELCOME_TO_THE_CLUB_NEWS@@";
            messages.Add(new {idCandidate=BitConverter.ToInt32(fields,8),dateRaw=BitConverter.ToUInt32(fields),nativeType=type,title=(string?)null,body=(string?)null});
            if(!Read(item+0x88,16).SequenceEqual(fields))throw new InvalidOperationException("Message changed");
        }
        object? template=welcome?ReadWelcomeTemplate():null;
        if(Pointer(moduleBase+0x56F3008)!=root || !Read(root,0x30).SequenceEqual(rootHeader) || Pointer(begin)!=owner || Pointer(owner+0x350)!=inbox || !Read(inbox,24).SequenceEqual(inboxHeader) || (take>0 && !Read(first,take*8).SequenceEqual(pointers)))throw new InvalidOperationException("Inbox changed");
        return new {status="partial",scope="single-human-manager-associated-messages",count,returned=take,atomicSnapshot=false,messages,welcomeTitleTemplate=template,unsupported=new[]{"formatted title","body","decoded date","active owner in multiplayer"}};
    }
    object ReadWelcomeTemplate()
    {
        const uint id=0xABDAF;
        var root=Pointer(moduleBase+0x56F1C28);var impl=Pointer(root+8);var index=Read(impl+0x68,24);
        var start=BitConverter.ToUInt64(index);var count=Bounds.Count(start,BitConverter.ToUInt64(index,8),BitConverter.ToUInt64(index,16),16,2000000);
        int language=BitConverter.ToInt32(Read(impl+0x12C,4));int lo=0,hi=count;
        while(lo<hi){int mid=lo+(hi-lo)/2;var e=Read(start+(ulong)mid*16,16);uint key=BitConverter.ToUInt32(e);int variant=BitConverter.ToInt32(e,4);if(key<id || key==id && variant<language)lo=mid+1;else hi=mid;}
        if(lo==count)return new {status="unavailable",reason="template missing"};
        var entry=Read(start+(ulong)lo*16,16);
        if(BitConverter.ToUInt32(entry)!=id || BitConverter.ToInt32(entry,4)!=language)return new {status="unavailable",reason="exact language missing"};
        var value=BitConverter.ToUInt64(entry,8);if(value==0)return new {status="unavailable",reason="null template"};
        var header=Read(value,24);var vb=BitConverter.ToUInt64(header);
        var variants=Bounds.Count(vb,BitConverter.ToUInt64(header,8),BitConverter.ToUInt64(header,16),8,128);
        if(variants==0)return new {status="unavailable",reason="template not loaded; no game call attempted"};
        if(variants!=1)return new {status="unavailable",reason="multiple variants require selection semantics"};
        var variantObject=Pointer(vb);var partsHeader=Read(variantObject,24);var pb=BitConverter.ToUInt64(partsHeader);
        var parts=Bounds.Count(pb,BitConverter.ToUInt64(partsHeader,8),BitConverter.ToUInt64(partsHeader,16),8,16);
        var segments=new List<string>();
        for(int i=0;i<parts;i++)
        {
            var part=Pointer(pb+(ulong)i*8);var text=Pointer(part+8);int length=BitConverter.ToInt32(Read(text,4));
            if(length<0 || length>4096)throw new InvalidDataException("Text length limit");
            segments.Add(Text.Decode(Read(text,length+5)));
        }
        if(Pointer(moduleBase+0x56F1C28)!=root || Pointer(root+8)!=impl || !Read(impl+0x68,24).SequenceEqual(index) || BitConverter.ToInt32(Read(impl+0x12C,4))!=language || !Read(value,24).SequenceEqual(header) || Pointer(vb)!=variantObject || !Read(variantObject,24).SequenceEqual(partsHeader))throw new InvalidOperationException("Localization changed");
        return new {status="template-only",templateId=id,language,segments,parametersResolved=false};
    }
    public void Dispose(){Native.CloseHandle(handle);process.Dispose();pe.Dispose();}
}
static class Native
{
    [DllImport("kernel32.dll",SetLastError=true)] public static extern IntPtr OpenProcess(uint access,bool inherit,int pid);
    [DllImport("kernel32.dll",SetLastError=true)] public static extern bool ReadProcessMemory(IntPtr handle,IntPtr address,byte[] buffer,nuint size,out nuint read);
    [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr handle);
}
