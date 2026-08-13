---
name: connxio-cxmal
description: Reference and guidance for Connxio Macro Language (CxMaL). Use when the user wants to use dynamic values in endpoints, filenames, logging, conditions, data collection, or any other CxMaL-supported field — e.g. building a dynamic URL from file content, formatting a date in an outbound filename, reading a field from the message body, or handling null values safely.
argument-hint: "what the user wants to do with CxMaL (e.g. 'use the order ID from the file as the outbound filename')"
---

# Connxio Macro Language (CxMaL)

CxMaL is Connxio's domain-specific language for injecting dynamic values into integration configuration fields. Macros are written as `{macroName}` or `{macroName:path}` and are resolved at runtime for each message.

## Syntax

```
{macroName}
{macroName:path}
{macroName.Method(arg)}
{macroName:path | pipe: action}
{macroName:path | pipe1: action | pipe2: action}
```

---

## Where CxMaL can be used

| Location | Fields | Notes |
|----------|--------|-------|
| **Inbound REST adapter** | URL | Only `{metadata:...}` is meaningful this early in the pipeline |
| **Outbound REST adapter** | Endpoint URL, headers | Full access to all macros |
| **Outbound Azure Storage** | Blob/file name | Full access |
| **Outbound SFTP** | Output file name | Full access |
| **Data Collection transformation** | URL, key, value fields | Full access |
| **Logging webhooks** | Webhook URL, Transaction Tag | Full access |
| **Conditions** (rules) | Condition expression | Full access — see `connxio-condition` skill |

---

## Macros

### `{file:path}` — Read from message content (JSON or XML)

Reads a value from the message body using dot-notation for JSON or element names for XML. Supports array indexing.

**JSON examples:**
```
{file:orderId}
{file:order.customer.name}
{file:items[0].sku}
{file:items[2].price}
```

**XML examples (element name):**
```
{file:note.heading}
{file:order.customer.name}
```

**In a URL:**
```
https://api.example.com/orders/{file:orderId}/status
```

**In a filename:**
```
order_{file:orderId}_{date | date: yyyyMMdd}.json
```

---

### `{metadata:field}` — Read from message metadata

Accesses the metadata object attached to every message. Useful for routing, logging, and conditions.

**Available fields:**

| Field | Description |
|-------|-------------|
| `configCorrelationId` | Integration ID |
| `transactionType` | Integration name |
| `interchangeId` | Unique message ID |
| `started` | Pipeline start timestamp |
| `inboundFileName` | Inbound file name |
| `inboundEndpoint` | Inbound endpoint/address |
| `inboundAdapter` | Adapter type (e.g. `SFTP`, `Api`) |
| `outboundFileName` | Outbound file name |
| `outboundEndpoint` | Outbound endpoint |
| `outboundAdapter` | Outbound adapter type |
| `manualResendCount` | Number of manual resends |
| `dataCollection` | Snapshot of data collection values |
| `userDefinedProperties` | Properties from code components |

**Examples:**
```
https://api.example.com/log?source={metadata:inboundAdapter}
outbound_{metadata:inboundFileName}_{date | date: yyyyMMdd}.xml
```

---

### `{filename}` — Inbound filename (without extension)

```
{filename}
→ "myfile"  (if the inbound file was "myfile.txt")
```

Useful for preserving or transforming the filename on outbound:
```
processed_{filename}.xml
{filename | string: toLower}.json
```

---

### `{interchange}` — The interchange ID (message trace ID)

```
{interchange}
→ "99d9f5c7-6826-4d3f-80a2-1ab3b9e2c7a8"
```

Useful as a unique correlation key in URLs or filenames:
```
https://api.example.com/callback/{interchange}
{interchange}_{filename}.json
```

---

### `{guid}` — A random GUID (generated fresh each use)

```
{guid}
→ "7b6fd3d0-41cb-46d6-af57-27f4bb1e6c9c"
```

Use when you need a unique value that is not tied to the message:
```
temp_{guid}.json
```

---

### `{date}` — Current UTC datetime

Returns the current UTC datetime. Supports method chaining and the `date` pipe for formatting.

**Basic:**
```
{date}
→ "2024-03-27T09:30:46.8926251Z"
```

**With methods:**
```
{date.AddDays(1)}
{date.AddHours(-2)}
{date.AddMonths(1).AddDays(10)}
{date.SetCstZone(Central Europe Standard Time)}
{date.SetCstZone(Central Europe Standard Time).AddDays(1)}
```

**With formatting (date pipe):**
```
{date | date: yyyyMMdd}           → "20240327"
{date | date: dd.MM.yyyy}         → "27.03.2024"
{date | date: dd.MM.yyyy HH.mm.ss} → "27.03.2024 09.30.46"
{date.AddDays(1) | date: yyyyMMdd} → "20240328"
```

**In a filename:**
```
export_{date | date: yyyyMMdd}.csv
backup_{date.SetCstZone(Central Europe Standard Time) | date: yyyyMMdd_HHmm}.zip
```

---

### `{datacollection:key}` — Data from a Data Collection transformation

Access values stored by a Data Collection transformation earlier in the pipeline. Supports `#json` to navigate into JSON-valued entries.

```
{datacollection:status}
{datacollection:apiResponse}
{datacollection#json:apiResponse.body.id}
{datacollection#json:apiResponse.body.name}
```

**In a URL:**
```
https://api.example.com/items/{datacollection#json:lookup.id}
```

---

### `{userdefinedproperties:key}` — Properties set in code components

Access key/value pairs written to `UserDefinedProperties` inside a code component. Supports `#json`.

```
{userdefinedproperties:routeTo}
{userdefinedproperties#json:result.code}
```

---

### `{statusevent:path}` — Status event data (for test assertions)

Used primarily in integration testing. Provides access to the status event object including error info and metadata.

```
{statusevent:Error.errorCode}
{statusevent:StatusEventResult}
{statusevent:Metadata.inboundFileName}
```

---

## Pipes

Pipes transform or guard the output of a macro. Chain multiple pipes with `|`.

### Transformation pipes

| Pipe | Usage | Result |
|------|-------|--------|
| `\| date: <format>` | `{date \| date: yyyyMMdd}` | `20240327` |
| `\| string: toUpper` | `{filename \| string: toUpper}` | `MYFILE` |
| `\| string: toLower` | `{filename \| string: toLower}` | `myfile` |
| `\| array: contains(value)` | `{file:tags \| array: contains('urgent')}` | `true` / `false` |
| `\| array: notContains(value)` | `{file:tags \| array: notContains('draft')}` | `true` / `false` |
| `\| array: contains(field == value)` | `{file:items \| array: contains(id == 42)}` | `true` / `false` |

### Error handling pipes

Only the first triggered error handling pipe is executed. Later pipes are skipped once one fires.

| Pipe | Trigger | Action |
|------|---------|--------|
| `\| null: ignore` | Field is null | Leaves macro text as-is |
| `\| null: remove` | Field is null | Removes macro from the string |
| `\| null: fallback <value>` | Field is null | Substitutes `<value>` |
| `\| null: terminate` | Field is null | Terminates the message |
| `\| error: ignore` | Any macro error | Leaves macro text as-is |
| `\| error: remove` | Any macro error | Removes macro from the string |
| `\| error: fallback <value>` | Any macro error | Substitutes `<value>` |
| `\| error: terminate` | Any macro error | Terminates the message |

### Pipe chaining example

```
{file:myVariable | null: fallback defaultValue | error: terminate | string: toUpper}
```
- If `myVariable` is null → result is `DEFAULTVALUE`
- If reading the file errors → message is terminated
- Otherwise → value from file, uppercased

---

## Common patterns

### Dynamic REST endpoint from file content
```
https://api.example.com/customers/{file:customerId}/orders
```

### Outbound filename with date and original name
```
{filename}_{date | date: yyyyMMdd_HHmm}.xml
```

### Outbound filename using interchange ID (always unique)
```
{interchange}.json
```

### Filename with safe null handling
```
{file:orderId | null: fallback unknown}_{date | date: yyyyMMdd}.json
```

### Date in a specific timezone
```
{date.SetCstZone(Central Europe Standard Time) | date: yyyy-MM-dd}
```

### URL built from data collection lookup result
```
https://api.example.com/route/{datacollection#json:routingResult.targetId}
```

### Transaction tag in logging (for traceability)
```
{metadata:transactionType}-{file:orderId}
```

---

## Tips

- `{file:...}` works for both JSON (dot-notation + array index) and XML (element names).
- `{filename}` does **not** include the file extension.
- `{guid}` generates a **new** random GUID each time it is evaluated — do not use it if you need the same value in two places.
- `{interchange}` is stable for the entire message lifecycle — use it for correlation.
- On inbound REST, only `{metadata:...}` is available; `{file:...}` is not yet populated.
- Always use the `null` or `error` pipe when a field may be absent to avoid runtime failures.
- The `date` pipe accepts any .NET standard or custom date/time format string.
- Pipes are executed left to right. Error-handling pipes short-circuit — once one fires, the rest are skipped.
