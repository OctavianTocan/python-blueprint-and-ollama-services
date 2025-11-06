# Blueprint: BP_SimpleCharacter

## At a glance
- Variables: 0
- Graphs: 3
- Event Handlers: 1
- Unique Calls: 2

## Logic Flows
### BP_SimpleCharacter (Utility Graph)
Entry points: `OnDeath`. Invokes `Actor::Destroy`, `Character::Jump`. Writes `Health`. Notes: Game starts - initialize.
- Calls: Actor::Destroy, Character::Jump
- Writes: Health
- Entry Points: OnDeath
### DeathEvent (Utility Graph)
Entry points: `OnDeath`. Invokes `Actor::Destroy`. Notes: Custom event fired when character dies.
- Calls: Actor::Destroy
- Entry Points: OnDeath
### EventGraph (Event Graph)
Entry points: `EventGraph`. Invokes `Character::Jump`. Writes `Health`. Notes: Game starts - initialize.
- Calls: Character::Jump
- Writes: Health
- Entry Points: EventGraph

## Graphs
### Event Graph
- **EventGraph**
  - Entry Points: `EventGraph`
  - Calls: `Character::Jump`
  - Writes: `Health`
  - Notes:
    - Game starts - initialize
    - Make character jump
    - Character initialization sequence
  - Node Mix: Event ×1, CallFunction ×1, VariableSet ×1, Comment ×1
### Utility Graph
- **BP_SimpleCharacter**
  - Entry Points: `OnDeath`
  - Calls: `Actor::Destroy`, `Character::Jump`
  - Writes: `Health`
  - Notes:
    - Game starts - initialize
    - Make character jump
    - Character initialization sequence
    - … (+2 more)
  - Node Mix: CallFunction ×2, Event ×1, VariableSet ×1, Comment ×1, CustomEvent ×1
- **DeathEvent**
  - Entry Points: `OnDeath`
  - Calls: `Actor::Destroy`
  - Notes:
    - Custom event fired when character dies
    - Remove character from world
  - Node Mix: CustomEvent ×1, CallFunction ×1