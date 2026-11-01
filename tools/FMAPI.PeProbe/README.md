# PE research probe

Original standalone diagnostic for trusted local PE files. It reads a file from disk; it does not open a game process or invoke game functions. Build with .NET 10 using `dotnet build tools/FMAPI.PeProbe`. Run the DLL with a PE path and an RTTI fragment, or `xref` followed by hexadecimal RVAs.

The tool reports MSVC RTTI/vtable candidates and raw relative-displacement candidates. References must be confirmed by instruction-boundary disassembly; adjacent vtable slots may belong to another table. This is not a general untrusted-file parser or a supported game adapter. Keep outputs private: never commit game binaries, generated metadata, disassembly, raw process samples or save-derived content. No native game data is bundled. The tool has no third-party dependencies and is not part of the shipping solution.

Validation: standalone Release build passed with zero warnings/errors. It was used to reproduce the manager RTTI candidates documented in `docs/research/message-reader-checkpoint.md`. Full SDK tests were not rerun for this diagnostic-only addition.
