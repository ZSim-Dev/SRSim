# 14. 事件驱动实现建议

[返回目录](../battle-system-mechanics.md)

如果你想做可扩展模拟器，最推荐的不是“巨型 if-else”，而是**事件驱动**。

### 14.1 关键事件列表

```text
OnBattleStart
OnWaveStart
OnBeforeActionOrderResolve
OnTurnStart
OnActionStart
OnBeforePayCost
OnAfterPayCost
OnBeforeTargetSelect
OnAfterTargetSelect
OnBeforeHit
OnHit
OnDamageCalculated
OnDamageDealt
OnHealDone
OnShieldApplied
OnToughnessDamage
OnWeaknessBreak
OnStatusApply
OnStatusExpire
OnKill
OnUnitDowned
OnRevive
OnActionEnd
OnTurnEnd
OnUltimateQueued
OnUltimateInserted
```

### 14.2 为什么必须事件驱动

因为 HSR 的技能文本大量是下面这种：

- “当友方攻击后……”  
- “当敌方进入弱点击破时……”  
- “在我方回合开始时……”  
- “若本次攻击为追加攻击……”  
- “每波开始时……”

这些天然是事件监听，不适合写死在大流程里。

---
