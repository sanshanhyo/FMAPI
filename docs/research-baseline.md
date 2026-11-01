# Public research baseline

Checked on **2026-11-01**. These primary sources inform project direction. They do not establish FMAPI runtime compatibility.

- The [official FM27 page](https://www.footballmanager.com/fm27) describes Launch Preview access and a digital release date of 2026-11-10. Compatibility records must distinguish preview and release builds.
- The [official FM26 page](https://www.footballmanager.com/fm26) describes the move to Unity. The [official FM27 features page](https://www.footballmanager.com/fm27/features) also carries Unity branding. An engine family does not reveal a stable public modding API or guarantee access to game data.
- [Unity's IL2CPP introduction](https://docs.unity.com/en-us/engine/6000.6/manual/programming-environment/scripting-backends/il2cpp/il2cpp-introduction) explains its ahead-of-time conversion and native compilation model. A particular game's scripting backend, engine version, metadata format, ABI, and platform behavior still require build-specific verification.

FMAPI remains independent and unofficial. Its current executable behavior is limited to the offline host and synthetic adapter. Revisit these sources when planning a real adapter; public product pages can change.
