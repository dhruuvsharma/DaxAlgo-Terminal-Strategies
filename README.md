# DaxAlgo Terminal — Strategy Pack

The nine first-party strategies for **[DaxAlgo Terminal](https://github.com/dhruuvsharma/DaxAlgo-Terminal)**,
maintained as an independent repository. The terminal itself now ships as an **empty sandbox** — a fresh
install has no built-in strategies; you author your own (in-app Roslyn builder / AI Strategy Builder) or
install packs like this one. These strategies are just the first such pack.

Each strategy is a runtime **plugin**: it compiles against the published `DaxAlgo.Sdk` / `DaxAlgo.Sdk.Wpf`
NuGet packages (no host source needed) and the terminal loads it from its `plugins/` folder — the host is
never recompiled.

## The loop

```powershell
dotnet build DaxAlgo.Strategies.slnx    # 1. build all 9 strategies + tests
dotnet test  DaxAlgo.Strategies.slnx    # 2. offline kernel/calculator harness
./pack-plugin.ps1                        # 3. -> dist/*.daxplugin  (one per strategy)
```

4. In DaxAlgo Terminal: **Plugins → Manage strategy plugins… → Install plugin…**, pick a `.daxplugin`,
   restart. The strategy appears in the catalog under the id in its `plugin.json`.

`./pack-plugin.ps1 -Name TradingTerminal.Strategies.SigmaIcFlow` packs a single strategy.

## Strategies

| Strategy | What |
|---|---|
| `SigmaIcFlow` | Σ⁻¹·IC order-flow optimizer (11-signal weighted composite, regime classifier, isotonic entry gate) |
| `CumulativeDelta` | Cumulative-delta divergence |
| `FilteredOrderFlow` | Filtered order-flow imbalance — arXiv:2507.22712 |
| `ImbalanceHeatFront` | Imbalance heat-front (3D) |
| `IndexKScoreSurface` | Index k-score surface (3D) |
| `IndexRegimeGraph` | Index regime graph over the Advanced Market Regime stack |
| `OrderFlowCube` | Order-flow regime cube (3D) |
| `OrderFlowPressureMap` | Multi-ticker order-flow pressure monitor |
| `OrderFlowSurfaceSpike` | Order-flow surface spike detector (3D) |

## Layout

| Path | What |
|---|---|
| `src/TradingTerminal.Strategies.<Name>/` | One strategy plugin each (kernel + `IStrategyPlugin` + WPF window + `plugin.json`) |
| `tests/…​.Tests/` | Offline harnesses (SigmaIcFlow warm-up, PressureMap calculator) |
| `pack-plugin.ps1` | Builds + packages each strategy into an integrity-indexed `.daxplugin` |
| `Directory.Build.props` | Shared props + `DaxAlgoSdkVersion` (the single SDK-version knob) |

## Compatibility

The strategies target **SDK `0.1.1-alpha`** (`DaxAlgoSdkVersion` in `Directory.Build.props`). DaxAlgo
Terminal loads a plugin only when its `plugin.json` `targetSdkVersion` matches the host SDK on
**major.minor** (pre-1.0: every minor bump is a breaking plugin contract). Bump `DaxAlgoSdkVersion`,
rebuild, and repackage when upgrading the host.

## Licensing

Strategy code is **AGPL-3.0** (see `LICENSE`) — the same license as the DaxAlgo Terminal open-source
core these strategies were factored out of. They build against the **MIT-licensed** DaxAlgo plugin SDK.
