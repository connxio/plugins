---
name: connxio-delay-helper
description: Add or configure a Delay transformation in a Connxio integration. Use when the user wants to delay message processing by a fixed or random duration.
argument-hint: "integration id and desired delay duration or range in seconds"
---

# Connxio Delay Helper

When the user wants to add or configure a Delay transformation in a Connxio integration, use this skill to produce the correct delay transformation properties and update the integration.

## Delay transformation format

A Delay transformation has the following structure in the `transformations` array of a subintegration:

```json
{
  "transformationType": "Delay",
  "transformationName": "Delay_1",
  "enabled": true,
  "condition": {
    "enabled": false
  },
  "properties": "{\"delay\":5,\"fromSeconds\":10,\"toSeconds\":20,\"random\":true}"
}
```

### Properties

| Field         | Type    | Description                                                                 |
|---------------|---------|-----------------------------------------------------------------------------|
| `delay`       | integer | Fixed delay in seconds. Used when `random` is false.                        |
| `random`      | boolean | When true, a random duration between `fromSeconds` and `toSeconds` is used. |
| `fromSeconds` | integer | Lower bound of the random delay range (seconds).                            |
| `toSeconds`   | integer | Upper bound of the random delay range (seconds). Max 300.                   |

### Rules

- Max delay is **300 seconds** (5 minutes).
- For a fixed delay: set `random: false` and `delay` to the desired number of seconds.
- For a random delay: set `random: true` and provide `fromSeconds` and `toSeconds`.
- Always insert the Delay transformation **after** any script/mapping steps and **before** the outbound connection, unless the user specifies otherwise.
- Preserve all existing transformations — only append the new Delay entry.
- When updating an existing Delay, patch only the changed fields.

## Procedure

1. Call `get_integration` with the integration ID to retrieve the current state.
2. Locate the target `subIntegrationId` (default: the first subintegration).
3. Append the Delay transformation to the `transformations` array at the correct position.
4. Call `update_integration` with the full updated integration body.

## Examples

**Fixed 30-second delay:**
```json
{
  "transformationType": "Delay",
  "transformationName": "Delay_1",
  "enabled": true,
  "condition": { "enabled": false },
  "properties": "{\"delay\":30,\"fromSeconds\":0,\"toSeconds\":0,\"random\":false}"
}
```

**Random 10–20 second delay:**
```json
{
  "transformationType": "Delay",
  "transformationName": "Delay_1",
  "enabled": true,
  "condition": { "enabled": false },
  "properties": "{\"delay\":5,\"fromSeconds\":10,\"toSeconds\":20,\"random\":true}"
}
```
