# 8. 各类伤害的独立规则

[返回目录](../battle-system-mechanics.md)

### 8.1 直伤（Direct Damage）

完全走第 7 章的常规公式。

### 8.2 追加攻击（Follow-Up Attack）

高确定项：

- Follow-Up Attack 是一类**自动触发的额外攻击**。  
- 它仍然是攻击实例，因此仍可走普通命中/伤害/削韧/触发流程。  
- 但它带有专属标签，因此会受“追加攻击增伤/易伤”影响。

推荐实现：

```ts
attack.tags = ['attack', 'follow_up']
```

### 8.3 反击（Counter）

高确定项：

- Counter 本质是自动触发的攻击。  
- 部分页面把它视为 Follow-Up Attack 的一个子类或相关分支。

建议：

```ts
attack.tags = ['attack', 'counter', 'follow_up']
```

如果后续某角色只吃“counter”不吃“follow_up”的特殊加成，再细拆。

### 8.4 普通 DoT

角色 DoT 采用常规伤害体系，但：

- 不暴击  
- 不视作普通 hit  
- 是否削韧通常为否  
- 受 DoT 专属增伤/易伤影响

推荐公式：

```text
DoTDamage = BaseDoT
          × 1
          × DMGBoostMult
          × WeakenMult
          × DEFMult
          × RESMult
          × VulnerabilityMult
          × DMGMitigationMult
          × BrokenMult
```

### 8.5 击破伤害（Break Damage）

高确定项：击破伤害与普通攻击伤害是独立体系。其特点：

- 主要受角色等级、击破特攻、目标最大 Toughness、元素基础倍率影响。  
- 不暴击。  
- 不吃普通 DMGBoost。  
- 吃 DEF、RES、Vulnerability、DMGMitigation、Broken 等目标乘区。

推荐骨架：

```text
BreakDamage = BreakBase
            × (1 + BreakEffect)
            × (1 + BreakDamageIncrease)
            × DEFMult
            × RESMult
            × VulnerabilityMult
            × DMGMitigationMult
            × BrokenMult
```

其中：

```text
MaxToughnessMult = 0.5 + TargetMaxToughness / 40
```

### 8.6 各属性击破基础倍率

高确定项：

- 物理：`2.0 × LevelMult × MaxToughnessMult`
- 火：`2.0 × LevelMult × MaxToughnessMult`
- 冰：`1.0 × LevelMult × MaxToughnessMult`
- 雷：`1.0 × LevelMult × MaxToughnessMult`
- 风：`1.5 × LevelMult × MaxToughnessMult`
- 量子：`0.5 × LevelMult × MaxToughnessMult`
- 虚数：`0.5 × LevelMult × MaxToughnessMult`

建议：`LevelMult` 做查表，而不是写公式。

### 8.7 击破异常（Break DoT / Break Control）

#### 物理（Bleed）

建议按两部分建模：

- 立即击破伤害  
- 后续 Bleed

Wiki 摘要给出：

- 普通敌人：`0.16 × TargetMaxHP`
- 精英/Boss：`0.07 × TargetMaxHP`
- 上限受 `2 × LevelMult × MaxToughnessMult` 约束

#### 火（Burn）

- 立即击破伤害 + Burn
- 基础 Burn 参考：`1 × LevelMult`

#### 雷（Shock）

- 立即击破伤害 + Shock
- 基础 Shock 参考：`2 × LevelMult`

#### 风（Wind Shear）

- 立即击破伤害 + Wind Shear
- 可叠层，基础与 `StackCount × LevelMult` 相关

#### 冰（Freeze）

高确定项：

- 被冻结单位在其应行动时失去该次行动。  
- 会承受 Ice Break 相关伤害。  
- 随后有“50% 提前下一次行动”的时序表现。

工程上建议把它拆成：

```text
附加 Frozen 状态
→ 当目标 turn would start 时：
    1. 消耗本次正常行动
    2. 结算冻结伤害/解除冻结
    3. 对其下次行动施加 50% Advance Forward
```

#### 量子（Entanglement）

高确定项：

- 有基础 `20%` 行动延后。  
- 下次轮到目标时附带延迟伤害。  
- 延后量受 Break Effect 影响。

建议做成：

- 立即延后 + 挂一个“下次行动前爆发”的状态。

#### 虚数（Imprisonment）

高确定项：

- 存在延后/控制表现，且 Break Effect 会影响其延后程度。  
- 但本轮没有拿到统一的干净总公式。

建议：

- 把虚数击破的延后量做成版本配置项。  
- 先用与社区一致的近似实现，等补实测后替换。

### 8.8 超击破（Super Break）

这部分目前最适合做“**社区高可信 + 引擎可配置**”。

常见社区实现骨架：

```text
SuperBreakDamage = LevelMult
                 × (ToughnessDamage / 30)
                 × (1 + BreakEffect)
                 × DEFMult
                 × RESMult
                 × VulnerabilityMult
                 × BrokenMult
                 × SpecificSuperBreakBonuses
```

高可信但未完全锁死的原因：

- 游戏版本中 Toughness 显示口径可能发生过变化。  
- 某些角色/状态会额外修改 Super Break 乘区。  
- 公开来源更偏社区实测而非官方完整公式。

实现建议：

```ts
interface SuperBreakConfig {
  enabled: boolean
  toughnessDisplayToInternalRatio: number
  denominator: number   // default 30
}
```

### 8.9 欢愉伤害（Elation DMG）

这部分属于较新的特殊伤害体系，上一版遗漏了。当前最强公开资料主要来自社区机制词条，但已经足够支撑引擎级建模。

高可信社区确认项：

- `Elation DMG` 是**独立伤害类别**，不是普通 `DMG Boost` 框架里的常规攻击伤害。  
- 它有单独公式分支，数值与 **Punchline、Elation(Stat)、角色等级**有关。  
- 它**不受普通 DMG Boost 影响**。  
- 它仍然会经过目标侧乘区：
  - `Weaken`
  - `DEF`
  - `RES`
  - `Vulnerability`
  - `DMG Mitigation`
  - `Broken`
- 它可以暴击。  
- 它存在专属 `Elation DMG Vulnerability`，因此不能直接并入普通易伤桶。

对模拟器，建议扩展伤害类别：

```ts
type DamageClass =
  | 'normal'
  | 'dot'
  | 'break'
  | 'super_break'
  | 'elation'
```

推荐骨架：

```text
ElationDamage = ElationBase
               × CritMult
               × PunchlineMult
               × MerrymakeMult
               × WeakenMult
               × DEFMult
               × RESMult
               × ElationVulnerabilityMult
               × DMGMitigationMult
               × BrokenMult
```

实现解释：

- `ElationBase` 应单独由 `AbilityMultiplier × LevelMultiplier × (1 + ElationStat)` 这一类字段构成。  
- 不默认乘入普通 `DMGBoostMult`。  
- 只有文本明确写“Elation DMG 提高”或“Elation DMG Vulnerability”时，才进入对应专属桶。  
- 若某次欢愉伤害同时具有元素属性，则元素只决定属性/抗性侧结算，不代表它自动吃普通属性伤害提高。

工程建议：

1. 给伤害包同时保留 `element` 与 `damageClass='elation'`。  
2. 不要把 `Elation Skill` 自动等同于 `Skill`、`Follow-Up Attack` 或 `Counter`。  
3. 所有与 Punchline / Merrymake / Certified Banger 相关的数值，最好做成独立资源与状态桶。

---
