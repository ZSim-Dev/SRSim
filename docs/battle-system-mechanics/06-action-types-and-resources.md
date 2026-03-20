# 6. 指令类型与资源系统

[返回目录](../battle-system-mechanics.md)

### 6.1 动作类型建议

至少支持这些动作标签：

- `BasicATK`
- `Skill`
- `Ultimate`
- `TalentTriggeredAction`
- `FollowUpAttack`
- `Counter`
- `SummonAction`
- `TechniqueOpeningEffect`
- `ExtraTurnAction`
- `JointAttack`（如后续要支持特殊联动）

动作标签不是表现用途，而是为了控制：

- 是否消耗 SP  
- 是否允许在额外回合中使用  
- 是否计入“追加攻击次数”  
- 是否吃某些专属增伤标签  
- 是否能作为触发器再次触发其它效果

### 6.2 SP（战技点）

这一块现在已经能确认一组足够硬的基础规则，剩下不确定的主要是**跨波次继承**与**上限变化类特效的叠加优先级**。  
建议实现为**有明确默认值的公共共享资源池**：

```ts
interface SkillPointState {
  current: number
  min: number
  max: number
  carryOverBetweenWaves: boolean
  initialAtBattleStart: number
}
```

高确定项：

- SP 是**队伍共享资源**，不是每个角色独立资源。  
- 队伍**默认最大 SP 为 5**。  
- 队伍**入战时初始 SP 为 3**。  
- 使用 **Basic ATK 会恢复 SP**。  
- 使用 **Skill 会消耗 SP**。  
- Ultimate 不属于常规“消耗 SP 的战技动作”。  
- 个别角色/效果可以**提高 Max SP**，因此 `max` 不能写死成常量。

因此，对通用模拟器，推荐把以下内容当作**默认引擎规则**：

- `initialAtBattleStart = 3`
- `max = 5`
- `BasicATK +1 SP`
- `Skill -1 SP`
- `Ultimate 0 SP`

实现建议：

- 不要把 `max=5` 写死在不可修改常量里；写成 `EngineConfig.spRules.baseMax`。  
- 把“基础规则”与“角色/效果改写上限”拆开。  
- 多波是否继承 SP 目前仍建议做配置项。  
- 如果目标是高保真实机复刻，这块仍建议补录像实测验证波次切换时序。

### 6.3 Energy（能量）

这一块现在可以确认一张**基础返能表**，但仍然缺少完整的“所有受击模板 / 多段攻击 / 特殊动作返能细则”统一表。  
因此建议做成：**基础公共规则 + 可覆盖的动作级配置**。

#### A. 引擎层

```ts
interface EnergyState {
  current: number
  max: number
  regenRate: number
}
```

#### B. 动作脚本层

把每个动作、受击、击杀、击破、特定天赋的能量收益都做成脚本事件：

- `OnUseBasicGainEnergy`
- `OnUseSkillGainEnergy`
- `OnHitGainEnergy`
- `OnKillGainEnergy`
- `OnBeingHitGainEnergy`
- `OnBreakGainEnergy`

高确定项：

- Basic Attack：基础回能 `20`  
- Enhanced Basic Attack：基础回能 `30`  
- Skill：基础回能 `30`  
- Ultimate：基础回能 `5`  
- 击杀敌人：基础回能 `10`  
- 角色在受击时会获得能量，且数值会**随敌方攻击类型浮动**。  
- 常见受击回能档位至少包括 `5 / 10 / 15 / 20 / 25`。  
- `Real Energy Regeneration = Base Energy Regeneration × Energy Regeneration Rate`  
- 一些效果会在战斗开始时、每波开始时或特定触发后给能量。  
- 终结技依赖能量阈值，不依赖正常行动条时点。

对 Follow-Up Attack，HoYoWiki 还给出三类基础回能：

- Type 1 = `0`
- Type 2 = `5`
- Type 3 = `10`

因此建议不要只给 FUA 一个统一返能常量，而是把其返能类型做成动作字段。

工程建议：

- 把基础返能表做成可配置 JSON，但默认值可以直接采用上面的已确认规则。  
- 不要让“受击返能”“技能返能”“额外返能”“FUA 分类返能”混在同一函数里。  
- 受击返能应由**敌方攻击模板**决定，而不是写成一个单值常量。

### 6.4 Toughness（弱点击破槽）

高确定项：

- Toughness 是**敌人专属属性**。  
- 只有使用敌方弱点属性攻击时才会削韧。  
- Toughness 归零触发 Weakness Break。  
- 敌人在其**下次行动轮到自己时**，恢复 Toughness 并解除 Broken 状态。

推荐结构：

```ts
interface ToughnessState {
  current: number
  max: number
  weaknesses: ElementType[]
  broken: boolean
  brokenBy?: ElementType
  brokenSourceUnitId?: string
}
```

---
