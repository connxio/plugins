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
