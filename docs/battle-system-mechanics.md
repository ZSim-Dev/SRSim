# 崩坏：星穹铁道战斗系统机制详解

> 来源：`~/work/崩坏星穹铁道战斗系统机制报告.md`
>
> 说明：这是为 `SRSim` 拆分后的文档入口页。原始长文已按一级章节拆到 `docs/battle-system-mechanics/` 目录，便于按主题查阅与后续维护。

> 目标：整理到足以直接实现一个战斗模拟器的粒度。
> 范围：聚焦**通用战斗引擎**，不展开每个角色、遗器、光锥、命途祝福的全量专属脚本。
> 方法：把内容分为 **A. 高确定规则**、**B. 高可信社区结论**、**C. 仍需实测/版本配置项**。
> 结论使用优先级：**若 A 与 B 冲突，以 A 为准；若缺 A，则先用 B 并做可配置实现；C 不建议硬编码死。**

---

## 章节目录

- [0. 使用说明](./battle-system-mechanics/00-usage.md)
- [1. 资料可信度分层](./battle-system-mechanics/01-confidence-levels.md)
- [2. 核心术语与统一记号](./battle-system-mechanics/02-core-terms-and-notation.md)
- [3. 推荐的战斗对象模型](./battle-system-mechanics/03-battle-object-model.md)
- [4. 战斗流程总览](./battle-system-mechanics/04-battle-flow-overview.md)
- [5. 回合与行动条机制](./battle-system-mechanics/05-turn-and-action-value-system.md)
- [6. 指令类型与资源系统](./battle-system-mechanics/06-action-types-and-resources.md)
- [7. 伤害计算总公式](./battle-system-mechanics/07-damage-formula.md)
- [8. 各类伤害的独立规则](./battle-system-mechanics/08-special-damage-rules.md)
- [9. 生存相关机制](./battle-system-mechanics/09-survivability-systems.md)
- [10. 弱点与属性系统](./battle-system-mechanics/10-weakness-and-elements.md)
- [11. 仇恨与目标选择](./battle-system-mechanics/11-aggro-and-targeting.md)
- [12. Buff / Debuff / 控制效果时序](./battle-system-mechanics/12-status-timing.md)
- [13. 追加攻击、反击、召唤物、倒计时对象](./battle-system-mechanics/13-follow-up-counter-summons-countdown.md)
- [14. 事件驱动实现建议](./battle-system-mechanics/14-event-driven-architecture.md)
- [15. 推荐的最小伪代码](./battle-system-mechanics/15-minimal-pseudocode.md)
- [16. 如果你要“直接开始写模拟器”，推荐的模块拆分](./battle-system-mechanics/16-recommended-module-split.md)
- [17. 仍需实测/建议配置化的部分](./battle-system-mechanics/17-configurable-or-needs-testing.md)
- [18. 推荐测试用例](./battle-system-mechanics/18-test-cases.md)
- [19. 最终建议：如何从这份文档落地成“可运行模拟器”](./battle-system-mechanics/19-how-to-land-this-into-a-simulator.md)
- [20. 参考资料与来源](./battle-system-mechanics/20-references.md)
- [21. 当前报告的结论强度总结](./battle-system-mechanics/21-conclusion-strength-summary.md)
- [22. 一句话总结](./battle-system-mechanics/22-one-line-summary.md)

## 目录结构

```text
docs/
  battle-system-mechanics.md
  battle-system-mechanics/
    00-usage.md
    01-confidence-levels.md
    02-core-terms-and-notation.md
    03-battle-object-model.md
    04-battle-flow-overview.md
    05-turn-and-action-value-system.md
    06-action-types-and-resources.md
    07-damage-formula.md
    08-special-damage-rules.md
    09-survivability-systems.md
    10-weakness-and-elements.md
    11-aggro-and-targeting.md
    12-status-timing.md
    13-follow-up-counter-summons-countdown.md
    14-event-driven-architecture.md
    15-minimal-pseudocode.md
    16-recommended-module-split.md
    17-configurable-or-needs-testing.md
    18-test-cases.md
    19-how-to-land-this-into-a-simulator.md
    20-references.md
    21-conclusion-strength-summary.md
    22-one-line-summary.md
```

## 使用方式

- 想快速了解整体结论时，先读本页。
- 想看具体机制时，直接跳到对应分章文件。
- 想继续实现模拟器时，可优先阅读“回合与行动条机制”“指令类型与资源系统”“伤害计算总公式”“事件驱动实现建议”等章节。
