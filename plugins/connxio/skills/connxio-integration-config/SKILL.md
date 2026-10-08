---
name: connxio-integration-config
description: General guide for creating and editing Connxio integration configs through the Connxio MCP tools. Use when adding, changing, reordering or removing transformation steps (Dataverse, REST, Script, Splitting, Terminate, Delay), changing inbound/outbound adapters, or calling connxio-update_integration / connxio-create_integration. Covers the config structure, update pitfalls, step property shapes, data flow between steps and termination patterns.
---

# Connxio integration config: creating and editing

Practical rules learned from building real integrations. Read this before any `connxio-create_integration` or `connxio-update_integration` call. For script bodies see `connxio-script-action`, for macros `connxio-cxmal`, for conditions `connxio-condition`.

## Ground rules

1. **Pass `contextId` explicitly on every call.** Check with `connxio-list_contexts` which one the user is working in and stay in it. Never switch context silently. A default context may exist, but do not rely on it.
2. **Only do what was asked.** Do not "improve" other steps, rename things, change schedules or filters. Mention suspicious things instead of fixing them.
3. **Never write to a customer's external systems yourself** (Dataverse, BC, Tripletex, ...). You only edit Connxio configs. Metadata reads are allowed only if the project rules say so. Never print secrets or tokens.
4. **The user edits the integration between turns.** Always `connxio-get_integration` right before every update, and use that `_etag`. Never reuse an old copy.
5. If a value is unknown (schema id, endpoint, field), use an obvious placeholder like `REPLACE_WITH_SCHEMA_ID`, save the rest, and tell the user what is left.
6. After an update, say what changed and that nothing has been run. Flag assumptions explicitly.

## Config structure

```
Integration
  inboundConnection          adapterType: Api | TimeTrigger | ... (+ intervalExpression for time triggers)
  subIntegrations[]
    transformations[]        run in array order
    outboundConnections[]    run after transformations
    loggingWebhookOverrides, preDefinedUserProperties, messageOutboundFormat, ...
  loggingWebhooks[], retryOptions, ...
```

Each transformation:
```json
{
  "id": "<guid>",
  "transformationType": "Dataverse|REST|InlineScript|Splitting|TerminateTransformation|Delay|...",
  "transformationName": "Readable name",
  "properties": "<JSON STRING, not an object>",
  "enabled": true,
  "condition": { "enabled": true, "expression": "" },
  "continuousBatchOptions": { "useContinuousBatch": false }
}
```

- `properties` is a **stringified JSON** string. Double-escape correctly. Build it with a script (`JSON.stringify` / `ConvertTo-Json -Compress`), never by hand.
- `condition.expression` empty means always run. A condition uses CxMaL, e.g. `'{file:wf_product_key}' != ''`. Quote string macros.
- Use new GUIDs for new steps. Keep the ids of existing steps. Ids are stable references.
- `continuousBatchOptions` is only present on Dataverse steps. Use `false` for GETs. Upserts in existing integrations often use `true`; copy what the integration already does.
- Order in the array is execution order. To insert a step, splice it at the right index.

## Updating: `connxio-update_integration`

- It takes the **full** integration object. Partial objects drop fields or fail validation.
- Procedure: get, modify in memory (script), submit everything including the current `_etag`.
- Easy to forget (400 `The X field is required`): top-level `sender`, `receiver`, `messageInboundFormat`, `messageInboundEncoding`, `intervalExpression`, `loggingWebhooks`, `retryOptions`, `environment`, `archived`, company/subscription fields, `configCorrelationId`, `transactionType`. Per sub-integration: `messageOutboundFormat`, `outboundConnections`, `preDefinedUserProperties`, `enabled`, `sender`, `receiver`, and **every sub-field of `loggingWebhookOverrides`** (`logLevel`, `inboundMesssageType`, `outboundMessageType`, `logMessageContent`, `transactionTag`, `customInboundDescription`, `customOutboundDescription`, `logMetaData`, `enabled`).
- Optional: `updatedBy`, `tags`.
- When you change a script, **omit `scriptHash`** so the server recomputes it. Keep it for scripts you did not touch.
- An etag mismatch means the user edited it. Re-fetch and re-apply your change on top. Do not overwrite.
- The response (and `get`/`list` of big integrations) is very large and is saved to a temp file. Do not view it. Extract what you need with a regex/jq/`ConvertFrom-Json` (new `_etag`, a script, a step's properties), then **delete the temp file**.
- `connxio-create_integration` validates; `connxio-create_integration_no_validation` is for drafts that are not complete yet.
- After saving, verify by re-reading the relevant part (or the returned object), not by assuming.

## Step property shapes

### Dataverse GET (Operation 1)
```json
{"SecurityConfigId":"<guid>","Operation":1,"VariableName":"quotation",
 "EntityName":"wf_quotation","Filter":"wf_serviceagreement eq \"{file:wf_soserviceagreementid}\"",
 "SelectedFields":["wf_quotationid","wf_workflexid"]}
```
- Use logical names, lower case (except where the filter uses lookup display names, copy existing filters).
- Result is stored in `event.metadata.dataCollection[VariableName]` as a JSON string (array of rows).
- Lookups come back as a display value in `<field>` plus the GUID in `<field>_key`. To filter on or read the guid use `_key`.
- Read from earlier results in macros with `{datacollection#json:var.[0].field}`.
- Select the lookup field itself (`wf_account`) to get both `wf_account` and `wf_account_key`.
- Date delta: `modifiedon gt "{date.UseDateTimeDelta(2026-01-01T00:00:00.00)}"` in the Filter. The date is the first-run start.
- An empty result is `[]`; the step does not fail.

### Dataverse upsert (Operation 2)
`{"SecurityConfigId","SchemaId":"<schemaGuid>_<version>","Operation":2,"VariableName"}`. The schema (template) is created separately (see `connxio-dataverse-schema`). It maps the message content to the entity. Ask for the SchemaId, do not invent it.

### REST
```json
{"EndpointURL":"https://.../{env:Var}/...","HTTPVerb":"POST","WebhookConnectionId":"<securityConfigId>",
 "Headers":{"content-Type":"application/json","accept":"application/json"},"Body":"",
 "UsePaging":false,"UseDateDelta":false,"PagingType":1,"NextLinkType":1,
 "RestConnectionPropertiesSecondary":{"HTTPVerb":"POST","RestResponseErrorHandlingRules":[],"CustomTimeout":0},
 "TerminateOnDuplicateDetection":false,"DuplicateDetectionEntryTtlMinutes":7200,
 "RestResponseErrorHandlingRules":[],"CustomTimeout":60,
 "VariableName":"priceRequest","UseContentAsRequestBody":true,"UseResponsAsContent":false}
```
- POST: `UseContentAsRequestBody: true` sends the current content as body.
- GET: `UseContentAsRequestBody: false`. `UseResponsAsContent: true` replaces the content with the response (be careful, the original content is lost).
- Response is stored in the data collection under `VariableName`.
- Environment variables are `{env:Name}`. Copy the full property set from an existing REST step of the same system. Do not hand-write it from memory.

### Script (InlineScript)
`{"script":"const execute = (event) => { ...; return event; };"}`. See `connxio-script-action`. Content is a string: `JSON.parse(event.content)` in, `event.content = JSON.stringify(x)` out. Always stringify.

### Splitting
Use the global "Split List into Single Elements" component. Copy the whole properties object from an existing integration (it includes a SAS URL, `IsGlobal: true`). Input must be a JSON array in `event.content`; each element becomes its own message and the rest of the steps run once per element.

### TerminateTransformation
`{"Condition":"<expr>","LogLevel":1,"Status":"Success|Warning|Error","Description":"readable text with {file:id}","PersistError":false}`
- Stops the message when the condition is true. Use it for guards ("skip if type is X").
- Condition syntax follows step conditions; keep it simple, and test on a real run.
- `Status: "Success"` ends the message as a normal, successful run with the description in the log.

### Delay
Use the `connxio-delay-helper` skill.

### Outbound connections
Redirect (`adapterType: "Redirect"`, `IntegrationId` in `connectionProperties`) sends the message into another integration. Dataverse outbound uses `{SecurityConfigId, SchemaId, Operation:2, VariableName}`. Prefer moving outbound adapters into a transformation step only when the user asks.

## Data flow between steps

- **`event.content`** is the message body. Steps, `{file:...}` and scripts all read it.
- **Data collection** is where Dataverse/REST steps put their results (key = `VariableName`). Read in scripts via `event.metadata.dataCollection.<name>` (usually a JSON string, parse it; guard with `typeof x === 'string'`). Read in macros via `{datacollection#json:name.[0].field}`.
- **User-defined properties (UDP)**: `event.metadata.userDefinedProperties.<key>`, macro `{userdefinedproperties:key}`. Use them for flags and ids that must survive across steps (e.g. `contactExists`, `planningLineId`) and for conditions on later steps.
- **After a split**, the data collection is not split per message. Earlier, list-level results are still the whole list, and lookups made after the split hold the value of the latest message. If a later step needs the current element's id, store it in a UDP right after the split, and read it from the UDP.
- Pass identifiers forward in `event.content` (e.g. the script that builds the final payload sets `contactid`, `accountid`) so later `{file:...}` filters can use them.

## Common patterns

- **Fetch list, then process each**: Dataverse GET, then a script "Set X as content" (parse the data collection, stringify to content), then Split.
- **Empty guard**: in that script, if there is no data, `throw new Error("Success|No X to update")` to end cleanly (code words: `Success`, `Warning`, `Error`; `|PersistError` suffix; `Loglevel:None`/`Loglevel:Never`). Any other exception is a normal error.
- **Existence check, then create**: GET step, small script sets a UDP (`exists` true/false), the create/upsert step has condition `'{userdefinedproperties:exists}' == 'false'`, and a later script picks the id from the upsert response or the GET response. Note that concurrent messages can still race.
- **Conditional lookups**: add a condition such as `'{file:wf_product_key}' != ''` on GET steps whose key may be empty.
- **Type/skip guard after a split**: TerminateTransformation with a readable Description.
- **Time-triggered integrations ignore the inbound body.** The time trigger content (e.g. `{"foo":"bar"}`) is a placeholder; the first step fetches the real data.
- **Mapping steps**: build the target model in a script; throw `Error|...` with an id in the message when required data is missing so the error is traceable.
- **Naming**: step names describe the action ("Get quotation", "Map to BC format", "Post the price request"). Variable names are camelCase and unique within the integration.

## Checklist before saving

- [ ] Fetched fresh, using the latest `_etag`
- [ ] Only the requested change was made; other steps are byte-identical
- [ ] `properties` is a valid JSON string; scripts have no `scriptHash` if edited
- [ ] New step ids are new GUIDs; step order is right
- [ ] Every `{datacollection...}` / `{userdefinedproperties...}` / `{file:...}` reference points to something an earlier step produces
- [ ] Conditions and terminates handle empty/null data
- [ ] Placeholders are listed to the user
- [ ] Temp output files are deleted
