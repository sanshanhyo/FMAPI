# Experimental save-context contract

ISaveContextReader exposes a value-only current save/date/manager/team result. SessionId scopes all IDs; it is not a native pointer or cross-save identity guarantee. SaveLabel is an adapter-provided label, not a filesystem path. Consumers must check status and IsSynthetic and reread context after session changes; a retained immutable snapshot remains historical data. No events, game pause state, save file parsing or stable SDK promise is introduced.

MockSaveContextReader implements this contract with explicitly supplied owned fixtures. Every load receives a new session ID; clear/dispose returns unavailable and disposal prevents further loads. No synthetic fallback is wired into Windows, Core or IModContext, so this new experimental reader does not bypass host game-read grants. A future host integration must enforce grants and scope reader access to mod lifetime before exposing it to mods.

The end-to-end test uses the public reader interface, checks date/manager/team and synthetic provenance, replacement identity and shutdown. Actual current-game-date source, save identity, manager/team lifetime observation and exact-build qualification remain unverified. Historical message date decoding is not used as current game date.

Validation: 60 offline Core.Tests cases passed with documented cached test dependency versions; existing offline CLI demo passed. No game access.
