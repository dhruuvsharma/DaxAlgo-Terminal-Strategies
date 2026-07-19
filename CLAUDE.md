# DaxAlgo Terminal Strategy Pack — Claude Working Guide

This repo holds the **nine first-party strategy plugins** for
[DaxAlgo Terminal](https://github.com/dhruuvsharma/DaxAlgo-Terminal) (a WPF multi-broker trading
terminal). They were factored **out of** the host repo so the terminal ships as an empty sandbox; each
strategy now compiles against the published **`DaxAlgo.Sdk` / `DaxAlgo.Sdk.Wpf` NuGet packages** and is
loaded by the terminal at runtime from its `plugins/` folder — the host is never recompiled.

## What a strategy is here

- **`src/…/Engine/…Strategy.cs` (or `…Kernel.cs`)** — the strategy itself: an `IBacktestStrategy` that
  receives ticks/bars/depth/trades and places orders through `IOrderRouter`. **All strategy math lives
  here.** The same kernel runs in backtest and live, so they can't diverge.
- **`src/…/…Plugin.cs`** — the `IStrategyPlugin` entry point (the host finds exactly one public
  implementation per assembly) + the catalog descriptor. Registration is plain `IServiceCollection` calls.
- **`src/…/plugin.json`** — read by the host BEFORE any code loads: `id`, `version`, `publisher`, and
  `targetSdkVersion` (major.minor must match the host SDK; pre-1.0 = exact).
- **`src/…/…ViewModel.cs` + `…Window.xaml(.cs)`** — the live strategy window. The VM derives from
  `LiveSignalStrategyViewModelBase` (host-provided: instrument picker, warm-up, start/stop, signal feed,
  presets, Activity Log) and supplies `DataRequirement` + `BuildStrategy(contract)` returning the SAME
  kernel. A UI plugin references `DaxAlgo.Sdk.Wpf`; a headless one would reference `DaxAlgo.Sdk`.
- **`tests/…​.Tests/`** — offline harnesses driving the kernel/calculator with synthetic input. Keep green.

## Hard rules

1. **Reference ONLY the SDK.** A strategy csproj references `DaxAlgo.Sdk.Wpf` (or `DaxAlgo.Sdk`) with
   `ExcludeAssets="runtime"` plus its own public NuGet UI deps (`MahApps.Metro`, `HelixToolkit.Wpf`,
   `CommunityToolkit.Mvvm`, MS.Extensions abstractions). **Never** reference host internals
   (`TradingTerminal.Infrastructure`, the shells) — they aren't in the SDK and won't be at runtime.
2. **Never ship host assemblies in a `.daxplugin`.** The host shares its own `TradingTerminal.*` /
   `DaxAlgo.Sdk*` / MahApps / ScottPlot / CommunityToolkit into the plugin's load context; a shipped copy
   breaks type identity and the strategy silently stops matching. `pack-plugin.ps1` ships only the
   strategy dll/pdb/deps.json + `plugin.json` (+ `HelixToolkit.Wpf.dll`, the one private dep the host
   lacks, for the 3D-cube strategies).
3. **`DaxAlgoSdkVersion` is the single version knob** (`Directory.Build.props`) — bump in lockstep with a
   host SDK upgrade, then rebuild + repackage. Keep each `plugin.json` `targetSdkVersion` compatible on
   major.minor.
4. **Strict MVVM** in the window projects: no business logic in `.xaml.cs`; VMs use
   `[ObservableProperty]`/`[RelayCommand]`. Strategy math never touches WPF.

## Build / test / pack

```powershell
dotnet build DaxAlgo.Strategies.slnx        # all 9 + tests (NU1701 on HelixToolkit.Wpf is expected)
dotnet test  DaxAlgo.Strategies.slnx
./pack-plugin.ps1                            # -> dist/*.daxplugin ; install via the Plugin Manager
```

.NET 9 SDK, TFM `net9.0-windows7.0` (WPF). No host source or submodule — restore pulls the SDK from
nuget.org.

## Relationship to the host

The engine/live contracts (`IBacktestStrategy`, `IStrategyPlugin`, `LiveSignalStrategyViewModelBase`,
`StrategyFactoryRegistration`, the parameter schema) are owned by the host and exposed through the SDK —
**do not redeclare them.** For host-side architecture, see the DaxAlgo-Terminal repo's `CLAUDE.md` and
`docs/`. When the host SDK version changes, this repo follows.
