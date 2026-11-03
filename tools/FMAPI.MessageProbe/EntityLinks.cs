using System.Collections.Generic;
using System.IO;

sealed partial class Probe
{
    string? CandidateType(ulong pointer)
    {
        if(pointer==0)return null;
        try{return TypeName(pointer);}
        catch(InvalidDataException){return null;}
    }
    object SamplePlayerPositions()
    {
        var root=Pointer(moduleBase+0x5703738);var mode=Read(moduleBase+0x5703DE0,1)[0];
        var vector=mode==0?root+0x60:Pointer(root+0x80);var bounds=Read(vector,16);
        var begin=BitConverter.ToUInt64(bounds);var end=BitConverter.ToUInt64(bounds,8);
        if(end<begin || (end-begin)%8!=0 || end-begin>8000000UL*8)throw new InvalidDataException("Person registry bounds");
        var registryType=CandidateType(root);var rootWord=Pointer(root);ulong? rootWordModuleRva=rootWord>=moduleBase && rootWord-moduleBase<(ulong)pe.PEHeaders.PEHeader!.SizeOfImage?rootWord-moduleBase:null;
        var inspected=(int)Math.Min((end-begin)/8,64UL);var pointers=inspected==0?Array.Empty<byte>():Read(begin,inspected*8);
        var players=new List<object>();
        for(int i=0;i<inspected && players.Count<8;i++)
        {
            var person=BitConverter.ToUInt64(pointers,i*8);if(person==0)continue;
            if(Pointer(person)!=moduleBase+0x4D27758)continue;
            if(TypeName(person)!=".?AVACTUAL_PLAYER@db@@")throw new InvalidDataException("Actual player PERSON RTTI mismatch");
            var displacement=BitConverter.ToInt32(Read(person-4,4));if(displacement<0 || displacement>4096)throw new InvalidDataException("Actual player displacement");
            var player=person-(uint)displacement-0x288;
            if(Pointer(player)!=moduleBase+0x4D27228 || TypeName(player)!=".?AVACTUAL_PLAYER@db@@")throw new InvalidDataException("Actual player primary mismatch");
            var identity=Read(person+8,8);var slots=Read(player+0x150,15);
            if(slots[0]>20)throw new InvalidDataException("Goalkeeper familiarity range");
            if(!Read(person+8,8).SequenceEqual(identity) || !Read(player+0x150,15).SequenceEqual(slots))throw new InvalidOperationException("Player position fields changed");
            players.Add(new {registryIndex=i,personReferenceCandidate=BitConverter.ToUInt32(identity),personUidCandidate=BitConverter.ToUInt32(identity,4),goalkeeperFamiliarity=slots[0],businessRuleIsGoalkeeper=slots[0]>=15,otherPositionSlotsRaw=slots.Skip(1).Select(value=>(int)value).ToArray(),identityStatus="candidate fields; persistent UID binding not yet confirmed"});
        }
        if(Pointer(moduleBase+0x5703738)!=root || Read(moduleBase+0x5703DE0,1)[0]!=mode || !Read(vector,16).SequenceEqual(bounds) || (inspected>0 && !Read(begin,inspected*8).SequenceEqual(pointers)))throw new InvalidOperationException("Person registry changed");
        return new {status=players.Count>0?"partial":"unavailable",scope="first 64 loaded person-registry slots; at most 8 exact actual players",inspected,registryType,rootWordModuleRva,registryEntries=(end-begin)/8,players,notClubRoster=true};
    }
    object ReadRequestedPositions(uint[] requested)
    {
        var table=Pointer(moduleBase+0x5703738);
        if(Pointer(table)!=moduleBase+0x4CA5278 || TypeName(table)!=".?AV?$DATABASE_TABLE@VPERSON@db@@@db@@")throw new InvalidDataException("PERSON table mismatch");
        var flags=Read(table+0x5C,1)[0];var dirty=Read(table+0xA0,1)[0];
        if((flags&1)!=0 && dirty!=0)throw new InvalidOperationException("UID cache requires native sorting; no game call attempted");
        var indirect=(flags&1)==0?Pointer(table+0x80):0;var vector=(flags&1)==0?indirect:table+0x88;
        var bounds=Read(vector,24);var begin=BitConverter.ToUInt64(bounds);
        var count=Bounds.Count(begin,BitConverter.ToUInt64(bounds,8),BitConverter.ToUInt64(bounds,16),8,8000000);
        var records=new List<object>();
        foreach(var uid in requested)
        {
            int lo=0,hi=count-1,steps=0;ulong person=0;
            while(lo<=hi && steps++<32)
            {
                int mid=lo+(hi-lo)/2;var candidate=Pointer(begin+(ulong)mid*8);
                if(candidate==0)throw new InvalidDataException("Null UID index entry");
                int observed=BitConverter.ToInt32(Read(candidate+0x0C,4));
                if(observed==(int)uid){person=candidate;break;}
                if(observed<(int)uid)lo=mid+1;else hi=mid-1;
            }
            if(lo<=hi && steps>32)throw new InvalidDataException("UID lookup step limit");
            if(person==0){records.Add(new {uid,status="unavailable",reason="UID absent from selected loaded index"});continue;}
            if(Pointer(person)!=moduleBase+0x4D27758 || TypeName(person)!=".?AVACTUAL_PLAYER@db@@"){records.Add(new {uid,status="unsupported",reason="not exact ACTUAL_PLAYER PERSON subobject"});continue;}
            var displacement=BitConverter.ToInt32(Read(person-4,4));if(displacement<0 || displacement>4096)throw new InvalidDataException("Actual player displacement");
            var player=person-(uint)displacement-0x288;
            if(Pointer(player)!=moduleBase+0x4D27228 || TypeName(player)!=".?AVACTUAL_PLAYER@db@@")throw new InvalidDataException("Actual player primary mismatch");
            var identities=Read(person+8,8);if(BitConverter.ToUInt32(identities,4)!=uid)throw new InvalidOperationException("UID changed");
            var slots=Read(player+0x150,15);if(slots.Any(value=>value>20))throw new InvalidDataException("Position familiarity range");
            if(!Read(person+8,8).SequenceEqual(identities) || !Read(player+0x150,15).SequenceEqual(slots))throw new InvalidOperationException("Requested player changed");
            var employment=ReadPlayerEmployment(person,player);
            if(!Read(person+8,8).SequenceEqual(identities) || Pointer(player)!=moduleBase+0x4D27228)throw new InvalidOperationException("Player identity changed after employment read");
            records.Add(new {uid,status="available",uidMatched=true,personReferenceRaw=BitConverter.ToUInt32(identities),goalkeeperFamiliarity=slots[0],businessRuleIsGoalkeeper=slots[0]>=15,otherPositionSlotsRaw=slots.Skip(1).Select(value=>(int)value).ToArray(),positionFields=PositionFields.Decode(slots),positionNamesVerified=true,employment});
        }
        if(Pointer(moduleBase+0x5703738)!=table || Read(table+0x5C,1)[0]!=flags || ((flags&1)!=0 && Read(table+0xA0,1)[0]!=dirty) || ((flags&1)==0 && Pointer(table+0x80)!=indirect) || !Read(vector,24).SequenceEqual(bounds))throw new InvalidOperationException("UID index changed");
        return new {status="partial",scope="explicit requested UIDs; no all-registry scan",requested=requested.Length,records,clubMembershipVerifiedHere=false};
    }
    object ReadPlayerEmployment(ulong person,ulong player)
    {
        if(Pointer(Pointer(person)+0x3C0)!=moduleBase+0x1634E50)throw new InvalidDataException("Unsupported player employment getter");
        var vbtable=Pointer(player+8);
        if(vbtable<moduleBase || vbtable-moduleBase>(ulong)file.Length-12)throw new InvalidDataException("Player employment vbtable range");
        int offset=BitConverter.ToInt32(Read(vbtable+8,4));
        if(offset<0 || offset>8192)throw new InvalidDataException("Player employment virtual offset");
        var slot=player+0x88+(uint)offset;var contract=Pointer(slot);var contractType=CandidateType(contract);
        ulong team=0,club=0;string? teamType=null,clubType=null;uint? clubUid=null;byte? kind=null;
        if(contractType==".?AVFULL_CONTRACT@db@@")
        {
            kind=Read(contract+0x26,1)[0];team=Pointer(contract+0x10);teamType=CandidateType(team);
            if(teamType==".?AVTEAM@db@@"){club=Pointer(team+0x30);clubType=CandidateType(club);if(clubType==".?AVCLUB@db@@")clubUid=BitConverter.ToUInt32(Read(club+0x0C,4));}
        }
        if(Pointer(player+8)!=vbtable || BitConverter.ToInt32(Read(vbtable+8,4))!=offset || Pointer(slot)!=contract || (team!=0 && Pointer(contract+0x10)!=team) || (club!=0 && Pointer(team+0x30)!=club) || (clubUid!=null && BitConverter.ToUInt32(Read(club+0x0C,4))!=clubUid))throw new InvalidOperationException("Player employment changed");
        return new {status=clubUid!=null?"available":"partial",contractType,kind,teamType,clubType,clubUid,source="pinned ACTUAL_PLAYER PERSON virtual+3C0 getter 1634E50",atomicSnapshot=false};
    }
    public object CaptureEntityLinks(uint[]? requestedUids=null,bool selectionOnly=false)
    {
        budget=65536;
        const string gameAssemblyHash="820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A";
        var assembly=process.Modules.Cast<System.Diagnostics.ProcessModule>().Single(module=>string.Equals(module.ModuleName,"GameAssembly.dll",StringComparison.OrdinalIgnoreCase));
        using(var stream=File.OpenRead(assembly.FileName))if(Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(stream))!=gameAssemblyHash)throw new InvalidDataException("Unsupported GameAssembly selection-name mapping profile");
        var selected=Pointer(moduleBase+0x56F32C8);var selectedType=CandidateType(selected);
        var selectedIdentity=selected==0?Array.Empty<byte>():Read(selected,16);
        object? activeManager=null;int selectionMatches=0;
        var root=Pointer(moduleBase+0x56F3008);var header=Read(root,0x30);
        if(BitConverter.ToUInt64(header)!=moduleBase+0x4E2D678 || TypeName(root)!=".?AVHUMAN_NON_PLAYER_MANAGER@@")throw new InvalidDataException("Human manager root mismatch");
        var begin=BitConverter.ToUInt64(header,0x18);
        var count=Bounds.Count(begin,BitConverter.ToUInt64(header,0x20),BitConverter.ToUInt64(header,0x28),8,16);
        var entries=count==0?Array.Empty<byte>():Read(begin,count*8);var managers=new List<object>();
        for(int i=0;i<count;i++)
        {
            var owner=BitConverter.ToUInt64(entries,i*8);if(owner==0)continue;
            if(Pointer(owner)!=moduleBase+0x4CC086C || Pointer(owner+0x440)!=moduleBase+0x4CC08D8)throw new InvalidDataException("Human owner mismatch");
            var person=owner+0x440;var identity=Read(person+8,8);
            var displacement=BitConverter.ToInt32(Read(person-4,4));
            if(displacement<0 || displacement>4096)throw new InvalidDataException("Manager PERSON displacement");
            var adjusted=person-(uint)displacement;var complete=adjusted-0x440;var vbtable=Pointer(complete);
            if(vbtable!=moduleBase+0x4CC086C)throw new InvalidDataException("Manager job vbtable mismatch");
            var offset=BitConverter.ToInt32(Read(vbtable+8,4));if(offset<0 || offset>8192)throw new InvalidDataException("Manager job virtual offset");
            var virtualBase=complete+(uint)offset;var contract=Pointer(virtualBase+0x80);
            var contractType=CandidateType(contract);ulong payload=0,linkedClub=0;string? payloadType=null;string? payloadField30Type=null;byte? contractKind=null;uint? clubUidCandidate=null;ulong? kindMethodRva=null;
            if(contractType==".?AVFULL_CONTRACT@db@@")
            {
                contractKind=Read(contract+0x26,1)[0];
                var vtable=Pointer(contract);var function=Pointer(vtable+0x50);
                if(function>=moduleBase && function-moduleBase<int.MaxValue)kindMethodRva=function-moduleBase;
                payload=Pointer(contract+0x10);payloadType=CandidateType(payload);
                if(payloadType==".?AVTEAM@db@@"){linkedClub=Pointer(payload+0x30);payloadField30Type=CandidateType(linkedClub);if(payloadField30Type==".?AVCLUB@db@@")clubUidCandidate=BitConverter.ToUInt32(Read(linkedClub+0x0C,4));}
            }
            var flag=Read(owner+0x422,1)[0];
            bool isSelected=selected!=0 && selected==person && selectedType==".?AVHUMAN_NON_PLAYER@db@@";
            if(isSelected)
            {
                selectionMatches++;
                if(!selectedIdentity.AsSpan(8,8).SequenceEqual(identity))throw new InvalidOperationException("Selected manager identity changed");
                activeManager=new {uid=BitConverter.ToUInt32(identity,4),clubUid=clubUidCandidate,contractType,contractKind,source="native GameCurrentManager (GCuM) selection global",activeVerified=true,atomicSnapshot=false};
            }
            if(!Read(person+8,8).SequenceEqual(identity) || Pointer(virtualBase+0x80)!=contract || (payload!=0 && Pointer(contract+0x10)!=payload) || (linkedClub!=0 && Pointer(payload+0x30)!=linkedClub) || (clubUidCandidate!=null && BitConverter.ToUInt32(Read(linkedClub+0x0C,4))!=clubUidCandidate) || (contractKind!=null && Read(contract+0x26,1)[0]!=contractKind))throw new InvalidOperationException("Manager entity changed");
            managers.Add(new {personReferenceCandidate=BitConverter.ToUInt32(identity),personUidCandidate=BitConverter.ToUInt32(identity,4),flag422Raw=flag,contractType,contractKind,kindMethodRva,payloadType,payloadField30Type,clubUidCandidate,activeVerified=isSelected});
        }
        if(Pointer(moduleBase+0x56F3008)!=root || !Read(root,0x30).SequenceEqual(header) || (count>0 && !Read(begin,count*8).SequenceEqual(entries)))throw new InvalidOperationException("Human manager collection changed");
        if(selectionMatches>1)throw new InvalidDataException("Duplicate selected manager ownership");
        if(Pointer(moduleBase+0x56F32C8)!=selected || (selected!=0 && !Read(selected,16).SequenceEqual(selectedIdentity)))throw new InvalidOperationException("Selected manager changed");
        object positions=selectionOnly?new {status="not-requested"}:requestedUids==null?SamplePlayerPositions():ReadRequestedPositions(requestedUids);
        var selection=new {status=selectionMatches==1?"available":"unavailable",sourcePropertyKey="GCuM",selectedType,matchedHumanOwner=selectionMatches==1,reason=selectionMatches==1?(string?)null:selected==0?"no native current-manager selection":"selected record not matched to validated human-owner collection"};
        return new {status="partial",selection,positions,binarySha256=Hash,gameAssemblySha256=gameAssemblyHash,processId=process.Id,processStartedAt=started.ToUniversalTime(),atomicSnapshot=false,managerCandidates=managers,activeManager,unsupported=new[]{"cross-session active-selection stability","current match/tactic position assignment","cross-save UID persistence"}};
    }
}
