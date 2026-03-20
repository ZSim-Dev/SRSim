# 11. 仇恨与目标选择

[返回目录](../battle-system-mechanics.md)

### 11.1 当前确定度

这部分现在已经拿到一套**可直接实现的社区逆向公式**，但“Taunt 与 Lock-On 的正式优先级链”“敌人 AI 是否还有额外脚本权重”仍未完全锁定。  
最稳妥的策略是：**基础仇恨公式按社区逆向实现，强制指定类效果按脚本层覆盖。**

高确定/高可信项：

- Taunt（嘲讽）会覆盖普通仇恨优先级。  
- Lock On / 指定目标类效果会强制把某次特定行动绑定到目标。  
- 某些状态会让单位不可被选中，甚至不出现在行动序列中（例如 Departed / Backup 之类特殊状态）。  
- Bounce 攻击不受普通仇恨影响，而是均等随机命中候选目标。  
- 社区通用仇恨公式为：

```text
Aggro = BaseAggro × (1 + AggroModifier)
P(target) = Aggro_target / Σ Aggro_all_candidates
```

- 已有较完整的 Path 基础仇恨表：
  - Hunt = 3
  - Erudition = 3
  - Harmony = 4
  - Nihility = 4
  - Abundance = 4
  - Remembrance = 4
  - Elation = 4
  - Destruction = 5
  - Preservation = 6

### 11.2 建议的目标选择分层

敌方选目标建议按以下顺序：

```text
1. 过滤不可选中目标（死亡、离场、特殊不可选中态）
2. 若技能本身是 Bounce 段，则在候选里均等随机，不走普通仇恨
3. 应用强制锁定类效果（Lock On / forced target）
4. 应用 Taunt 类效果
5. 在剩余候选中按 aggro weight 抽样或排序
6. 若技能有特殊规则（最低血/相邻/随机/有弱点优先），再覆盖默认逻辑
```

### 11.3 推荐配置结构

```ts
interface TargetingConfig {
  baseAggroWeightsByRole?: Record<string, number>
  tauntOverridesNormalAggro: boolean
  lockOnOverridesTaunt: boolean | 'scripted'
  bounceIgnoresAggro: boolean
  defaultTieBreaker: 'slot' | 'spawnOrder' | 'random'
}
```

### 11.4 若你现在就要实现

可采用以下“接近可还原”的方案：

- 普通敌方攻击：按仇恨权重随机。  
- Base Aggro 默认先按 Path 表给值。  
- 嘲讽：直接强制目标。  
- Lock-On：默认视为“覆盖普通仇恨”的脚本化指定目标。  
- Bounce：跳过普通仇恨，均等随机。  
- 特殊 Boss 技能：按技能脚本单独指定目标规则。

### 11.5 仍未完全锁定的点

- Taunt 与 Lock-On 的**正式优先级**，当前更适合设为脚本或配置项。  
- 多个 Lock-On 并存时如何覆盖。  
- 多来源 `AggroModifier` 的严格叠加顺序。  
- 某些 Boss 是否在普通仇恨抽样之外还带有额外 AI 规则。

---
