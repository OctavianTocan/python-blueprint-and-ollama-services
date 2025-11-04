# ABP_IG_Character — Types, graphs, and observable data flows

Source asset: `data/in/ABP_IG_Character.COPY`
Class: Anim Blueprint (character)

This document captures type signals and graph responsibilities observed in the AnimBP export. Exact numeric values and unproven assumptions are intentionally omitted.

## Key named graphs and responsibilities

- GetAttachmentManager

  - Retrieves attachment controller/manager from character/weapon context.

- GetScopeData, GetCheckEquippedItemHasScope

  - Scope/optic presence and data queries; likely feed aiming and offset logic.

- UpdateAimingLookLocationLagValues, UpdateAimingLookRotationLagValues

  - Update functions for aiming-state look lag. Types involved: Vector3 and float fields within nested lag structs.

- UpdateAimingMovementLocationLagValues

  - Updates aiming-state movement location lag (no rotation sub-struct observed for aiming in the DA instance).

- UpdateStandingLocationLag, UpdateStandingRotationLag

  - Standing-state look/movement lag updates. Types: Vector3 components and spring parameters (floats).

- UpdateStandingMovementLocationLag, UpdateStandingMovementRotationLag

  - Standing-state movement lag updates for location and rotation respectively.

- GetAimingOffset, GetAimingOffsetLocation

  - Provides aiming offsets (Vector3 location; rotation may be implied elsewhere).

- GetWorldSpaceLocationScope, GetScopeLocationOffsetComponentSpace

  - World- and component-space conversions for scope/optic location offsets (Vector3s).

- GetWeaponBodyScopeSocketLocation

  - Obtains weapon socket location used for scope alignment (Vector3).

- IsRunning, IsNotAiming, IsLowered, IsNotLowered, IsAlive, IsThirdPerson, IsNotTacticalSprinting

  - Boolean state queries consumed by layer blending and conditional updates.

- GetWeaponRecoilState, GetTargetRecoilRotation, GetTargetRecoilLocation, UpdateRecoilValues

  - Recoil logic. Types: Vector3 locations/rotations (Rotator or Quaternion internally, observed externally as Euler Vector3), floats for timing/scalars.

- Layer_Crawling_01, Running_Layer, Aiming_Layer, StandingOrLowered_Layer, plus montage and additive layers
  - Layered animation composition based on state booleans and offsets.

## Type signals inferred from graph IO and DA cross-reference

- Vector3 (X, Y, Z: float):

  - Offsets (Look multipliers, translations), lag Horizontal/Vertical components, scope/world locations, recoil target locations.

- Rotation (Rotator or Quaternion-like; exported often as 3 or 4 components):

  - Recoil target rotation (function names suggest rotation usage); TPTacticalAimOffset in DA uses a 4-component Rotation (X,Y,Z,W). Confirm engine type per class.

- Spring parameters (floats):

  - Stiffness, CriticalDampingFactor, Mass within SpringInterpolation sub-structs for Standing/Aiming lag.

- Booleans:

  - State checks and feature toggles (running, aiming, lowered, third person, alive, tactical sprinting).

- Play rates (floats):

  - Breathing, walking, running, turning.

- Blend structs (floats):
  - Running Blend (BlendIn), Lowered Settings (SettingsBlend with BlendIn/BlendOut), Aiming Sync Time (BlendIn/TimedValue).

## Data asset relationships (from DA_IG_Pistol_AnimBP_Settings_BODYCAM)

- Standing Lag and Aiming Lag share parallel nested structs used by the above update functions.
- Look Offset multipliers and Standing/Tactical offsets are consistent with getters like `GetAimingOffset*`.
- Lowered Settings + Running toggles influence the `StandingOrLowered_Layer` and running/aim layers.

## Observed variable activity

- The AnimBP includes extensive VariableGet/VariableSet usage across graphs (hundreds of references), confirming many state variables are read/updated per-tick and per-event. The .COPY snippet does not list a consolidated property section.
- Variables appear to include:
  - State flags (isRunning, isAiming, isLowered, isAlive, isThirdPerson)
  - Recoil state/targets (location/rotation vectors)
  - Offsets and lags (location/rotation vectors; spring parameters)
  - Scope attachment references and transform data

## Unknowns and to-verify items

- Exact types for rotation representations per graph (Rotator vs Quaternion) — verify node pin types in the editor.
- Consolidated member variable list for the AnimBP class is not visible in the provided .COPY; extract via editor or a fuller export.
- Which pins map the DA fields directly into AnimBP variables (explicit read nodes vs. function inputs).

## Research next

- Open `ABP_IG_Character` in the UE editor and inspect:
  - Variable panel for full list of member variables and their types.
  - Pin types for functions manipulating recoil, aiming offsets, and lag.
  - Which DA(s) are referenced and how their fields are read (Data Table Row Handle, Object reference, or direct variables).
- Cross-check `BPDA_IG_Settings_Animation` struct definitions to confirm field names and engine types.
