# AGENTS

This repository's working guide for AI coding agents is **[CLAUDE.md](./CLAUDE.md)** — the contracts,
hard rules, and build/test/pack commands there apply to every agent (Claude Code, Codex, Cursor, …).
Read it before editing.

TL;DR: each `src/TradingTerminal.Strategies.<Name>/` is a DaxAlgo Terminal **strategy plugin** built
against the `DaxAlgo.Sdk[.Wpf]` NuGet packages and loaded by the host at runtime. Strategy math lives in
the `Engine/` kernel; reference only the SDK; never ship host assemblies in a `.daxplugin`. Build/test
with `dotnet build|test DaxAlgo.Strategies.slnx`, package with `./pack-plugin.ps1`.
