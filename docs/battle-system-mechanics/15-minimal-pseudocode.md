# 15. 推荐的最小伪代码

[返回目录](../battle-system-mechanics.md)

### 15.1 主循环

```ts
while (!battle.isFinished()) {
  processQueuedInsertedActions() // ultimates, forced passives, extra actions

  const actor = getNextNormalActorByMinAV()
  advanceTimelineTo(actor)

  startTurn(actor)

  if (actor.actionState.canAct) {
    const action = actor.controller.chooseAction(battle)
    executeAction(actor, action)
  }

  endTurn(actor)

  if (battle.waveCleared()) {
    startNextWave()
  }
}
```

### 15.2 推进行动条

```ts
function advanceTimelineTo(actor: Unit) {
  const dt = actor.speedState.currentAv

  for (const unit of battle.normalTimelineUnits()) {
    unit.speedState.currentAv = Math.max(0, unit.speedState.currentAv - dt)
    unit.speedState.currentAg = unit.speedState.currentAv * unit.speedState.currentSpd
  }
}
```

### 15.3 速度变化

```ts
function recalcAVOnSpeedChange(unit: Unit, newSpd: number) {
  const currentAv = unit.speedState.currentAv
  const currentSpd = unit.speedState.currentSpd

  unit.speedState.currentAv = currentAv * currentSpd / newSpd
  unit.speedState.currentSpd = newSpd
  unit.speedState.currentAg = unit.speedState.currentAv * newSpd
}
```

### 15.4 行动提前/延后

```ts
function modifyActionGauge(unit: Unit, advancePct: number, delayPct: number) {
  const currentAg = unit.speedState.currentAg
  const newAg = Math.max(0, currentAg - 10000 * (advancePct - delayPct))
  unit.speedState.currentAg = newAg
  unit.speedState.currentAv = newAg / unit.speedState.currentSpd
}
```

### 15.5 Extra Turn

```ts
function grantExtraTurn(unit: Unit) {
  battle.extraTurnStack.push({
    unitId: unit.id,
    preservedAv: unit.speedState.currentAv,
    preservedAg: unit.speedState.currentAg,
  })
}

function executeExtraTurn(unit: Unit) {
  unit.actionState.isInExtraTurn = true
  // 禁止终结技，状态不 tick
  const action = unit.controller.chooseExtraTurnAction(battle)
  executeAction(unit, action)
  unit.actionState.isInExtraTurn = false
}
```

### 15.6 普通伤害结算

```ts
function calcNormalDamage(ctx: DamageContext): number {
  const base = ctx.abilityMultiplier * ctx.scalingStat + ctx.flatExtraDamage
  const crit = ctx.canCrit && ctx.didCrit ? (1 + ctx.critDmg) : 1
  const dmgBoost = 1 + sumApplicableDamageBonuses(ctx)
  const weaken = 1 - ctx.target.weaken
  const defMult = calcDEFMult(ctx)
  const resMult = calcRESMult(ctx)
  const vulnMult = 1 + sumApplicableVulnerabilities(ctx)
  const mitigationMult = multiplyMitigations(ctx.target)
  const brokenMult = ctx.target.isBroken ? 1.0 : 0.9

  return base * crit * dmgBoost * weaken * defMult * resMult * vulnMult * mitigationMult * brokenMult
}
```

### 15.7 击破伤害结算

```ts
function calcBreakDamage(ctx: BreakContext): number {
  const breakBase = calcBreakBase(ctx.element, ctx.attacker.level, ctx.target.maxToughness)
  const breakEffectMult = 1 + ctx.attacker.breakEffect
  const breakDmgIncrease = 1 + ctx.attacker.breakDamageIncrease
  const defMult = calcDEFMult(ctx)
  const resMult = calcRESMult(ctx)
  const vulnMult = 1 + sumApplicableVulnerabilities(ctx)
  const mitigationMult = multiplyMitigations(ctx.target)
  const brokenMult = ctx.target.isBroken ? 1.0 : 0.9

  return breakBase * breakEffectMult * breakDmgIncrease * defMult * resMult * vulnMult * mitigationMult * brokenMult
}
```

---
