# 2. 核心术语与统一记号

[返回目录](../battle-system-mechanics.md)

建议在模拟器里统一使用以下命名：

### 2.1 单位（Unit）

一个可参与战斗结算的对象。包括：

- 角色
- 敌人
- 召唤物
- 倒计时对象（如部分特殊机制在行动条上显示的 countdown）
- 某些临时形态对象

### 2.2 属性（Stats）

分为四层：

1. **基础属性（Base Stats）**：角色面板基础值、等级成长、敌人模板值。  
2. **面板属性（Displayed Stats）**：装备/词条/被动常驻后。  
3. **战斗态属性（Battle Stats）**：进入战斗后叠加 Buff/Debuff 后的即时值。  
4. **派生属性（Derived Stats）**：由战斗态属性临时计算出来的值，如 `DEFMult`、`RESMult`、`CurrentAV`。

### 2.3 AV / AG / SPD

- `SPD`：速度。  
- `AG`：Action Gauge，行动槽总量。KQM 体系中默认基准值是 `10000`。  
- `AV`：Action Value，可理解为“距离下次行动还剩多少时间”。行动序列按 **AV 从低到高** 排，**AV 最低者先行动**。

### 2.4 Turn / Action / Extra Turn

建议区分三类概念：

- **Normal Turn（正常回合）**：来自正常行动条推进。  
- **Extra Turn（额外回合）**：不改变原行动条位置，不消耗原正常轮次。  
- **Inserted Action（插队动作）**：如终结技，它不是普通 AV 推进得到，而是在结算窗口插入。

### 2.5 Break / Broken / Toughness

- `Toughness`：敌人专属韧性条。  
- `Weakness Break`：韧性归零触发的事件。  
- `Broken`：被击破后处于“破韧状态”的时段，持续到该敌人下次轮到自己行动时恢复。

---
