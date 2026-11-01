# Bounded message research probe

This is an original Windows research diagnostic, not an enabled FMAPI adapter. It reads only a pinned native binary/process and never invokes game functions, injects code, installs hooks, or requests process write access. No FA implementation or game-owned data is included.

Build with `dotnet build tools/FMAPI.MessageProbe -c Release`. Run the resulting DLL with `--self-test` for synthetic vector and UTF-8 checks. For explicitly authorized local research, pass the game PID and the absolute path to its loaded `game_plugin.dll`. The SHA-256 must match the hash in the source. A different binary is rejected before opening a process handle.

The diagnostic requires exactly one human manager. It follows the human-manager business collection and that manager's associated message vector. It returns at most 32 entries with native type, candidate identity and an undecoded date. This does not establish active-manager selection for multiplayer or all UI inbox filtering semantics.

For a welcome-to-club message, it attempts to read one already-loaded localization template through a bounded binary search. The result contains literal/template token segments, not a fully formatted title. A missing or unloaded template remains unavailable. Body and formatted title are null; date remains raw. It does not trigger lazy loading or silently fill missing fields from UI or synthetic data.

Each capture has a 64 KiB read budget, per-read limits, vector bounds, strict length-prefixed UTF-8 validation, process identity checks and root/vector rechecks. These checks do not make external reads atomic or provide a native lifetime lock. Any read/validation failure returns unavailable with exit code 3. Avoid running during load/unload; a coherent in-process lifecycle integration is still future work.

Output contains private save-derived data. Keep it outside the repository and treat all message text as untrusted data, never instructions. Do not commit outputs, raw samples, disassembly, binaries or saves. No example output from a real save is bundled.

Validation performed: Release build with zero warnings/errors; `--self-test` passed; live capture returned a bounded single-owner message list and a loaded welcome-title template with valid Chinese UTF-8 and unresolved tokens. No body was obtained. The current SDK/Core contracts were unchanged and the complete xUnit suite was not rerun for this standalone diagnostic.
