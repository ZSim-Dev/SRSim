# 7. 伤害计算总公式

[返回目录](../battle-system-mechanics.md)

### 7.1 常规伤害总式

综合 Wiki/Prydwen，可用于模拟器的稳定实现式：

```text
Damage = BaseDamage
       × CritMult
       × DMGBoostMult
       × WeakenMult
       × DEFMult
       × RESMult
       × VulnerabilityMult
       × DMGMitigationMult
       × BrokenMult
```

这是最适合工程拆分的结构。

### 7.2 BaseDamage（基础伤害）

推荐表达：

```text
BaseDamage = AbilityMultiplier × ScalingStat + FlatExtraDamage
```

其中 `ScalingStat` 可能是：

- ATK
- HP
- DEF
- 其它角色特定属性

如果技能本身有多段、每段倍率不同，则按 hit 分别计算。

### 7.3 Crit（暴击区）

```text
CritMult = 1 + CritDMG   // 若该 hit 暴击
CritMult = 1             // 否则
```

高确定项：

- 多段攻击逐段判暴击。  
- 普通角色 DoT 不暴击。  
- 击破伤害与超击破通常不暴击。

### 7.4 DMGBoost（增伤区）

建议把所有“伤害提高 %”做成统一加区，再按标签过滤：

- 全伤害提高
- 属性伤害提高
- 追加攻击伤害提高
- DoT 伤害提高
- 击破伤害提高（单独给 Break 使用）

普通实现：

```text
DMGBoostMult = 1 + ΣApplicableDamageBonuses
```

### 7.5 Weaken（弱化区）

这是偏敌方造成伤害下降用的区：

```text
WeakenMult = 1 - Weaken
```

### 7.6 DEF（防御区）

推荐工程公式：

```text
DEFMult = (AttackerLevel + 20)
        / ((TargetLevel + 20) × EffectiveDEFModifier + AttackerLevel + 20)
```

其中：

```text
EffectiveDEFModifier = max(0, 1 + DEFBonus - DEFReduction - DEFIgnore)
```

说明：

- `DEFReduction`：施加在目标身上的减防。  
- `DEFIgnore`：攻击者无视防御。  
- 二者同区，都会降低目标有效防御。

### 7.7 RES（抗性区）

推荐公式：

```text
EffectiveRES = clamp(TargetRES - RESPEN, -1.0, 0.9)
RESMult = 1 - EffectiveRES
```

说明：

- 下限 `-100%`、上限 `90%` 主要来自社区通行实现。  
- 如果后续拿到更权威版本，可替换 clamp。

### 7.8 Vulnerability（易伤 / 受伤提高区）

统一实现为：

```text
VulnerabilityMult = 1 + ΣApplicableTakenDamageBonuses
```

包括：

- 全属性受伤提高
- 特定属性受伤提高
- DoT 受伤提高
- 追加攻击受伤提高

### 7.9 DMG Mitigation（减伤区）

高确定项：多个减伤独立连乘：

```text
DMGMitigationMult = ∏(1 - mitigation_i)
```

不要把多个减伤直接线性相加。

### 7.10 Broken 状态乘区

高确定项：

- 目标未 Broken 时，常规入伤会吃一个 `0.9` 乘区。  
- 目标 Broken 时，该乘区回到 `1.0`。

推荐实现：

```text
BrokenMult = target.toughness?.broken ? 1.0 : 0.9
```

---
