---
name: connxio-condition
description: Add, update, or remove a condition (conditional rule) on a Connxio transformation, outbound connection, or subintegration. Use when the user wants to make an action run only when certain criteria are met, using CxMaL expressions.
argument-hint: "integration id and the condition logic to apply (e.g. 'only run if file.status == active')"
---

# Connxio Condition Helper

Conditions in Connxio use **CxMaL (Connxio Macro Language)** expressions to control whether a transformation, outbound connection, or subintegration runs for a given message.

## Where conditions apply

| Target | Notes |
|--------|-------|
| Transformation (any type) | `condition` field on the transformation object |
| Outbound connection | `condition` field on the outbound connection object |
| Subintegration | `condition` field on the subintegration object |
| **Inbound connection** | ❌ **Not supported** — conditions cannot be applied to inbound adapters |

## Condition JSON structure

```json
{
  "enabled": true,
  "expression": "'{file:status}' == 'active'"
}
```

To **disable** a condition (always run):
```json
{
  "enabled": false
}
```

## Condition syntax (CxMaL operators)

| Operator | Meaning |
|----------|---------|
| `==` / `is` / `eq` | Equal |
| `!=` / `is not` | Not equal |
| `>` / `<` / `>=` / `<=` | Numeric comparison |
| `&&` / `and` | Logical AND |
| `\|\|` / `or` | Logical OR |
| `()` | Grouping / precedence |
| `true` / `false` | Boolean literals |
| `null` | Null literal |

Strings must be wrapped in **single or double quotes**: `'value'` or `"value"`.

## CxMaL macros for use in conditions

### `{file:path}` — Read from message content (JSON or XML)

```
'{file:status}' == 'active'
'{file:order.type}' == 'B2B'
{file:amount} > 1000
'{file:address.country}' == 'NO' || '{file:address.country}' == 'SE'
{file:myArray | array: contains('John')} == true
{file:myArray | array: notContains(name == 'Lisa')} == true
```

For arrays of objects: `{file:items | array: contains(id == 42)}`

### `{metadata:field}` — Read from message metadata

Available metadata fields:
- `inboundFileName`, `inboundEndpoint`, `inboundAdapter`
- `outboundFileName`, `outboundEndpoint`, `outboundAdapter`
- `transactionType`, `interchangeId`, `configCorrelationId`
- `manualResendCount`

```
'{metadata:inboundAdapter}' == 'SFTP'
{metadata:manualResendCount} > 0
'{metadata:transactionType}' == 'OrderSync'
```

### `{filename}` — The inbound filename (without extension)

```
'{filename}' == 'invoice'
'{filename | string: toLower}' == 'invoice'
```

### `{interchange}` — The interchange ID

```
'{interchange}' != null
```

### `{datacollection:key}` — Data from a Data Collection transformation

```
'{datacollection:status}' == 'OK'
{datacollection#json:apiResponse.body.approved} == true
```

### `{userdefinedproperties:key}` — Properties set in code components

```
'{userdefinedproperties:routeTo}' == 'systemA'
{userdefinedproperties#json:result.code} == 200
```

## Pipes

Pipes transform the output of a macro before evaluation:

| Pipe | Example |
|------|---------|
| `\| string: toUpper` | `'{filename \| string: toUpper}' == 'INVOICE'` |
| `\| string: toLower` | `'{filename \| string: toLower}' == 'invoice'` |
| `\| array: contains(value)` | `{file:tags \| array: contains('urgent')} == true` |
| `\| array: notContains(value)` | `{file:tags \| array: notContains('draft')} == true` |
| `\| null: ignore` | Returns original macro text on null |
| `\| null: remove` | Removes macro from string on null |
| `\| null: fallback <value>` | `{file:name \| null: fallback unknown}` |

## Examples

### Check if a JSON field equals a value

```
'{file:delay}' == 'yes'
```

### Check a nested field

```
'{file:order.status}' == 'confirmed'
```

### Numeric comparison

```
{file:amount} >= 500
```

### Combine conditions

```
'{file:type}' == 'order' && {file:amount} > 100
```

### Check metadata

```
'{metadata:inboundAdapter}' == 'Api' && '{file:priority}' == 'high'
```

### Check array contains a string

```
{file:categories | array: contains('express')} == true
```

## Procedure

1. Call `get_integration` with the integration ID to retrieve the current state.
2. Locate the target object:
   - For a **transformation**: find it in `subIntegrations[n].transformations` by name or id.
   - For an **outbound connection**: find it in `subIntegrations[n].outboundConnections`.
   - For a **subintegration**: the `condition` field is directly on the subintegration object.
3. Set the `condition` field:
   ```json
   {
     "enabled": true,
     "expression": "<CxMaL expression>"
   }
   ```
4. Call `update_integration` with the full updated integration body.
5. Confirm the change with the user, showing the expression that was applied.

### Run if field equals value OR field is absent

Use `null: fallback` to default to the matching value when the field doesn't exist:

```
'{file:delay | null: fallback yes}' == 'yes'
```

- If `delay` field is missing → fallback to `yes` → condition is **true** (runs)
- If `delay` = `"yes"` → condition is **true** (runs)
- If `delay` = `"no"` → condition is **false** (skipped)

## Tips

- When reading strings from file content, always wrap the macro in quotes: `'{file:field}'` — otherwise string comparison will fail.
- Numeric macros (`{file:amount}`) should **not** be quoted when doing numeric comparisons.
- Boolean fields from the file content can be compared directly: `{file:isActive} == true`.
- Use `| null: fallback <default>` to avoid null errors on optional fields.
- To remove a condition, set `{ "enabled": false }` (do not include `expression`).
