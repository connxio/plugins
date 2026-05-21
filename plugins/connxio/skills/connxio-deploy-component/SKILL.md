---
name: connxio-deploy-component
description: "Deploy a .NET Connxio code component (mapper/splitter) to a Connxio environment. Use when: uploading new component version, deploying mapper, deploying splitter, publishing dll to connxio, building and uploading code component, updating integration to new version. Covers build, package, upload, and updating all integrations."
argument-hint: "Component project name and target environment (dev/test/prod)"
---

# Deploy Connxio Code Component

## When to Use
- User wants to upload/deploy/publish a mapper or splitter to Connxio
- User says "upload new code component", "deploy to connxio", "publish updated mapper"
- After code changes to any project under `src/` in `int-b24-bc` or `int-kubix-bc`

## MCP Server Selection

| Environment | MCP tool prefix |
|-------------|----------------|
| Dev         | `mcp_connxio-vikin_` |
| Test        | `mcp_connxio-vikin2_` |
| Prod        | `mcp_connxio-vikin3_` |

Default to **Test** unless the user specifies otherwise.

> Code components are stored at **company level** — upload only ONCE per new version. The same binary is shared across all subscriptions.

## Procedure

### 1. Identify the project
Find the `.csproj` under `src/` matching the component the user wants to deploy. The project folder name maps to the component:

| Project folder | Connxio component name |
|---|---|
| `Int.Bc.B24.Pricat.Parquet.Mapper` | `BC-B24-Pricat-Parquet-Mapper` |
| `Int.Bc.B24.Pricat.Mapper` | `BC-B24-Pricat-Mapper` |
| `Int.Bc.B24.Invoice.Mapper` | `BC-B24-Invoice-Mapper` |
| `Int.Bc.B24.OrderResponse.Mapper` | `BC-B24-OrderResponse-Mapper` |
| `Int.Bc.B24.Invrpt.Mapper` | `BC-B24-Invrpt-Mapper` |
| `Int.Bc.B24.DespatchAdvice.Mapper` | `BC-B24-DespatchAdvice-Mapper` |
| `Int.B24.Bc.InboundOrders.Mapper` | `B24-BC-Order-Mapper` |
| `Int.B24.Bc.InboundOrders.Splitter` | `B24-BC-Order-Splitter` |

If unsure, call `list_code_components` and match by name.

### 2. Check `.csproj` for runtime dependencies

Open the `.csproj` and inspect `<PackageReference>` entries:
- If **all** packages have `<ExcludeAssets>runtime</ExcludeAssets>` → upload a **single `.dll`**
- If **any** package lacks `<ExcludeAssets>runtime</ExcludeAssets>` (e.g. `Parquet.Net`) → upload a **`.zip`** of all output files (the zip format is supported by Connxio and required when bundling native dependencies)

### 3. Build

```powershell
cd "src/<ProjectFolder>"
dotnet build -c Release -o build_output
```

### 4. Package (if zip required)

```powershell
$src  = "build_output"
$dest = "<ComponentName>.zip"   # MUST be outside the source folder
Remove-Item $dest -ErrorAction SilentlyContinue
Compress-Archive -Path "$src\*" -DestinationPath $dest
```

> **IMPORTANT:** The destination `.zip` must be **outside** the source folder. If the zip is written inside the glob source (e.g. `build_output\*.zip` then zipping `build_output\*`), the archive includes itself and Connxio will throw "Bad IL format".

### 5. Upload

Call `upload_code_component` with:
- `filePath`: absolute path to the `.zip` (or `.dll` for dependency-free components)
- `name`: exact component name from Connxio (see table above)
- Omit `version` to auto-increment the patch (e.g. 1.0.0 → 1.0.1)

The upload response lists all integrations currently using the old version.

### 6. Update integrations

For each integration listed in the upload response, call `update_component_in_integration` with:
- `integrationId`: the integration's `configCorrelationId`
- `componentName`: same name used in upload
- `oldVersion`: previous version
- `newVersion`: newly uploaded version

Ask the user to confirm before updating if there are multiple integrations or if targeting prod.

## Notes
- The `publish_output\` folder is gitignored — safe to write there
- Always clean or overwrite `publish_output\` before republishing to avoid stale files
- Check the CLAUDE.md version gap notes before deploying — the registry version and the in-use version in integrations may differ
