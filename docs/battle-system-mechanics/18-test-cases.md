# 18. 推荐测试用例

[返回目录](../battle-system-mechanics.md)

你写模拟器后，至少要拿下面这些 case 回归：

### 18.1 纯速度验证

- A：100 SPD  
- B：125 SPD  
- 无任何拉条/减速

验证：同样 AV 时间里，B 的行动次数更多，接近 KQM 提示的“100 SPD 4 动时，125 SPD 约 5 动”的关系。

### 18.2 中途加速

- 单位剩余 AV 不为 0 时获得速度 Buff

验证：不是重置为新 Base AV，而是按 `CurrentAV × CurrentSPD / NewSPD` 换算。

### 18.3 100% 拉条

验证：

- AV 立刻归 0  
- 已排队终结技/被动优先  
- 连续多个 100% 拉条时最后被拉者先动

### 18.4 Extra Turn

验证：

- 不改变原行动条位置  
- 不递减状态  
- 不能放终结技

### 18.5 Weakness Break

验证：

- 归零时立刻造成击破伤害  
- 行动延后 25%  
- 进入 Broken  
- 在目标下次轮到自己行动时恢复 Toughness

### 18.6 Broken 乘区

验证：

- 未 Broken 时 `BrokenMult = 0.9`  
- Broken 时 `BrokenMult = 1.0`

### 18.7 多段攻击

验证：

- 每段独立暴击  
- 每段独立触发 on-hit  
- 但动作结束触发只在整段动作完成后统一处理

### 18.8 战前技 / 每波开始

验证：

- Battle Start 与 Wave Start 是两个独立事件  
- 某些状态只在入战触发，不会每波重置

---
