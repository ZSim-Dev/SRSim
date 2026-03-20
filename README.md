# SRSim

一个面向《崩坏：星穹铁道》的 CLI 战斗模拟器原型。

## 当前引擎约定

- 时间线采用 `AV/AG` 模型，默认基础行动槽为 `10000`，行动顺序按最小 `AV` 决定。
- 速度变化会按照剩余 `AV × 旧速度 / 新速度` 重新换算，而不是简单重置回合。
- 行动提前 / 延后通过修改 `AG` 实现，支持与速度变化独立组合。
- 伤害结算已拆出基础乘区：基础伤害、暴击、增伤、弱化、防御、抗性、易伤、减伤与 Broken 乘区。
- `Unit` 已预留 Toughness 与基础战斗修正字段，便于继续扩展击破、状态与更复杂脚本层。

## 后续建议

- 补完事件总线，把 Battle Start、Wave Start、Turn Start、Weakness Break 等时点抽成统一钩子。
- 将 SP、Energy、Aggro 与 Super Break 细节配置化，避免第一版硬编码过死。
- 在角色脚本层继续扩展 Follow-Up、Extra Turn、Summon 与更复杂的目标选择逻辑。
