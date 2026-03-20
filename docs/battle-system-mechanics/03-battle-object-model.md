# 3. 推荐的战斗对象模型

[返回目录](../battle-system-mechanics.md)

下面这个对象结构足够支撑绝大多数通用机制。

```ts
interface Unit {
  id: string
  side: 'ally' | 'enemy' | 'summon' | 'special'
  archetype: 'character' | 'enemy' | 'summon' | 'memosprite' | 'countdown' | 'transformed'

  level: number
  maxHp: number
  hp: number

  baseStats: StatBlock
  battleStats: StatBlock

  speedState: {
    currentSpd: number
    currentAg: number
    currentAv: number
  }

  energy: number
  maxEnergy: number

  toughness?: {
    current: number
    max: number
    weaknesses: ElementType[]
    broken: boolean
    brokenBy?: ElementType
  }

  actionState: {
    alive: boolean
    targetable: boolean
    selectable: boolean
    canAct: boolean
    isInExtraTurn: boolean
    hasQueuedUltimate: boolean
  }

  statuses: StatusInstance[]
  shields: ShieldInstance[]
  summons: string[]

  scriptHooks: ScriptHookMap
}
```

### 3.0 忆灵 / Memosprite 的特殊建模

这是上一版缺失但对新版本模拟器非常重要的子系统。当前资料足以支持一个**保守但可落地**的建模方式。

高确定/高可信项：

- 忆灵通常应视为**独立战斗实体**，而不是角色身上的纯状态标记。
- 至少部分忆灵明确拥有：
  - 独立 `SPD`
  - 独立 `HP`
  - 独立行动次数 / 生命周期
  - 独立忆灵技能或特殊动作
- 至少部分忆灵会被**100% Advance Forward**，这意味着它们拥有独立行动条位置。
- 忆灵的**可被选中性不是全局统一规则**：有的明确不可被选中，有的则更接近在场实体。
- 某些忆灵/忆灵相关倒计时对象明确写有“**换波时 Action Value 不重置**”，但当前不足以证明这是全体忆灵通则。

因此，模拟器推荐额外定义：

```ts
interface MemospriteState {
  ownerId: string
  initialSpd: number
  independentHp: boolean
  targetabilityMode: 'targetable' | 'untargetable' | 'scripted'
  actionResetOnWaveStart: 'reset' | 'keep' | 'scripted'
  resourceMode?: 'none' | 'charge' | 'custom'
}
```

实现原则：

1. **把忆灵作为 Unit 建模**，不要仅做主人技能的附带状态。
2. **目标可选性按实体文本决定**，不要假设所有忆灵都不可选中。
3. **波次 AV 是否保留按实体/效果文本决定**，不要做统一全局规则。
4. 若忆灵拥有独立资源（如 Charge），该资源应独立于普通 Energy 实现。

### 3.1 重要设计建议

1. **把召唤物也建模成 Unit**，不要把它们做成纯被动标记。
2. **把行动系统与技能系统解耦**：行动系统只决定“谁现在可以动”，技能系统决定“动的时候做什么”。
3. **把 Buff/Debuff 做成通用实例对象**，不要直接把效果写死在角色逻辑里。
4. **所有动作都走事件流**，例如：
   - `OnBattleStart`
   - `OnWaveStart`
   - `OnTurnStart`
   - `OnActionStart`
   - `OnHit`
   - `OnDamageDealt`
   - `OnBreak`
   - `OnTurnEnd`

---
