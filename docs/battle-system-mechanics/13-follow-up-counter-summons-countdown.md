# 13. 追加攻击、反击、召唤物、倒计时对象

[返回目录](../battle-system-mechanics.md)

### 13.0 Aha Instant / 啊哈时刻与 Elation Skill

这部分是欢愉体系的关键执行窗口，和普通追加攻击、Extra Turn 都有关联，但**不能直接等同**。

高可信社区确认项：

- `Aha Instant` 是一个专用结算窗口：当条件满足时，Aha 进入行动并触发一段连续结算。  
- 在 `Aha Instant` 期间，所有可用 `Elation Skill` 的单位会各施放 1 次 `Elation Skill`。  
- 若当前没有任何可施放的 `Elation Skill`，则 Aha 会改为使用默认行为（如词条中的 `Let There Be Laughter`）。  
- `Elation Skill` 的执行顺序由固定的参与顺序/Participant ID 决定。  
- `Aha Instant` 结束后，会结算本次计入 Punchline 的后处理，并清空 Punchline。  
- 某些效果可令 Aha **立即获得 1 次 extra turn**；这改变的是 Aha 的行动时点，而不是把所有 Elation Skill 自动转成普通 follow-up。

因此，推荐的引擎模型不是：

```text
Aha Instant = 一串普通 Follow-Up Attack
```

而应是：

```text
Aha action
→ open AhaInstant window
→ gather eligible ElationSkill participants
→ execute ElationSkill list in participant order
→ apply end-of-instant rewards / cleanup
→ clear Punchline (if effect text says so)
→ close window
```

重要区分：

- `Elation Skill` **不应默认标记为 Follow-Up Attack**。  
- `Aha Instant` **不等于**普通 Extra Turn；它更像“在 Aha 行动内打开的专用多角色结算窗口”。  
- 只有当某个效果文本明确写“立即获得 1 次 extra turn”时，才对 Aha 本体施加 Extra Turn 语义。

推荐数据结构：

```ts
interface AhaState {
  punchline: number
  instantOpen: boolean
  merrymake?: number
}

interface ElationSkillParticipant {
  unitId: string
  participantId: number
  canCast: boolean
}
```

### 13.1 追加攻击

高确定项：

- 追加攻击是自动触发的攻击，不是“正常回合动作声明”的一部分。  
- 它仍然会创建一条完整攻击事件流：选目标、命中、伤害、削韧、触发后效。

### 13.2 反击

建议本质上与追加攻击同引擎实现，仅多一个 `counter` 标签。

### 13.3 召唤物

高确定项：

- 至少部分召唤物有：
  - 独立 SPD  
  - 独立行动条  
  - 独立行动次数 / 层数 / 优先目标逻辑

建议实现：

```ts
interface SummonUnit extends Unit {
  ownerId: string
  durationMode: 'indefinite' | 'turn_count' | 'action_count' | 'special'
  remainingActions?: number
}
```

### 13.4 倒计时对象

某些机制会在行动条上生成“倒计时对象”，它的本质是：

- 参与行动顺序  
- 到点触发特殊脚本  
- 不一定能普攻/战技

不要把它塞进角色本体的附属字段里，最好单独当作 `Unit`。

---
