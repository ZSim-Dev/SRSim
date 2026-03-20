# 16. 如果你要“直接开始写模拟器”，推荐的模块拆分

[返回目录](../battle-system-mechanics.md)

```text
battle/
  engine.ts                // 主循环
  timeline.ts              // SPD / AV / 插队 / Extra Turn / summon timeline
  events.ts                // 事件总线
  targeting.ts             // 目标选择与仇恨
  damage.ts                // 常规伤害 / DoT / Break / Super Break
  toughness.ts             // 削韧、击破、Broken 恢复
  statuses.ts              // Buff/Debuff/控制/驱散/递减
  resources.ts             // HP / Shield / SP / Energy
  actions.ts               // 动作声明/消耗/目标/多段 hit
  scripts/
    character/*.ts         // 角色脚本
    enemy/*.ts             // 敌人脚本
  config/
    engine-version.json
    energy-rules.json
    sp-rules.json
    aggro-rules.json
```

这样做的好处是：你暂时不确定的规则（SP、Energy、Aggro）可以先放进 config，不阻塞主引擎开发。

---
