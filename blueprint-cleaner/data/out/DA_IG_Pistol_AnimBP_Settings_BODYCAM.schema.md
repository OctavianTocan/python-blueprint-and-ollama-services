# DA_IG_Pistol_AnimBP_Settings_BODYCAM — Schema (types and fields)

Source asset: `data/in/DA_IG_Pistol_AnimBP_Settings_BODYCAM.COPY`
Class: `/Game/InfimaGames/ShooterTemplate/Core/Weapons/BPDA_IG_Settings_Animation.BPDA_IG_Settings_Animation_C`
Kind: Data Asset (data-only parameters)

This document lists the observable fields in the asset and their types. Exact numeric values are intentionally omitted.

## Top-level fields

- Running Blend: Struct

  - Properties observed:
    - BlendIn: float
  - Note: Only `BlendIn` appears in this instance. If the underlying struct supports more fields (e.g., `BlendOut`), they do not appear here.

- Play Rate Breathing: float
- Play Rate Walking: float
- Play Rate Running: float
- Play Rate Turning: float

- Look Offset Multiplier Location: Vector3

  - X: float, Y: float, Z: float

- Look Offset Multiplier Rotation: Vector3

  - X: float, Y: float, Z: float

- Standing Offset: Struct

  - Translation: Vector3 (X, Y, Z: float)

- Standing Lag: Struct

  - Movement: Struct
    - Location: Struct
      - Horizontal: Vector3 (X, Y, Z: float)
      - Vertical: Vector3 (X, Y, Z: float)
    - Rotation: Struct
      - Horizontal: Vector3 (X, Y, Z: float)
      - Vertical: Vector3 (X, Y, Z: float)
  - Look: Struct
    - Location: Struct
      - Horizontal: Vector3 (X, Y, Z: float)
      - Vertical: Vector3 (X, Y, Z: float)
  - SpringInterpolation: Struct
    - Stiffness: float
    - CriticalDampingFactor: float
    - Mass: float

- Standing Lag Location Controller Multiplier: float

- Aiming Lag: Struct

  - Movement: Struct
    - Location: Struct
      - Horizontal: Vector3 (X, Y, Z: float)
      - Vertical: Vector3 (X, Y, Z: float)
    - Note: A Movement→Rotation sub-struct is not present in this instance.
  - Look: Struct
    - Location: Struct
      - Horizontal: Vector3 (X, Y, Z: float)
      - Vertical: Vector3 (X, Y, Z: float)
  - SpringInterpolation: Struct
    - Stiffness: float
    - CriticalDampingFactor: float
    - Mass: float

- Lowered Settings: Struct

  - SettingsBlend: Struct
    - BlendIn: float
    - BlendOut: float
  - RemoveStandingOffset: bool
  - RunningAnimationUsed: bool
  - RunningAnimationOffsetUsed: bool

- Aiming Sync Time: Struct

  - BlendIn: float
  - TimedValue: float

- Tactical Aim Offset: Struct

  - Translation: Vector3 (X, Y, Z: float)

- TPTacticalAimOffset: Struct

  - Rotation: 4-component rotation with X, Y, Z, W (float each)
  - Note: This is a rotation represented by four components; confirm the exact engine type (e.g., quaternion) in the class definition.

- NativeClass: string (object path to `BlueprintGeneratedClass`)

## Cross-references (what we can and cannot assert)

- This asset is data-only; no logic is defined here.
- The names of fields (Standing/Aiming Lag, Look Offset, etc.) align with update functions present in the character AnimBlueprint (`ABP_IG_Character`), but the .COPY dumps here do not explicitly show the wiring. Treat the mapping as “to be verified in Blueprint”.

## Research next

- Open `BPDA_IG_Settings_Animation` in the editor to confirm the concrete struct types used for:
  - Running Blend, Lowered Settings→SettingsBlend, Standing/Aiming Lag, and the Offset structs.
- Verify whether `TPTacticalAimOffset.Rotation` is an `FQuat` or a custom struct type.
- Check whether `Standing Lag` and `Aiming Lag` share a single struct type where some sub-fields are optional or simply unset in this instance.
- Identify the exact consumer blueprint(s) and pins that read these fields (AnimBP graph variables or function inputs).
