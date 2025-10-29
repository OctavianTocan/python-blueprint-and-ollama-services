# Blueprint: BPAC_IG_PCH_Melee

*Parent Class:* `SceneComponent`

## At a glance
- Variables: 11
- Graphs: 8
- Event Handlers: 6
- Unique Calls: 22

## Variables
| Name | Type | Category | Notes |
| --- | --- | --- | --- |
| `Base Damage` | real (double) | real | — |
| `Surfaces Handle` | struct<DataTableRowHandle> | struct | — |
| `Trace Radius` | real (double) | real | — |
| `Range` | real (double) | real | — |
| `Impulse` | real (double) | real | — |
| `Damage Type Class` | class<DamageType> | class | — |
| `Character` | object<Character> | object | — |
| `Camera` | object<CameraComponent> | object | — |
| `Third Person` | bool | bool | — |
| `Hit Result` | struct<HitResult> | struct | — |
| `Destruction Field` | Class<Actor> | Class | — |

## Graphs
### Composite Graph
- **CGraph Act**
  - Entry Points: `CGraph Act`
  - Calls: `Actor::GetComponentByClass`, `BPI_IG_Character::GetHeadTraceStartLocation`, `BPI_IG_Character::Is Third Person`, `GameplayStatics::BreakHitResult`, `KismetMathLibrary::Add_DoubleDouble`, `KismetMathLibrary::Add_VectorVector`, … (+6 more)
  - Reads: `Character`, `Destruction Field`, `Hit Result`, `LookImpactLocation`, `Range`, `Third Person`, … (+1 more)
  - Writes: `Camera`, `Character`, `Hit Result`, `Third Person`
  - Notes:
    - We use this as the endpoint (as opposed to the final look point). This allows us to take into account the melee component's range, because if we don't, we can punch infinitely far, which is pretty awful.
    - Without spawning this actor we wouldn't be able to destroy any of the Chaos Physics Actors in the levels, as they require Field Systems to destroy them. The idea is that the actor you're spawning here has one attached. If you spawn an actor without one, not much will happen, naturally.
    - We're using this now instead of the camera center calculation, so that we can actually trace from the character's viewpoint as opposed to from the player's viewpoint. This is so that it doesn't look like we can actually aim through walls when the character is clearly aiming at a wall with his face.
  - Node Mix: CallFunction ×10, VariableGet ×10, Knot ×6, VariableSet ×4, MacroInstance ×3
- **CGraph Add Impulse**
  - Entry Points: `CGraph Add Impulse`
  - Calls: `GameplayStatics::BreakHitResult`, `KismetMathLibrary::Multiply_VectorFloat`, `KismetMathLibrary::Normal`, `KismetMathLibrary::Subtract_VectorVector`, `PrimitiveComponent::AddImpulseAtLocation`, `SceneComponent::IsSimulatingPhysics`
  - Reads: `Hit Result`, `Impulse`
  - Notes:
    - Add some nice impulses!
  - Node Mix: CallFunction ×8, Knot ×7, VariableGet ×4, Tunnel ×2, Comment ×1
### Event Graph
- **EventGraph**
  - Entry Points: `Event Act`, `Event All Apply`, `Event Apply Visual Effects`, `Event Multicast Apply Visual Effects`, `Event Server Damage`
  - Calls: `Actor::GetComponentByClass`, `BPFL_IG_Surfaces::SpawnSurfaceDetails`, `BPI_IG_Character::GetHeadTraceStartLocation`, `BPI_IG_Character::Is Local`, `BPI_IG_Character::Is Third Person`, `GameplayStatics::ApplyPointDamage`, … (+15 more)
  - Reads: `Base Damage`, `Character`, `Damage Type Class`, `Destruction Field`, `Hit Result`, `Impulse`, … (+5 more)
  - Writes: `Camera`, `Character`, `Hit Result`, `Third Person`
  - Notes:
    - We use this as the endpoint (as opposed to the final look point). This allows us to take into account the melee component's range, because if we don't, we can punch infinitely far, which is pretty awful.
    - Without spawning this actor we wouldn't be able to destroy any of the Chaos Physics Actors in the levels, as they require Field Systems to destroy them. The idea is that the actor you're spawning here has one attached. If you spawn an actor without one, not much will happen, naturally.
    - We're using this now instead of the camera center calculation, so that we can actually trace from the character's viewpoint as opposed to from the player's viewpoint. This is so that it doesn't look like we can actually aim through walls when the character is clearly aiming at a wall with his face.
    - … (+6 more)
  - Node Mix: CallFunction ×27, VariableGet ×21, Knot ×14, VariableSet ×5, Comment ×5
### Event Handler
- **Event Act**
  - Entry Points: `Event Act`
  - Calls: `self.ExecuteUbergraph_BPAC_IG_PCH_Melee`
  - Node Mix: FunctionEntry ×1, CallFunction ×1
- **Event All Apply**
  - Entry Points: `Event All Apply`
  - Calls: `self.ExecuteUbergraph_BPAC_IG_PCH_Melee`
  - Node Mix: FunctionEntry ×1, CallFunction ×1
- **Event Apply Visual Effects**
  - Entry Points: `Event Apply Visual Effects`
  - Calls: `self.ExecuteUbergraph_BPAC_IG_PCH_Melee`
  - Node Mix: FunctionEntry ×1, CallFunction ×1
- **Event Multicast Apply Visual Effects**
  - Entry Points: `Event Multicast Apply Visual Effects`
  - Calls: `self.ExecuteUbergraph_BPAC_IG_PCH_Melee`
  - Node Mix: FunctionEntry ×1, CallFunction ×1
- **Event Server Damage**
  - Entry Points: `Event Server Damage`
  - Calls: `self.ExecuteUbergraph_BPAC_IG_PCH_Melee`
  - Node Mix: FunctionEntry ×1, SetVariableOnPersistentFrame ×1, CallFunction ×1