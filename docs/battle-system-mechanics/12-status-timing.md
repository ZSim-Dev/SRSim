# 12. Buff / Debuff / 控制效果时序

[返回目录](../battle-system-mechanics.md)

### 12.1 通用状态对象

推荐结构：

```ts
interface StatusInstance {
  id: string
  kind: 'buff' | 'debuff' | 'control' | 'other'
  sourceUnitId: string
  ownerUnitId: string

  dispellable: boolean
  removableByCleanse: boolean
  stackable: boolean
  maxStacks?: number
  stacks: number

  durationMode: 'turns' | 'actions' | 'until_trigger' | 'permanent'
  remainingTurns?: number
  tickTiming?: 'source_turn_start' | 'source_turn_end' | 'owner_turn_start' | 'owner_turn_end' | 'special'

  tags: string[]
  params: Record<string, number | string | boolean>
}
```

### 12.2 状态递减时机

高确定项：

- 状态持续时间往往写在具体效果文本里，例如“在某人的回合开始时减少 1”。
- 因此**不能假设所有状态都在 owner turn end 递减**。
- Extra Turn 中状态**不递减**。

工程建议：

- 给每个状态显式写 `tickTiming`。
- 没有明确证据时，不要把它默认成统一时点。

### 12.3 驱散/净化

高确定项：

- Debuff 一般可驱散，除非特别注明不可驱散。
- Buff 移除、Debuff 移除都存在。
- 某些状态虽然归类为 Debuff，但文本明确“不可移除”。

### 12.4 叠层、刷新、覆盖

目前公开统一的“通用叠层规则表”不够强，因此推荐按每个状态显式声明：

```ts
stackPolicy: 'refresh' | 'independent_instances' | 'add_stacks' | 'replace_weaker' | 'replace_stronger' | 'no_stack'
```

### 12.5 控制类效果

必须单独支持：

- Freeze
- Entanglement
- Imprisonment
- Taunt
- Forced target / Lock On
- Special cannot act / cannot be targeted
- Time Stop（某些特殊战前/角色机制）

---
