using System.Buffers.Binary;
using System.Text;
var data=File.ReadAllBytes(args[0]);int p=0;
uint U32(byte[] d,ref int o){var v=BinaryPrimitives.ReadUInt32BigEndian(d.AsSpan(o,4));o+=4;return v;}
ulong U64(byte[] d,ref int o){var v=BinaryPrimitives.ReadUInt64BigEndian(d.AsSpan(o,8));o+=8;return v;}
string Str(byte[] d,ref int o){int e=Array.IndexOf(d,(byte)0,o);if(e<o||e-o>4096)throw new InvalidDataException();var v=Encoding.UTF8.GetString(d,o,e-o);o=e+1;return v;}
byte[] Decode(byte[] input,int size,int mode)
{
 if(size<0||size>256*1024*1024)throw new InvalidDataException("size");
 if(mode==0){if(input.Length!=size)throw new InvalidDataException();return input;}
 if(mode is not (2 or 3))throw new InvalidDataException("Compression "+mode);
 var output=new byte[size];int i=0,o=0;
 while(i<input.Length){int token=input[i++];int literal=token>>4;if(literal==15){int b;do{b=input[i++];literal+=b;}while(b==255);}input.AsSpan(i,literal).CopyTo(output.AsSpan(o,literal));i+=literal;o+=literal;if(i==input.Length)break;int offset=input[i]|input[i+1]<<8;i+=2;if(offset<=0||offset>o)throw new InvalidDataException("offset");int match=(token&15)+4;if((token&15)==15){int b;do{b=input[i++];match+=b;}while(b==255);}for(int n=0;n<match;n++)output[o+n]=output[o+n-offset];o+=match;}
 if(o!=size)throw new InvalidDataException("output size");return output;
}
if(Str(data,ref p)!="UnityFS")throw new InvalidDataException("not UnityFS");
var version=U32(data,ref p);var unity=Str(data,ref p);var revision=Str(data,ref p);var total=U64(data,ref p);int compressed=(int)U32(data,ref p),uncompressed=(int)U32(data,ref p);var flags=U32(data,ref p);
if(version>=7)p=(p+15)&~15;
int blockData=p;var infoPos=(flags&128)!=0?data.Length-compressed:p;
var info=Decode(data.AsSpan(infoPos,compressed).ToArray(),uncompressed,(int)(flags&63));
if((flags&128)==0)blockData+=compressed;
if((flags&512)!=0)blockData=(blockData+15)&~15;
int q=16;int blocks=(int)U32(info,ref q);if(blocks<0||blocks>65536)throw new InvalidDataException();
using var memory=new MemoryStream();
for(int n=0;n<blocks;n++){int us=(int)U32(info,ref q),cs=(int)U32(info,ref q);int bf=BinaryPrimitives.ReadUInt16BigEndian(info.AsSpan(q,2));q+=2;if(memory.Length+us>256*1024*1024)throw new InvalidDataException("aggregate limit");var decoded=Decode(data.AsSpan(blockData,cs).ToArray(),us,bf&63);memory.Write(decoded);blockData+=cs;}
var flat=memory.ToArray();int nodes=(int)U32(info,ref q);Console.WriteLine($"UnityFS version={version} nodes={nodes} bytes={flat.Length}");
for(int n=0;n<nodes;n++){var off=U64(info,ref q);var len=U64(info,ref q);var nf=U32(info,ref q);var path=Str(info,ref q);if(off+len>(ulong)flat.Length)throw new InvalidDataException();Console.WriteLine($"NODE {path} bytes={len}");}
// Search only this explicitly selected resource archive, not process memory.
if(args[1]=="bindings")
{
 var found=new SortedSet<string>();
 for(int i=0;i<flat.Length;i++)
 {int e=i;while(e<flat.Length && flat[e]>=32 && flat[e]<=126)e++;if(e-i>=8 && e-i<1024){var s=Encoding.ASCII.GetString(flat,i,e-i);foreach(System.Text.RegularExpressions.Match m in System.Text.RegularExpressions.Regex.Matches(s,@"(?:newsitem|[Ii]nduction)\.[A-Za-z0-9_.]+"))found.Add(m.Value);}i=e;}
 foreach(var s in found.Take(300))Console.WriteLine(s);return;
}
if(args[1].StartsWith("window:"))
{
 var fields=args[1].Split(':');int start=Convert.ToInt32(fields[1],16),length=Convert.ToInt32(fields[2],16);if(length>262144)throw new InvalidDataException("Window limit");
 for(int i=start;i<Math.Min(flat.Length,start+length);i++)
 {int e=i;while(e<flat.Length && e<start+length && flat[e]>=32 && flat[e]<=126)e++;if(e-i>=6)Console.WriteLine($"{i:X} "+Encoding.ASCII.GetString(flat,i,Math.Min(e-i,512)));i=e;}
 return;
}
var term=Encoding.ASCII.GetBytes(args[1]);int matches=0;
for(int n=0;n+term.Length<=flat.Length;n++)
 if(flat.AsSpan(n,term.Length).SequenceEqual(term))
 {int start=Math.Max(0,n-80),end=Math.Min(flat.Length,n+240);var excerpt=Encoding.UTF8.GetString(flat,start,end-start);Console.WriteLine($"MATCH {n:X} "+System.Text.Json.JsonSerializer.Serialize(excerpt));if(++matches>=40)break;}
if(args.Length>2)File.WriteAllBytes(args[2],flat);
