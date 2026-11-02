using System.Text.Json;
using System.Text.Json.Nodes;

internal static class PositionCaptureDecoder
{
    public static void Write(string input,string output)
    {
        var inputPath=Path.GetFullPath(input);var outputPath=Path.GetFullPath(output);
        if(string.Equals(inputPath,outputPath,StringComparison.OrdinalIgnoreCase) || File.Exists(outputPath))throw new InvalidDataException("Use a new private output path; preserve original capture");
        foreach(var start in new[]{Directory.GetCurrentDirectory(),AppContext.BaseDirectory})
        {
            for(var dir=new DirectoryInfo(start);dir!=null;dir=dir.Parent)
                if(File.Exists(Path.Combine(dir.FullName,"FMAPI.slnx")) && outputPath.StartsWith(dir.FullName+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Decoded private data must remain outside repository");
        }
        if(new FileInfo(inputPath).Length>1024*1024)throw new InvalidDataException("Capture JSON size limit");
        var document=JsonNode.Parse(File.ReadAllText(inputPath))?.AsObject()??throw new InvalidDataException("Capture object missing");
        var result=document["result"]?.AsObject()??throw new InvalidDataException("Result missing");
        if(result["binarySha256"]?.GetValue<string>()!=PositionFields.NativeHash)throw new InvalidDataException("Unsupported capture binary profile");
        var records=result["positions"]?["records"]?.AsArray()??throw new InvalidDataException("Targeted UID position records missing");
        if(records.Count is <1 or >32)throw new InvalidDataException("Capture record count limit");
        foreach(var item in records)
        {
            var record=item?.AsObject()??throw new InvalidDataException("Malformed record");
            if(record["status"]?.GetValue<string>()!="available")continue;
            var extra=record["otherPositionSlotsRaw"];
            byte[] other=extra is JsonArray array?array.Select(node=>checked((byte)(node?.GetValue<int>()??throw new InvalidDataException("Null slot")))).ToArray():Convert.FromBase64String(extra?.GetValue<string>()??throw new InvalidDataException("Position slots missing"));
            if(other.Length!=14)throw new InvalidDataException("Need complete analyzed position block");
            var block=new byte[15];block[0]=checked((byte)record["goalkeeperFamiliarity"]!.GetValue<int>());other.CopyTo(block,1);
            record["positionFields"]=JsonSerializer.SerializeToNode(PositionFields.Decode(block));record["positionNamesVerified"]=true;
        }
        result["positionInterpretation"]=JsonSerializer.SerializeToNode(new{mode="offline interpretation of existing raw capture; no new process reads",nativeProfile=PositionFields.NativeHash,enumAssemblyProfile=PositionFields.AssemblyHash,enumMetadataProfile=PositionFields.MetadataHash,naturalThreshold=18,goalkeeperBusinessThreshold=15,reservedSlot151IncludedInMask=false});
        File.WriteAllText(outputPath,document.ToJsonString(new JsonSerializerOptions{WriteIndented=true}));
    }
}
