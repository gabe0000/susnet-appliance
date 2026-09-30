# SusNet appliance UI style guide

The starter in `templates/ui/` is the required baseline for the browser wizard
and operational dashboard. It is intentionally framework-neutral and contains
no operator identity or external assets.

## Visual language

- Dark, low-glare radio-console surface with cyan for navigation and focus,
  mint for healthy state, amber for attention, and coral for faults.
- Use the tokens in `tokens.css`; do not insert one-off color values into
  feature components.
- Prefer clear status words over color alone. Every state badge includes text.
- Use the system font stack and locally packaged assets only.
- Keep primary content at or below 1120 px and maintain useful layout down to
  a 320 px viewport.

## Interaction rules

- Every page has a skip link, one `h1`, visible keyboard focus, real labels,
  useful autocomplete attributes, and an `aria-live` status region.
- Secret fields never repopulate. Display only `Configured`, `Not configured`,
  or `Replace` after save.
- Separate draft save from apply. Destructive, RF, firmware, and network
  actions use the danger treatment and require a review step.
- Distinguish saved, running, registered, tested, blocked, and unavailable.
- Never hide a safety failure behind a disabled button; explain what must be
  corrected.
- Do not place implementation details, raw logs, or credentials in the normal
  operator flow.

## Components

The template supplies an application shell, progress steps, status badges,
cards, labeled fields, callouts, summary rows, button groups, and responsive
layouts. Implementations may translate these into server templates or a UI
framework, but token names, state meanings, accessibility behavior, and
spacing hierarchy remain stable.

Run `make lint` to reject external assets and basic accessibility regressions
in the starter template.
