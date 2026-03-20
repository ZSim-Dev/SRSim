# SRSim

基于 `docs/battle-system-mechanics.md` 中的最小战斗切片，这个仓库当前已经提供了一个可运行的 CLI 战斗 demo：1 名最小角色对战 1 名最小敌人。

## 最小战斗 Demo

运行方式：

```bash
.venv/bin/python src/main.py
```

你会看到：

- 战斗总回合数
- 胜负结果
- 双方剩余 HP / Energy
- 每次行动的战斗日志

当前 demo 复用了现有的 `srsim.core` 引擎模块：

- `srsim.core.timeline`：按速度推进行动条
- `srsim.core.ai`：最小行动决策（终结技 > 战技 > 普攻）
- `srsim.core.actions` / `damage`：执行动作与伤害结算
- `srsim.core.engine`：驱动整场战斗直到一方被击败

## 相关文档

- 总入口：`docs/battle-system-mechanics.md`
- 最小伪代码：`docs/battle-system-mechanics/15-minimal-pseudocode.md`
- 落地建议：`docs/battle-system-mechanics/19-how-to-land-this-into-a-simulator.md`
