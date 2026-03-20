# 5. 回合与行动条机制

[返回目录](../battle-system-mechanics.md)

这是模拟器最核心的部分。

### 5.1 行动条的数学定义

高确定公式（KQM）：

- 默认 `Action Gauge = 10000`
- `Base AV = 10000 / SPD`
- `Current AG = Current AV × Current SPD`
- 仅速度变化时：

```text
New AV = Current AV × Current SPD / New SPD
```

- 一般形式（同时包含速度变化与拉条/推条）：

```text
New AV = Current AV × Current SPD / New SPD
       - 10000 × (AdvanceForward% - ActionDelay%) / New SPD
```

### 5.2 正常回合推进

推荐实现方式：

1. 维护每个单位 `currentAV`。  
2. 每次取 `currentAV` 最小的单位行动。  
3. 把这个最小 AV 视为“本次流逝的时间片”。  
4. 全部正常排队单位的 `currentAV -= minAV`。  
5. 当前单位进入 `AV = 0` 的行动态。  
6. 其行动结束后，重新赋予下次行动的基准 AV（或按修正后的 AG/AV 状态继续）。

等价实现也可以是维护 `AG`，但在写逻辑时 `AV` 更直观。

### 5.3 速度变化（SPD Buff/Debuff）

高确定公式：

```text
New AV = Current AV × Current SPD / New SPD
```

解释：

- 已经排队到一半的单位如果被加速，不是“重置为新 Base AV”，而是**把剩余 AV 按新速度换算**。  
- 因此速度 Buff 的收益与“何时上 Buff”相关。

### 5.4 行动提前（Advance Forward）

高确定公式：

```text
New Action Gauge = max(0, CurrentActionGauge - 10000 × AdvanceForward%)
```

再换算回 AV：

```text
New AV = New AG / Current SPD
```

特例：

- **100% Advance Forward**：直接把 AV 置 0，并尽快行动。  
- 但它仍然**晚于已排队的终结技与被动结算**。  
- 连续多个 100% 拉条时：**最后一个被 100% 拉条的单位先行动**。

### 5.5 行动延后（Action Delay）

与拉条方向相反，本质是增加 AG。高确定表达：

```text
New Action Gauge = max(0, CurrentActionGauge - 10000 × (AdvanceForward% - ActionDelay%))
```

所以如果只有延后：

```text
New Action Gauge = CurrentActionGauge + 10000 × ActionDelay%
```

注意：

- “减速”与“延后”不是同一个效果。  
- “减速”改变 `SPD`；“延后”改变 `AG / AV`。  
- 量子/虚数相关效果里，常常同时出现控制、延后、减速中的一种或多种。

### 5.6 额外回合（Extra Turn）

高确定项：

- Extra Turn 是**脱离正常行动条**的一次额外行动。  
- **不会消耗原本剩余正常轮次。**  
- **不会改变单位在行动条上的原位置。**  
- **状态效果不会在 Extra Turn 中递减。**  
- **额外回合中不能施放终结技。**

因此，推荐实现模型：

```text
保存单位当前正常行动条位置
→ 设置 unit.isInExtraTurn = true
→ 执行一次独立行动
→ 不扣正常回合层数/持续时间
→ 结束后恢复原行动条位置
```

### 5.7 终结技插队（Ultimate Insertion）

高确定项：

- 终结技可在几乎任意时点使用。  
- 它会在**当前攻击动作完成后**插入结算。  
- 它不是通过“正常 AV 推进”获得的。

推荐实现优先级：

```text
当前 hit/动作结算完成
→ 检查 queued ultimates
→ 逐个执行满足条件的终结技插队
→ 再回到正常行动条
```

注意：

- “当前动作完成后”这件事非常重要。不要在单个 hit 尚未结算完成时硬中断。  
- 玩家常利用“先普通动作，再立刻终结技”保留本回合 Buff，这说明“回合结束”的定义晚于动作声明、甚至晚于大部分伤害结算。

### 5.8 伏击（Ambush）

高确定项：

- 伏击时，所有角色统一后移 `20 AV`。  
- 该效果与 SPD 或其他 AG 修改器无关。

### 5.9 同 AV 平手

当前没有拿到足够高质量的统一文档。  
**不要写死猜测规则。** 建议：

- 用一个可配置 tie-breaker。  
- 默认可先用“进入队列时间 / 单位创建顺序 / 原始站位”之一。  
- 等录像与实测补齐后再定。

### 5.10 召唤物与倒计时对象的行动条

高确定项：

- 至少有一部分召唤物拥有**独立速度、独立行动条、独立行动次数或倒计时对象**。  
- 因此它们不能只建模成“动画性质的附属攻击”。

推荐实现：

- 召唤物也是 `Unit`。  
- 倒计时对象也是 `Unit`，但技能列表可能为空，只在 `OnTurnStart`/`OnActionStart` 做特殊脚本。

---
