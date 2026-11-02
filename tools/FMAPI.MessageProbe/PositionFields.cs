// Original research decoder. Not an SDK contract. Applies only to the pinned native profile.
internal sealed record PositionFamiliarity(string code,string nativeName,int playerOffset,uint maskBit,byte value,bool natural);
internal sealed record DecodedPositionFields(PositionFamiliarity[] familiarities,uint naturalPositionMask,string[] naturalPositionCodes,byte unusedSlot151Raw,bool businessRuleIsGoalkeeper);
internal static class PositionFields
{
    public const string NativeHash="BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F";
    public const string AssemblyHash="820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A";
    public const string MetadataHash="A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C";
    // Byte order comes from native mask table RVA 0x4D36ACC and loop 0x499AEB0.
    // Names/bits are independently paired with the pinned metadata PositionMask enum.
    static readonly (int Index,string Code,string Name,uint Bit)[] Mapping={
        (0,"GK","Goalkeeper",0x1),(2,"DL","DefenderLeft",0x8),
        (3,"DC","DefenderCentre",0x10),(4,"DR","DefenderRight",0x4),
        (5,"DM","DefensiveMidfielderCentre",0x80),(6,"ML","MidfielderLeft",0x200),
        (7,"MC","MidfielderCentre",0x400),(8,"MR","MidfielderRight",0x100),
        (9,"AML","AttackingMidfielderLeft",0x1000),(10,"AMC","AttackingMidfielderCentre",0x2000),
        (11,"AMR","AttackingMidfielderRight",0x800),(12,"ST","AttackerCentre",0x4000),
        (13,"WBL","WingBackLeft",0x40),(14,"WBR","WingBackRight",0x20)};
    public static DecodedPositionFields Decode(byte[] block)
    {
        if(block.Length!=15 || block.Any(value=>value>20))throw new InvalidDataException("Pinned position block requires 15 values in 0..20");
        var fields=Mapping.Select(item=>new PositionFamiliarity(item.Code,item.Name,0x150+item.Index,item.Bit,block[item.Index],block[item.Index]>=18)).ToArray();
        uint mask=0;foreach(var field in fields)if(field.natural)mask|=field.maskBit;
        return new(fields,mask,fields.Where(field=>field.natural).Select(field=>field.code).ToArray(),block[1],block[0]>=15);
    }
    public static void SelfTest()
    {
        var block=new byte[15];block[0]=20;block[1]=20;block[2]=18;block[3]=17;block[4]=1;
        var decoded=Decode(block);
        if(decoded.naturalPositionMask!=9 || !decoded.naturalPositionCodes.SequenceEqual(new[]{"GK","DL"}))throw new Exception("Native left/right or reserved-slot mapping");
        block[0]=15;decoded=Decode(block);
        if(!decoded.businessRuleIsGoalkeeper || decoded.familiarities[0].natural || decoded.naturalPositionMask!=8)throw new Exception("Goalkeeper/natural threshold distinction");
        block[0]=14;if(Decode(block).businessRuleIsGoalkeeper)throw new Exception("Goalkeeper threshold boundary");
        foreach(var invalid in new[]{new byte[14],new byte[16],Enumerable.Repeat((byte)21,15).ToArray()})
        {try{Decode(invalid);}catch(InvalidDataException){continue;}throw new Exception("Invalid position block accepted");}
    }
}
