# Connxio Plugins

Connxio agent plugins for VS Code, Claude Code, and GitHub Copilot tooling.

- `connxio`: registers the Connxio CLI MCP server with `connxio mcp serve` and includes Connxio skills.

## Install Connxio CLI First

Install the Connxio CLI before using the plugin:

```bash
npm install -g @connxio/cli
```

Then configure it:

```bash
connxio auth configure
connxio context add
connxio mcp doctor
```

The plugin depends on the `connxio` executable already being available in your `PATH`.

## Repository Layout

```text
.claude-plugin/
  marketplace.json
plugins/
  connxio/
    .claude-plugin/
      plugin.json
    .mcp.json
    skills/
```

## Install In VS Code

VS Code agent plugins are currently in preview and require `chat.plugins.enabled` to be enabled by your organization.

### Marketplace install

Add this repository as a plugin marketplace in your VS Code settings:

```json
{
  "chat.plugins.marketplaces": ["connxio/plugins"]
}
```

Then open the Extensions view, search for `@agentPlugins`, and install `connxio` from the `connxio-plugins` marketplace.

### Update plugin

Open the command palette and run `Extensions: Check for Extension Updates` to check for updates to marketplace plugins.

### Local plugin install

For local development, register the plugin directory directly:

```json
{
  "chat.pluginLocations": {
    "/path/to/Connxio.Plugins/plugins/connxio": true
  }
}
```

## Install In Claude Code

### Marketplace install

Add this repository as a marketplace, then install the plugin:

```bash
claude plugin marketplace add connxio/plugins
claude plugin install connxio@connxio-plugins
```

For local testing against an unpushed checkout:

```bash
claude plugin marketplace add .
claude plugin install connxio@connxio-plugins
```

### Direct plugin load

Load the plugin directly from the plugin directory:

```bash
claude --plugin-dir ./plugins/connxio
```

## Install In GitHub Copilot CLI

### Marketplace install

```bash
copilot plugin marketplace add connxio/plugins
copilot plugin install connxio@connxio-plugins
```

### Direct plugin install

```bash
copilot plugin install ./plugins/connxio
```

## Skills

Add skills under `plugins/connxio/skills/`.

## Troubleshooting

- If `connxio` is not found, reinstall the CLI and verify `connxio --help` works in your shell.
- If OAuth is not configured, run `connxio auth configure`.
- If no contexts are configured, run `connxio context add`.
- If the plugin loads but Connxio tools are unavailable, run `connxio mcp doctor`.
- If VS Code does not show agent plugins, verify `chat.plugins.enabled` is enabled for your organization.
