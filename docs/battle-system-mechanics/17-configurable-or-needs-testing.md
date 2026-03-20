# 17. 仍需实测/建议配置化的部分

[返回目录](../battle-system-mechanics.md)

下面这些规则，**不要在第一版里硬编码成“绝对真理”**。

### 17.1 SP

目前已确认的硬规则：

- `initialAtBattleStart = 3`
- `max = 5`
- `basicGain = 1`
- `skillCost = 1`
- `ultimateCost = 0`

仍建议配置化的只有：

- `carryOverBetweenWaves`
- `max` 的战斗中改写/叠加顺序

建议配置：

```json
{
  "initialAtBattleStart": 3,
  "max": 5,
  "basicGain": 1,
  "skillCost": 1,
  "ultimateCost": 0,
  "carryOverBetweenWaves": true
}
```

其中前 5 项已经有较强来源支撑；`carryOverBetweenWaves` 仍建议作为可配置项。

### 17.2 Energy

建议把基础返能做成默认表：

```json
{
  "basic": 20,
  "enhancedBasic": 30,
  "skill": 30,
  "ultimate": 5,
  "kill": 10,
  "beingHitBuckets": [5, 10, 15, 20, 25],
  "followUpTypeEnergy": {
    "type1": 0,
    "type2": 5,
    "type3": 10
  }
}
```

其中 Basic / Enhanced Basic / Skill / Ultimate / Kill / ERR 乘算关系已经有较强公开来源。  
真正仍需录像/实测补齐的是：

- 敌方各攻击模板对应哪一个 `beingHitBucket`
- 多段攻击的返能时点
- 个别特殊动作的额外返能是否受 ERR 影响

### 17.3 Aggro

建议先配置：

```json
{
  "baseByPath": {
    "hunt": 3,
    "erudition": 3,
    "harmony": 4,
    "nihility": 4,
    "abundance": 4,
    "remembrance": 4,
    "elation": 4,
    "destruction": 5,
    "preservation": 6
  },
  "tauntOverridesNormalAggro": true,
  "lockOnOverridesTaunt": "scripted",
  "bounceIgnoresAggro": true
}
```

其中 Path 基础权重和 Bounce 不吃仇恨，已经有较强社区来源；真正仍需配置或脚本化的是 Lock-On 与 Taunt 的正式优先级。

### 17.4 同 AV 平手

建议先用：

```json
{
  "timelineTieBreaker": "spawnOrder"
}
```

---
