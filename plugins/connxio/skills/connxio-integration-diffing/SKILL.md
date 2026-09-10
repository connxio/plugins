# Connxio Integration Diffing

When editing an existing Connxio integration (via `connxio_update_integration` or any other write action), never assume the last-known copy of that integration is still accurate.

## Why this matters

Connxio integrations are frequently edited outside of this assistant — directly in the Connxio UI, by other team members, or by the user making quick manual corrections (e.g. fixing a typo in a script, disabling a connection, changing a condition) without necessarily telling the assistant about it. If the assistant blindly reuses a previously-fetched copy of the integration and pushes a full-object update on top of it, any such manual changes are silently overwritten and lost.

## Rules

- Before making any change to an existing integration, always re-fetch its current live state first (e.g. via `connxio_get_integration`), even if the integration was already fetched or edited earlier in the same conversation.
- Compare the freshly-fetched state against the last state the assistant is aware of (from its own prior edits or reads).
- If a difference is found that the assistant did not itself make (e.g. a transformation was enabled/disabled, a script body changed, a condition expression changed, an endpoint URL changed), do not silently overwrite it.
  - Flag the specific difference to the user in plain terms (what changed, from what to what).
  - Ask whether it was an intentional manual change before proceeding.
  - If confirmed intentional, preserve that change and build the new edit on top of it.
  - If not intentional, ask the user how they'd like to proceed before continuing.
- Only proceed straight to applying the requested change without asking when the live state exactly matches the assistant's last-known state.
- This check applies every time, not just the first time an integration is touched in a session — integrations can change between turns, not just between sessions.

## Self-check before responding

- Did I re-fetch the current live state of the integration immediately before building my update payload?
- Did I compare it against what I last knew, rather than assuming no drift occurred?
- If a difference was found, did I ask the user about it before overwriting it?
