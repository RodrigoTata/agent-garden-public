---
name: rea
description: Reverse engineer native binaries (ELF/PE/Mach-O), managed code (.NET/IL2CPP), JavaScript/Electron ASAR packages, Android APKs, firmware images, and network/runtime traces with REA (Reverse Engineer Anything). Connects to REA MCP server or CLI to decompile code, inspect imports/certificates/metadata, observe live executions, or build AgentEnv web environment bundles. Use when the user asks to reverse engineer, decompile, analyze a compiled executable or package, extract firmware, inspect an APK or ASAR, or debug runtime network captures. Skip for standard source-code-only repo architecture tasks.
license: MIT
metadata:
  author: morluto
  source: https://github.com/morluto/rea
  upstream-license: MIT
  adapted-by: Rodrigo González
---

# REA (Reverse Engineer Anything)

Use REA when a conclusion depends on a shipped binary or package, decompilation, runtime observation, or behavior not established by source code alone. For ordinary architecture analysis of an accessible source repository, use normal repository tools and skip REA.

## Leading Words

- **Evidence**: Ground every finding in an audited, hash-verified Evidence record (`parent_evidence_id`, SHA-256). Distinguish static observations, dynamic measurements, inferences, and unknowns. Never claim static analysis observed execution.
- **Route**: Map the target format directly to its dedicated tool on the first call. Never guess or run broad preliminary scans when a specific tool matches the artifact.
- **Budget**: Enforce execution bounds (deadlines, memory ceilings, summary-first paging) to prevent transport overflows and agent timeouts.

---

## Process

### Step 1 — Target Routing

Identify the artifact or target type provided by the operator and route to its dedicated tool. Use `open_binary` for active-target native or archive workflows; target-free tools take an explicit local path or endpoint directly.

| Target Format / Scenario | Initial Tool / Command | Reference Guide / Workflow |
| :--- | :--- | :--- |
| **Electron ASAR / JavaScript Tree** | `analyze_javascript_application` | [references/javascript-applications.md](references/javascript-applications.md) |
| **Archive Inventory** (ZIP, APK, IPA, MSIX, DMG, PyInstaller) | `open_binary` → `inspect_artifact` | PyInstaller: bootloader is native prefix; CArchive is app layer |
| **Apple Bundle Resources** (plist, assets, nib, keyed archive) | `open_bundle_resources` → resource tools | Reads app bundle without requiring executable or deep provider |
| **Android APK Code / Methods** | `inspect_android_package` → `inspect_android_method` | [references/android-applications.md](references/android-applications.md) (requires JADX/Java) |
| **APK Signatures & Lineage** (v1, v2, v3, v3.1) | `inspect_apk_signature` | Validates scheme presence, cert fingerprints, and key rotation |
| **Managed PE / .NET CLI** | `inspect_managed_artifact` | .NET assembly analysis; NativeAOT uses Ghidra native workflow |
| **Firmware Image** | `inspect_firmware_regions` / `extract_firmware` | Uses caller-supplied Binwalk/Unblob on Linux |
| **Native Executable / Library** (ELF, PE, Mach-O) | `open_binary` → `analyze_function` / `binary_overview` | [references/native-and-artifacts.md](references/native-and-artifacts.md) (Ghidra, Hopper, IDA, Kuna) |
| **Native Runtime Behavior** (LLDB, Frida, GDB, Rizin) | Choose native runtime workflow | [references/runtime-observation.md](references/runtime-observation.md) |
| **Browser User Scenario** (clicks, inputs, page auth) | `capture_browser_scenario` | [references/runtime-observation.md](references/runtime-observation.md) |
| **Agent Environment Bundle** (AgentEnv from web app) | `capture_browser_scenario` → `export_environment_bundle` | [references/environments.md](references/environments.md) |
| **Network Traffic Capture** (HAR, SAZ, mitmproxy, qlog) | `inspect_web_network_capture` | Reads saved recordings offline without live requests |
| **Packet Captures** (PCAP, PCAPNG) | `inspect_packet_capture` / `inspect_pcap_capture` | Uses TShark/capinfos; requires Wireshark tooling |
| **Hardware Signal / Logic Traces** | `decode_signal_recording` | Uses sigrok-cli; reads existing recordings without live hardware |
| **WebAssembly Artifact** (.wasm) | `inspect_wasm_artifact` | Uses WABT; decodes WAT without executing binary |
| **EVM Bytecode** | `inspect_evm_interface` (raw or hex) | Discovers candidate functions, selectors, and mutability |
| **Go Compiler / Module Metadata** | `inspect_go_binary` | Target-free; extracts embedded module/dependency versions |
| **GGUF / Safetensors Models** | `inspect_model_artifact` | Target-free; reads header declarations and tensor shapes |
| **Unity IL2CPP Metadata** (`global-metadata.dat`) | `inspect_il2cpp_metadata` | Target-free; extracts types, fields, methods, and string literals |
| **Rust Dependency Metadata** (`.dep-v0`) | `inspect_rust_binary` | Target-free; extracts cargo-auditable crate lists |
| **PE Certificates / Imports / Load Config** | `inspect_pe_certificates` / `inspect_pe_imports` / `inspect_pe_load_config` | Target-free; decodes Authenticode, IAT/delay-load, CFG/SafeSEH |
| **ELF Notes / Kernel Modules** | `inspect_elf_notes` / `inspect_kernel_module` | Target-free; decodes build-id, ABI tags, and modinfo |
| **Apple `.ips` Crash Reports** | `inspect_apple_ips` | Target-free; parses registers and stack frames (bug_type 309) |
| **CPython Bytecode** (.pyc) | `inspect_python_pyc` | Target-free; decodes magic, hash/mtime, and marshal code objects |
| **Erlang BEAM** (.beam) | `inspect_erlang_beam` | Target-free; extracts chunks, atoms, imports, and exports |
| **SQLite Database Snapshot** | `inspect_sqlite_database` | Inspects schema and sample rows using native limits |
| **Offline Linux ELF Layout / Crash Core** | `inspect_binary_layout` / `inspect_recorded_crash` | Target-free; reads ELF sections, relocations, or core dumps |

**Completion criterion**: The target is matched to an exact REA tool and the invocation mode (active-target session vs. target-free path) is determined.

---

### Step 2 — Connection & Engine Readiness

Installing this skill supplies instructions; it does not automatically register the REA MCP server or launch analysis engines.

1. **Check Active Tools**: If REA MCP tools are registered and available in the current session, proceed directly to analysis. Do not run diagnostics or setup before every query.
2. **Handle Connection Drop or Startup Failure**:
   - If a call drops or REA fails to start, retry once if safe. If it fails again, inform the operator and follow [references/connection-and-recovery.md](references/connection-and-recovery.md).
   - For configuration or MCP repair, inspect with a read-only plan first:
     ```bash
     npx -y rea-agents@6.8.0 doctor --client antigravity --json
     npx -y rea-agents@6.8.0 setup --client antigravity --dry-run --json
     ```
     *(Substitute the active client ID: `antigravity`, `claude_code`, `codex`, `cursor`, `vscode`, etc.).*
3. **CLI Direct Fallback**: If MCP is unavailable or unnecessary (e.g. inspecting an operator-supplied ASAR or JS tree), execute directly via CLI without engine registration:
   ```bash
   npx -y rea-agents@6.8.0 analyze-javascript-application /absolute/path/to/app --json
   ```

> [!IMPORTANT]
> REA setup never installs Node.js, npm, Java, Ghidra, IDA, JADX, or Binwalk. Use existing host prerequisites. Preserve sandboxes and client approval policies; never silently disable isolation to force a command to run.

**Completion criterion**: The agent has an active MCP connection or a validated CLI invocation path.

---

### Step 3 — Summary-First Investigation

Large binary graphs, ASAR trees, and packet captures quickly exceed model context and transport frames.

1. **Request Summary Detail**: For targets of unknown or large size, always supply `"detail": "summary"` on initial calls (`analyze_javascript_application`, `inspect_binary_layout`, `open_binary`).
2. **Retain Parent Evidence ID**: Summary calls return a `parent_evidence_id`. Store this ID to page sections, modules, or procedures without re-running analysis.
3. **Handle Transport Constraints**: If MCP reports `resource_constraint` (`details.resource: "transport"`), use `inspect_analysis_view` with the retained Evidence reference, or export the session via `export_evidence_bundle`.

**Completion criterion**: The initial summary is retrieved and the `parent_evidence_id` is recorded in the working ledger.

---

### Step 4 — Focused Deep-Dive

Use the retained Evidence ID to query specific items:

```json
{
  "source": { "kind": "retained-evidence", "evidence_id": "ev_PARENT_ID" },
  "view": { "kind": "item", "collection": "modules", "selector": { "node_id": "TARGET_NODE_ID" } }
}
```

Consult the specialized domain guides as the task demands:
- **Native Binaries & Decompilation**: [references/native-and-artifacts.md](references/native-and-artifacts.md)
- **JavaScript & Electron ASAR**: [references/javascript-applications.md](references/javascript-applications.md)
- **Android APKs & Manifests**: [references/android-applications.md](references/android-applications.md)
- **Runtime Observation & Instrumentation**: [references/runtime-observation.md](references/runtime-observation.md)
- **Agent Environments (AgentEnv)**: [references/environments.md](references/environments.md)
- **Evidence Ledgers & Verification**: [references/evidence-workflows.md](references/evidence-workflows.md)
- **Troubleshooting & Timeouts**: [references/connection-and-recovery.md](references/connection-and-recovery.md)

**Completion criterion**: The specific question (function implementation, security check, network endpoint, or signature) is answered with exact byte/source provenance.

---

### Step 5 — Synthesis & Session Teardown

1. **Evidence Grounding**: Explain findings in clear, natural language, explicitly distinguishing:
   - **Observed Facts**: Bytes, hashes, decompiled pseudocode, manifest records, network payloads.
   - **Inferred Hypotheses**: Architectural intent, compiler optimizations, reconstructed structures.
   - **Unknowns**: Unanalyzed modules, stripped symbols, truncated traces, or skipped functions.
2. **Session Cleanup**: If an active binary session was opened with `open_binary`, close it cleanly:
   ```json
   { "tool": "close_binary", "arguments": {} }
   ```
   For Frida, GDB, Rizin, or browser sessions, invoke the corresponding persistent session teardown tool (`close_frida_session`, `close_browser_session`).

**Completion criterion**: Findings are reported with Evidence ID citations, inferences are separated from facts, and all persistent analysis sessions are confirmed closed.

