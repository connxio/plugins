---
name: connxio-script-action
description: Create or update Connxio Script transformations. Use when adding a script action, updating an existing Connxio script, changing script behavior, or fixing a Connxio execute(event) handler.
argument-hint: "desired script behavior, sample input, or change request"
---

# Connxio Script Action

When the user wants to create, update, or fix a Connxio Script transformation, produce valid JavaScript for the Connxio script editor.

## Required contract

Every Connxio script must define an `execute` handler and return the event:

```js
/**
 * Handler that will be called during the execution of the script.
 *
 * @param {TransformationEvent} event - Contains the file content and metadata about the file.
 * @returns {TransformationEvent} Return the modified event.
 */
const execute = (event) => {
  return event;
};
```

## Rules

- The script must be valid JavaScript.
- Always define `const execute = (event) => { ... }`.
- Always `return event`.
- Read the payload from `event.content`.
- Write the transformed payload back to `event.content`.
- Preserve metadata unless the user explicitly asks to change it.
- When updating an existing script, keep the current structure and behavior except for the requested change.
- Keep edits minimal. Do not rewrite the whole script unless the existing implementation is broken or the requested change requires it.
- If external packages are needed, use ESM imports and pin the version explicitly.
- Do not use file I/O or unsupported system access.
- `fetch` is allowed only when the requested behavior needs an HTTP call.
- `console.log()` is acceptable for debugging or test output examples.
- To terminate processing intentionally, throw `new Error(...)` with the requested Connxio termination semantics.

## Common patterns

### JSON transformation

For JSON input, use `JSON.parse(event.content)` and write back with `JSON.stringify(...)`:

```js
/**
 * Handler that will be called during the execution of the script.
 *
 * @param {TransformationEvent} event - Contains the file content and metadata about the file.
 * @returns {TransformationEvent} Return the modified event.
 */
const execute = (event) => {
  const myObj = JSON.parse(event.content);
  myObj.newField = "This is a new field added to the JSON object.";
  event.content = JSON.stringify(myObj);
  return event;
};
```

### Imported dependency

If the transformation needs a package, use a pinned ESM import, for example:

```js
import { XMLParser } from "fast-xml-parser@5.3.4";
```

### Reading another step's captured response (`dataCollection`)

When a script needs to read the response captured by an earlier REST (or
other) step in the same integration, it is available at
`event.metadata.dataCollection.<VariableName>`, where `<VariableName>` is the
exact `VariableName` configured on that earlier step's properties.

- **`dataCollection` must be spelled exactly like this** (lowercase `d`,
  camelCase) — do not write `dataCollection` with different casing (e.g.
  `DataCollection`, `datacollection`), and do not guess an alternative
  property name.
- **The key under `dataCollection` must exactly match the producing step's
  `VariableName`**, including case. If the REST step's properties have
  `"VariableName": "customerCreateResponse"`, the script must read
  `event.metadata.dataCollection.customerCreateResponse` — not a
  re-typed/paraphrased version of that name.
- The captured value may already be an object, or may be a JSON-encoded
  string depending on the adapter — always defensively parse it:

```js
const raw = event.metadata.dataCollection.customerCreateResponse;
const response = typeof raw === "string" ? JSON.parse(raw) : raw;
```

- Before writing a script that reads `dataCollection`, locate the exact
  `VariableName` string from the step that produces it (e.g. by inspecting
  the integration definition or the properties the user gave you) and copy
  it verbatim — do not type it from memory.

### Reading or writing user-defined properties (`userDefinedProperties`)

Scripts commonly read or set flags/values on
`event.metadata.userDefinedProperties.<PropertyName>` (e.g. `isUpdate`,
`customerId`), which conditions on later steps then reference via
`'{userdefinedproperties:<PropertyName>}'`.

- **`userDefinedProperties` must be spelled exactly like this** (camelCase) —
  do not write `UserDefinedProperties`, `userdefinedproperties`, or any other
  casing when accessing it from script code (`event.metadata.userDefinedProperties`).
- Note the case difference between the two contexts: in script code the
  object is `event.metadata.userDefinedProperties` (camelCase), but in a
  transformation's `condition.expression` string the placeholder syntax is
  **all lowercase**: `'{userdefinedproperties:isUpdate}'`. Do not mix these
  up (e.g. do not write `{userDefinedProperties:isUpdate}` in a condition
  expression, and do not write `event.metadata.userdefinedproperties` in a
  script).
- **`<PropertyName>` must exactly match (including case) across every place
  it's used**: the script that sets it, any other script that reads it, and
  every condition expression that checks it. If a script sets
  `event.metadata.userDefinedProperties.isUpdate`, every condition must read
  `{userdefinedproperties:isUpdate}` — not `{userdefinedproperties:IsUpdate}`
  or `{userdefinedproperties:is_update}`.
- Always guard for the object existing before writing to it, since it may be
  undefined on the first script in a chain:

```js
if (!event.metadata) {
  event.metadata = {};
}
if (!event.metadata.userDefinedProperties) {
  event.metadata.userDefinedProperties = {};
}
event.metadata.userDefinedProperties.isUpdate = hasExternalId ? "true" : "false";
```

- User-defined properties are always strings. When setting a flag, use the
  literal strings `"true"`/`"false"` (not JavaScript booleans), since
  condition expressions compare them as strings (e.g.
  `'{userdefinedproperties:isUpdate}' == 'false'`).
- Before writing a script that reads or sets a `userDefinedProperties` key
  that's already used elsewhere in the same integration, locate the exact
  property name from the existing script/condition and copy it verbatim —
  do not type it from memory or guess a variant spelling.

## Response preference

- Default to returning only the script code unless the user asks for explanation.
- If the user asks to update an existing script, return the full updated script unless they explicitly ask for a diff-only answer.
- Keep the final script focused on the requested behavior.

## Self-check before responding

- Is `execute` present?
- Does the script return `event`?
- Is `event.content` read and updated correctly?
- Are imports version-pinned?
- Is the script valid JavaScript?
- If the script reads `event.metadata.dataCollection.<VariableName>`, does
  `<VariableName>` exactly match (including case) the `VariableName` of the
  step that produces it, and is `dataCollection` spelled/cased correctly?
- If the script reads or sets `event.metadata.userDefinedProperties.<PropertyName>`,
  is `userDefinedProperties` spelled/cased correctly, and does `<PropertyName>`
  exactly match every other place it's used (other scripts, and
  `{userdefinedproperties:<PropertyName>}` in condition expressions)?
