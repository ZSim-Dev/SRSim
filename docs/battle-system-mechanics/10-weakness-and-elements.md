# 10. 弱点与属性系统

[返回目录](../battle-system-mechanics.md)

### 10.1 属性类型

标准元素：

- Physical
- Fire
- Ice
- Lightning
- Wind
- Quantum
- Imaginary

### 10.2 弱点命中与削韧

高确定项：

- 任何属性都能对 HP 造成伤害。
- **只有匹配敌人弱点属性的攻击** 才会削减 Toughness。
- Toughness 归零触发 Weakness Break。
- Weakness Break 会：
  1. 造成一次 Break Damage
  2. 使敌人行动延后 `25%`
  3. 以 `150%` 基础概率附加对应属性的击破异常/控制
  4. 进入 Broken 状态

### 10.3 Broken 状态恢复

高确定项：

- 敌人在其**下次轮到自己行动**时恢复 Toughness。
- 这意味着 Broken 持续时间取决于对方什么时候再轮到行动，而不是固定秒数或固定回合数。

### 10.4 无视弱点削韧 / 彩色削韧 / 特殊削韧

这类机制在角色脚本层很常见，但引擎最好抽象成：

```ts
interface ToughnessDamagePacket {
  amount: number
  element: ElementType
  ignoresWeaknessRequirement?: boolean
  weaknessBreakEfficiencyMultiplier?: number
}
```

否则后续很难支持“无视弱点削韧”“彩色削韧”“削韧效率提高”等效果。

---
