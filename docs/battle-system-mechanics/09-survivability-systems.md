# 9. 生存相关机制

[返回目录](../battle-system-mechanics.md)

### 9.1 治疗（Healing）

推荐公式：

```text
Healing = (ScalingStat × HealRatio + FlatHeal)
        × (1 + OutgoingHealingBoost + IncomingHealingBoost - IncomingHealingReduction)
```

建议把“治疗加成”与“被治疗加成/降低”拆开处理，不要混成一个字段。

### 9.2 护盾（Shield）

推荐公式：

```text
ShieldValue = (ScalingStat × ShieldRatio + FlatShield)
            × (1 + ShieldBonus)
```

建议：

- 护盾是一个或多个 `ShieldInstance` 的栈，不一定是一个总数字。  
- 这样才能处理：来源不同、持续时间不同、是否可刷新不同。

### 9.3 受击顺序建议

一次 hit 结算顺序建议为：

```text
计算原始伤害
→ 应用减伤/易伤/防御/抗性
→ 护盾吸收
→ 扣除生命
→ 检查濒死/死亡/复活
→ 触发受击后事件
```

### 9.4 倒地、濒死、复活

这部分多为角色脚本层，但引擎要预留通用钩子：

- `BeforeLethalDamage`
- `OnDowned`
- `OnRevive`
- `OnLeaveField`

否则后续很难支持“锁血”“延迟死亡”“一次性复活”等机制。

---
