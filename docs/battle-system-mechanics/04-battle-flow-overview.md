# 4. 战斗流程总览

[返回目录](../battle-system-mechanics.md)

推荐的宏观流程：

```text
进入战斗
→ 触发 Battle Start 事件
→ 若为伏击/先制等特殊开场，调整 AV/状态
→ 进入主循环：
    1. 处理已排队终结技 / 被动插队事件
    2. 选择最小 AV 的单位作为下一个正常行动者
    3. 推进全体 AV（或等价地减少最小 AV）
    4. 执行 Turn Start / Action Start
    5. 执行动作（普攻/战技/终结技/追加攻击/反击/召唤物动作）
    6. 处理命中、伤害、削韧、状态附加、击破
    7. 处理动作结束触发
    8. 处理 Turn End 与状态时长递减
→ 若整波敌人清空，进入 Wave Start
→ 若胜负满足条件，退出
```

### 4.1 战斗开始（Battle Start）

高确定项：

- 一些 Technique 明确写的是“**at the start of the next battle**”，因此**战前技不是即时战斗中事件，而是入战时注入状态/伤害/控制/位移**。  
- 终结技可以在战斗开始时、尚未扣除 AV 前使用。  
- 若发生 **Ambush（伏击）**，全队统一**后移 20 AV**，且这项修正**不依赖 SPD 或其他 AG 修正**。

### 4.2 波次开始（Wave Start）

高确定项：

- “每波开始时”是独立事件窗口，不等价于 Battle Start。  
- 一些效果明确写“at the start of each wave”。  
- 某些倒计时对象/特殊机制**不会在每波开始时重置 AV**，需要按效果文本单独判断。

### 4.3 单次行动生命周期

建议拆成：

```text
TurnStart
→ ActionDeclare
→ CostPay
→ TargetSelect
→ HitSequence(可多段)
→ Damage/Heal/Shield/Break/ApplyStatus
→ AfterActionTriggers
→ TurnEnd
```

这能避免角色脚本因为“触发时点不同”而纠缠。

---
