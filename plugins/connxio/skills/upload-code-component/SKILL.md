---
name: upload-code-component
description: "Deploy a .NET Connxio code component (mapper/splitter) to a Connxio environment. Use when uploading a new component version, building and packaging a DLL or ZIP, publishing a code component, or updating integrations to the new version."
argument-hint: "Component project name and target environment"
---

# Deploy Connxio Code Component

## When to Use

- User wants to upload/deploy/publish a mapper or splitter to Connxio
- User says "upload new code component", "deploy to connxio", "publish updated mapper"
- After code changes to a component project under `src/`

## MCP Server Selection

| Environment | MCP tool prefix                |
| ----------- | ------------------------------ |
| Dev         | Use the configured dev prefix  |
| Test        | Use the configured test prefix |
| Prod        | Use the configured prod prefix |

Default to **Test** unless the user specifies otherwise.

> Code components are stored at the **account level** — upload only once per new version. The same binary is shared across all subscriptions.

## Procedure

### 1. Identify the project

Find the `.csproj` under `src/` that corresponds to the component the user wants to deploy. Use the component's configured Connxio name when uploading.

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

**Windows / PowerShell**

```powershell
$src  = "build_output"
$dest = "<ComponentName>.zip"   # MUST be outside the source folder
Remove-Item $dest -ErrorAction SilentlyContinue
Compress-Archive -Path "$src\*" -DestinationPath $dest
```

**macOS / Linux**

```bash
src="build_output"
dest="<ComponentName>.zip"   # MUST be outside the source folder
rm -f "$dest"
cd "$src" && zip -r "../$dest" ./*
```

> **IMPORTANT:** The destination `.zip` must be **outside** the source folder. If the zip is written inside the glob source (e.g. `build_output\*.zip` then zipping `build_output\*`), the archive includes itself and Connxio will throw "Bad IL format".

### 5. Upload

Call `upload_code_component` with:

- `filePath`: absolute path to the `.zip` (or `.dll` for dependency-free components)
- `name`: exact component name from Connxio
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
- Check the repository's deployment notes before deploying — the registry version and the in-use version in integrations may differ
