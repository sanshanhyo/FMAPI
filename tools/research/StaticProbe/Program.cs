using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using System.Text;
using System.Reflection.Metadata;

if (args.Length < 2) throw new ArgumentException("Usage: StaticProbe <PE file> <RTTI name fragment>");
var bytes = File.ReadAllBytes(args[0]);
using var pe = new PEReader(new MemoryStream(bytes, writable: false));
var headers = pe.PEHeaders;
var imageBase = headers.PEHeader!.ImageBase;
Console.WriteLine($"SHA256 {Convert.ToHexString(SHA256.HashData(bytes))} ImageBase 0x{imageBase:X}");
if(args[1]=="map")
{
 var md=pe.GetMetadataReader();var wanted=new Dictionary<int,string>();
 foreach(var th in md.TypeDefinitions){var t=md.GetTypeDefinition(th);var tn=md.GetString(t.Namespace)+"."+md.GetString(t.Name);if(!tn.Contains(args[2],StringComparison.OrdinalIgnoreCase))continue;foreach(var mh in t.GetMethods()){var m=md.GetMethodDefinition(mh);wanted[System.Reflection.Metadata.Ecma335.MetadataTokens.GetToken(mh)]=tn+"."+md.GetString(m.Name);}}
 var map=File.ReadAllBytes(Path.Combine(Path.GetDirectoryName(args[0])!,"MethodAddressToToken.db"));
 if(BitConverter.ToInt32(map)!=0x4D544D55 || BitConverter.ToInt32(map,4)!=1)throw new InvalidDataException("Map version");
 int ac=BitConverter.ToInt32(map,8),mc=BitConverter.ToInt32(map,12),start=BitConverter.ToInt32(map,16),assembly=-1;
 using var br=new BinaryReader(new MemoryStream(map));br.BaseStream.Position=20;
 for(int i=0;i<ac;i++){var an=br.ReadString();if(an.Split(',')[0]==Path.GetFileNameWithoutExtension(args[0]))assembly=i;}
 if(assembly<0)throw new InvalidDataException("Map assembly absent");
 for(int i=0;i<mc;i++){int v=start+mc*8+i*8;if(BitConverter.ToInt32(map,v+4)==assembly && wanted.TryGetValue(BitConverter.ToInt32(map,v),out var name))Console.WriteLine($"NATIVE_RVA 0x{BitConverter.ToInt64(map,start+i*8):X} {name}");}
 return;
}
if(args[1]=="managed")
{
 var md=pe.GetMetadataReader();
 foreach(var th in md.TypeDefinitions)
 {
  var t=md.GetTypeDefinition(th);var tn=md.GetString(t.Namespace)+"."+md.GetString(t.Name);
  foreach(var fh in t.GetFields())
  {
   var f=md.GetFieldDefinition(fh);var name=md.GetString(f.Name);
   if(!name.Contains(args[2],StringComparison.OrdinalIgnoreCase))continue;
   string constant="";var ch=f.GetDefaultValue();if(!ch.IsNil){var c=md.GetConstant(ch);constant=Convert.ToHexString(md.GetBlobBytes(c.Value));}
   Console.WriteLine($"FIELD {tn}.{name} constant={constant}");
  }
  foreach(var mh in t.GetMethods()){var m=md.GetMethodDefinition(mh);var name=md.GetString(m.Name);if(name.Contains(args[2],StringComparison.OrdinalIgnoreCase))Console.WriteLine($"METHOD {tn}.{name} rva={m.RelativeVirtualAddress:X}");}
 }
 return;
}
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
if (args[1] is "live-header" or "live-inbox" or "live-text")
{
    if(Convert.ToHexString(SHA256.HashData(bytes))!="BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F") throw new InvalidOperationException("Unsupported binary");
    var process=System.Diagnostics.Process.GetProcessById(int.Parse(args[2]));
    var started=process.StartTime;
    var module=process.Modules.Cast<System.Diagnostics.ProcessModule>().Single(m=>string.Equals(m.FileName,Path.GetFullPath(args[0]),StringComparison.OrdinalIgnoreCase));
    var moduleBase=(ulong)module.BaseAddress;
    var handle=Native.OpenProcess(0x1010,false,process.Id);
    if(handle==IntPtr.Zero) throw new InvalidOperationException("Read handle failed");
    try
    {
        byte[] Read(ulong address,int count)
        {
            if(process.HasExited || process.StartTime!=started) throw new InvalidOperationException("Process changed");
            var data=new byte[count];
            if(!Native.ReadProcessMemory(handle,(IntPtr)address,data,(nuint)count,out var read)||read!=(nuint)count) throw new InvalidOperationException("Read failed");
            return data;
        }
        var pointer=BitConverter.ToUInt64(Read(moduleBase+0x56F2478,8));
        ulong PointerForProbe(ulong address)=>BitConverter.ToUInt64(Read(address,8));
        string TypeName(ulong objectAddress)
        {
            var vt=BitConverter.ToUInt64(Read(objectAddress,8));
            if(vt<moduleBase || vt-moduleBase>int.MaxValue)throw new InvalidOperationException("Vtable outside module");
            var vo=Offset((int)(vt-moduleBase)-8);if(vo<0)throw new InvalidOperationException("Vtable not backed");
            var col=BitConverter.ToUInt64(bytes,vo);if(col<imageBase || col-imageBase>int.MaxValue)throw new InvalidOperationException("Invalid locator");
            var co=Offset((int)(col-imageBase));if(co<0)throw new InvalidOperationException("Invalid locator RVA");
            var no=Offset(BitConverter.ToInt32(bytes,co+12))+16;
            if(no<16 || no+512>bytes.Length)throw new InvalidOperationException("Invalid type name");
            var ne=Array.IndexOf(bytes,(byte)0,no,512);if(ne<no)throw new InvalidOperationException("Invalid type name termination");
            return Encoding.ASCII.GetString(bytes,no,ne-no);
        }
        if(args[1]=="live-text")
        {
            var loc=BitConverter.ToUInt64(Read(moduleBase+0x56F1C28,8));
            var impl=BitConverter.ToUInt64(Read(loc+8,8));
            var bounds=Read(impl+0x68,24);var tb=BitConverter.ToUInt64(bounds);var te=BitConverter.ToUInt64(bounds,8);var tc=BitConverter.ToUInt64(bounds,16);
            var lang=BitConverter.ToInt32(Read(impl+0x12C,4));
            if(te<tb || tc<te || tc-tb>2000000*16 || (te-tb)%16!=0)throw new InvalidOperationException("Text index bounds");
            Console.WriteLine($"Localization entries={(te-tb)/16} language={lang}");foreach(var slot in new ulong[]{0xD8,0xE0}){var source=PointerForProbe(impl+slot);if(source!=0){Console.WriteLine($"Source {slot:X} type={TypeName(source)} header={Convert.ToHexString(Read(source,96))}"); if(TypeName(source)==".?AVSEGMENT_INPUT_STREAM@sicore@@"){var inner=PointerForProbe(source+0x18); if(inner!=0){Console.WriteLine($"Underlying type={TypeName(inner)} header={Convert.ToHexString(Read(inner,96))}");if(TypeName(inner)==".?AVZSTD_SEEKABLE_INPUT_STREAM@sicompression@@"){var backing=PointerForProbe(inner+0x18);Console.WriteLine($"Compressed backing type={TypeName(backing)} header={Convert.ToHexString(Read(backing,96))}");if(TypeName(backing)==".?AVSEGMENT_INPUT_STREAM@sicore@@"){var file=PointerForProbe(backing+0x18);Console.WriteLine($"Archive backing type={TypeName(file)} header={Convert.ToHexString(Read(file,96))}");}}}}}}
            foreach(uint id in new uint[]{0xA2A90,0xABDAF,0xA94A2})
            {
                ulong lo=0,hi=(te-tb)/16;
                while(lo<hi){var mid=(lo+hi)/2;var ent=Read(tb+mid*16,16);var key=BitConverter.ToUInt32(ent);var variant=BitConverter.ToInt32(ent,4);if(key<id || key==id && variant<lang)lo=mid+1;else hi=mid;}
                if(lo==(te-tb)/16){Console.WriteLine($"Text {id:X} not present");continue;}
                var match=Read(tb+lo*16,16);
                if(BitConverter.ToUInt32(match)!=id || BitConverter.ToInt32(match,4)!=lang){Console.WriteLine($"Text {id:X} no exact language entry");continue;}
                var value=BitConverter.ToUInt64(match,8);if(value==0){Console.WriteLine("Null text entry");continue;}
                var th=Read(value,24);var sb=BitConverter.ToUInt64(th);var se=BitConverter.ToUInt64(th,8);var sc=BitConverter.ToUInt64(th,16);
                Console.WriteLine($"Text {id:X} header={Convert.ToHexString(th)}");
                if(sb!=0 && se>=sb && sc>=se && sc-sb<=1024 && (se-sb)%8==0 && se>sb)
                {
                    var sp=BitConverter.ToUInt64(Read(sb,8));
                    if(sp!=0)
                    {
                        var sh=Read(sp,32);Console.WriteLine($"Text candidate {id:X} bytes={Convert.ToHexString(sh)}");
                        var pb=BitConverter.ToUInt64(sh);var pend=BitConverter.ToUInt64(sh,8);var pcap=BitConverter.ToUInt64(sh,16);
                        if(pb!=0 && pend>=pb && pcap>=pend && pcap-pb<=128 && (pend-pb)%8==0)
                        {
                            var parts=Read(pb,(int)(pend-pb));
                            for(var q=0;q<parts.Length;q+=8){var part=BitConverter.ToUInt64(parts,q);if(part!=0){var ph=Read(part,32);Console.WriteLine($"Part{q/8}={Convert.ToHexString(ph)}");var chars=BitConverter.ToUInt64(ph,8);if(chars!=0){var len=BitConverter.ToInt32(Read(chars,4));if(len<0||len>4096)throw new InvalidOperationException("String length");var cb=Read(chars+4,len+1);if(cb[len]!=0)throw new InvalidOperationException("String terminator");Console.WriteLine($"Template segment {q/8}="+new UTF8Encoding(false,true).GetString(cb,0,len));}}}
                        }
                    }
                }
            }
            if(!Read(impl+0x68,24).SequenceEqual(bounds))throw new InvalidOperationException("Text index changed");
            return;
        }
        if(args[1]=="live-inbox")
        {
            var ownerRoot=BitConverter.ToUInt64(Read(moduleBase+0x56F3008,8));
            Console.WriteLine("Owner root type="+TypeName(ownerRoot));
            var oh=Read(ownerRoot,0x30);
            if(BitConverter.ToUInt64(oh)!=moduleBase+0x4E2D678)throw new InvalidOperationException("Unexpected owner root");
            var ob=BitConverter.ToUInt64(oh,0x18);var oe=BitConverter.ToUInt64(oh,0x20);var oc=BitConverter.ToUInt64(oh,0x28);
            if(oe<ob || oc<oe || oc-ob>16*8 || (oe-ob)%8!=0)throw new InvalidOperationException("Owner vector bounds");
            Console.WriteLine("Owner count="+(oe-ob)/8);
            if(oe==ob)return;
            var owner=BitConverter.ToUInt64(Read(ob,8));Console.WriteLine($"First owner vtable RVA=0x{BitConverter.ToUInt64(Read(owner,8))-moduleBase:X}");
            var inbox=BitConverter.ToUInt64(Read(owner+0x350,8));
            var ih=Read(inbox,24);var ib=BitConverter.ToUInt64(ih);var ie=BitConverter.ToUInt64(ih,8);var ic=BitConverter.ToUInt64(ih,16);
            if(ie<ib || ic<ie || ic-ib>32768*8 || (ie-ib)%8!=0)throw new InvalidOperationException("Inbox vector bounds");
            Console.WriteLine("Owner inbox candidate count="+(ie-ib)/8);
            var ip=Read(ib,(int)Math.Min(ie-ib,8*3)); if(ip.Length>0){var welcome=BitConverter.ToUInt64(ip);var team=PointerForProbe(welcome+0xA0);Console.WriteLine("Welcome relation header="+Convert.ToHexString(Read(team,96)));try{Console.WriteLine("Relation type="+TypeName(team));var club=PointerForProbe(team+0x30);Console.WriteLine("Club type="+TypeName(club));var name=PointerForProbe(club+0xC8);var size=BitConverter.ToInt32(Read(name,4));if(size>=0&&size<=256){var nameBytes=Read(name+4,size);Console.WriteLine("Club short name JSON="+System.Text.Json.JsonSerializer.Serialize(new UTF8Encoding(false,true).GetString(nameBytes)));}}catch(InvalidOperationException){Console.WriteLine("Relation uses non-RTTI database layout");}}
            for(var n=0;n<ip.Length;n+=8){var it=BitConverter.ToUInt64(ip,n);Console.WriteLine($"Owned[{n/8}] type={TypeName(it)} id={BitConverter.ToInt32(Read(it+0x90,4))} dateRaw={BitConverter.ToUInt32(Read(it+0x88,4)):X}");}
            if(!Read(inbox,24).SequenceEqual(ih)||!Read(ownerRoot,0x30).SequenceEqual(oh))throw new InvalidOperationException("Ownership changed");
            return;
        }
        if(pointer==0) {Console.WriteLine("Manager unavailable");return;}
        var header=Read(pointer,0x1D8);
        if(BitConverter.ToUInt64(header)!=moduleBase+0x4CD7A58 || BitConverter.ToUInt64(header,8)!=moduleBase+0x4CD7A68) throw new InvalidOperationException("Manager type mismatch");
        Console.WriteLine("Manager type confirmed; bounded header only");
        for(var k=0x120;k<0x1D8;k+=8) Console.WriteLine($"field+{k:X}=0x{BitConverter.ToUInt64(header,k):X}");
        var begin=BitConverter.ToUInt64(header,0x120);var end=BitConverter.ToUInt64(header,0x128);var capacity=BitConverter.ToUInt64(header,0x130);
        if(begin==0 || end<begin || capacity<end || capacity-begin>8*100000 || (end-begin)%8!=0) throw new InvalidOperationException("Invalid bounded vector");
        Console.WriteLine($"Candidate vector count={(end-begin)/8}");
        var items=Read(begin,(int)Math.Min(end-begin,24));
        for(var i=0;i<items.Length;i+=8)
        {
            var item=BitConverter.ToUInt64(items,i);if(item==0)continue;
            var itemHeader=Read(item,0xA0);var vtable=BitConverter.ToUInt64(itemHeader);
            if(vtable<moduleBase || vtable-moduleBase>int.MaxValue) throw new InvalidOperationException("Item vtable outside module");
            var vtableRva=(int)(vtable-moduleBase);var locatorOffset=Offset(vtableRva-8);
            var locator=(int)(BitConverter.ToUInt64(bytes,locatorOffset)-imageBase);
            var typeRva=BitConverter.ToInt32(bytes,Offset(locator)+12);var nameOffset=Offset(typeRva)+16;
            var nameEnd=Array.IndexOf(bytes,(byte)0,nameOffset,512);
            Console.WriteLine($"item[{i/8}] type={Encoding.ASCII.GetString(bytes,nameOffset,nameEnd-nameOffset)} vtableRva=0x{vtableRva:X} candidateId={BitConverter.ToInt32(itemHeader,0x90)}");
            for(var k=8;k<0x90;k+=8) Console.WriteLine($" item+{k:X}=0x{BitConverter.ToUInt64(itemHeader,k):X}");
            if(i==0)
            {
                var payload=BitConverter.ToUInt64(itemHeader,0x80);
                if(payload!=0)
                {
                    var payloadHead=Read(payload,64);
                    Console.WriteLine($"Uninterpreted payload header={Convert.ToHexString(payloadHead)}");
                    var payloadVtable=BitConverter.ToUInt64(payloadHead);
                    if(payloadVtable>=moduleBase && payloadVtable-moduleBase<int.MaxValue)
                    {
                        var po=Offset((int)(payloadVtable-moduleBase)-8);
                        if(po>=0)
                        {
                            var col=BitConverter.ToUInt64(bytes,po);
                            if(col>=imageBase && col-imageBase<int.MaxValue && Offset((int)(col-imageBase)) is var co && co>=0)
                            {
                                var td=Offset(BitConverter.ToInt32(bytes,co+12))+16;
                                if(td>=16 && td+512<bytes.Length){var te=Array.IndexOf(bytes,(byte)0,td,512);if(te>=td) Console.WriteLine("Payload type="+Encoding.ASCII.GetString(bytes,td,te-td));}
                            }
                        }
                    }
                }
            }
        }
        var after=Read(pointer+0x120,24);
        if(!after.SequenceEqual(header.AsSpan(0x120,24).ToArray()))throw new InvalidOperationException("Vector changed");
        if(BitConverter.ToUInt64(Read(moduleBase+0x56F2478,8))!=pointer) throw new InvalidOperationException("Manager changed");
    }
    finally{Native.CloseHandle(handle);}
    return;
}
if(args[1]=="findhex")
{
 var term=Convert.FromHexString(args[2]);int pos=0,count=0;while(pos<bytes.Length){int n=bytes.AsSpan(pos).IndexOf(term);if(n<0)break;pos+=n;Console.WriteLine($"MATCH RVA=0x{Rva(pos):X} function=0x{Function(Rva(pos)):X}");pos+=term.Length;if(++count==40)break;}return;
}
if(args[1]=="find")
{
 foreach(var encoding in new[]{Encoding.UTF8,Encoding.Unicode})
 {var term=encoding.GetBytes(args[2]);int pos=0,count=0;while(pos<bytes.Length){int n=bytes.AsSpan(pos).IndexOf(term);if(n<0)break;pos+=n;Console.WriteLine($"MATCH encoding={encoding.WebName} RVA=0x{Rva(pos):X}");pos+=term.Length;if(++count==40)break;}}
 return;
}
if(args[1]=="strings")
{
 int found=0;
 for(int i=0;i<bytes.Length;i++)
 {int e=i;while(e<bytes.Length && bytes[e]>=32 && bytes[e]<=126)e++;if(e-i>=args[2].Length && e-i<512){var s=Encoding.ASCII.GetString(bytes,i,e-i);if(s.Contains(args[2],StringComparison.OrdinalIgnoreCase)){Console.WriteLine($"STRING 0x{Rva(i):X} {s}");if(++found>=40)break;}}i=e;}
 return;
}
if(args[1]=="vtable")
{
    var table=Convert.ToInt32(args[2],16);var off=Offset(table);
    for(var k=0;k<80;k++)
    {
        var va=BitConverter.ToUInt64(bytes,off+8*k);
        if(va<imageBase || va-imageBase>int.MaxValue)break;
        var rv=(int)(va-imageBase);
        if(!headers.SectionHeaders.Any(s=>(s.SectionCharacteristics&SectionCharacteristics.ContainsCode)!=0 && rv>=s.VirtualAddress && rv<s.VirtualAddress+s.SizeOfRawData))break;
        Console.WriteLine($"slot+{8*k:X}=0x{rv:X}");
    }
    return;
}
if (args[1] is "disasm" or "range")
{
    foreach (var arg in args[1]=="range"?args.Skip(2).Take(1):args.Skip(2))
    {
        var start = Convert.ToInt32(arg,16);
        var f = functions.FirstOrDefault(f => f.Begin == start);
        var length = f.End > start ? Math.Min(f.End-start,262144) : 256;
        if(args[1]=="range")length=Math.Min(Convert.ToInt32(args[3],16),65536);
        var decoder = Iced.Intel.Decoder.Create(64,new Iced.Intel.ByteArrayCodeReader(bytes,Offset(start),length));
        decoder.IP = imageBase+(uint)start;
        var formatter = new Iced.Intel.IntelFormatter();
        var output = new DisassemblyOutput();
        Console.WriteLine($"FUNCTION 0x{start:X} length {length}");
        while (decoder.IP < imageBase+(uint)start+(uint)length)
        {
            decoder.Decode(out var instruction);
            output.Value.Clear(); formatter.Format(instruction,output);
            Console.WriteLine($"{instruction.IP-imageBase:X}: {output.Value}");
        }
    }
    return;
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

sealed class DisassemblyOutput : Iced.Intel.FormatterOutput
{
    public StringBuilder Value { get; } = new();
    public override void Write(string text,Iced.Intel.FormatterTextKind kind) => Value.Append(text);
}
static class Native
{
    [System.Runtime.InteropServices.DllImport("kernel32.dll",SetLastError=true)] public static extern IntPtr OpenProcess(uint access,bool inherit,int pid);
    [System.Runtime.InteropServices.DllImport("kernel32.dll",SetLastError=true)] public static extern bool ReadProcessMemory(IntPtr handle,IntPtr address,byte[] buffer,nuint size,out nuint read);
    [System.Runtime.InteropServices.DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr handle);
}
