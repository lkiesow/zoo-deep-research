# Deep Research Skill for ZooCode

> Inspired by
>
> - [Deep Research Skill for Claude Code / OpenCode / Codex](https://github.com/Weizhena/deep-research-skills)
> - [Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

A structured research workflow skill for ZooCode, supporting two-phase research: outline generation (extensible) and deep investigation. Human-in-the-loop design ensures precise control at every stage.

```
    ┌──────────────────────┐             ┌──────────────────────────┐
    │        OUTLINE       │────────────►│     PARALLEL AGENTS      │
    │  /research <topic>   │             │     /research-deep       │
    │                      │             │                          │
    │  ├─ item 1           │             │  ┌──────┐  ┌──────┐      │
    │  ├─ item 2           │             │  │ web  │  │ web  │ ...  │
    │  └─ item N           │             │  │ res. │  │ res. │      │
    │  + field schema      │             │  └──────┘  └──────┘      │
    └──────────┬───────────┘             └───────────────┬──────────┘
               │                                         │
               │  review & edit                          │  deep search
               │                                         │  per item
               │                                         │
    ┌──────────┴───────────┐             ┌───────────────┴──────────┐
    │  HUMAN IN THE LOOP   │◄────────────│   STRUCTURED REPORT      │
    │                      │             │   /research-report       │
    │  confirm / modify    │             │                          │
    │  at each phase       │             │  ☑ results/*.json        │
    └──────────────────────┘             │  ☑ report.md             │
                                         └──────────────────────────┘
```

## Use Cases

- **Academic Research**: Paper surveys, benchmark reviews, literature analysis
- **Technical Research**: Technology comparison, framework evaluation, tool selection
- **Market Research**: Competitor analysis, industry trends, product comparison
- **Due Diligence**: Company research, investment analysis, risk assessment

## Prerequisites: Web Search MCP Server

ZooCode does not have a built-in web search tool. You must install
and configure a web search MCP server before using these skills.
For example, use [lkiesow/mcp-search-and-fetch](https://github.com/lkiesow/mcp-search-and-fetch).

## Installation

```bash
git clone https://github.com/Weizhena/deep-research-skills.git
cd deep-research-skills
```

```bash
python install.py
```

### Manual Install

```bash
# Create required directories
mkdir -p ~/.roo/skills ~/.roo/commands

# Install skills, strategy modules, and validation script
cp -r skills/* ~/.roo/skills/

# Install slash commands
cp commands/*.md ~/.roo/commands/

```

Then add the custom modes to your ZooCode configuration. For that, open ZooCode → Settings → Modes and select Import in the top right corner.

## Commands

| Command | Description |
| ------- | ----------- |
| `/research <topic>` | Generate research outline with items and fields |
| `/research-add-items` | Add more research items to existing outline |
| `/research-add-fields` | Add more field definitions to existing outline |
| `/research-deep` | Deep research each item (sequential subtasks) |
| `/research-report` | Generate markdown report from JSON results |

> **Note**: ZooCode processes research items sequentially (one subtask at a
> time). Results quality is identical; it just takes longer for large item lists.

## Workflow & Example

> **Example**: Researching "AI Agent Demo 2025"

### Phase 1: Generate Outline

```
/research AI Agent Demo 2025
```

The skill generates a list of items to research and a field framework, then
asks you to confirm or edit both. It optionally runs a web search to
supplement the list with the latest items.

**Output**: `AI_Agent_Demo_2025/outline.yaml` and `AI_Agent_Demo_2025/fields.yaml`

### (Optional) Add More

```
/research-add-items
/research-add-fields
```

Add more research items or field definitions to an existing outline.

### Phase 2: Deep Research

```
/research-deep
```

The skill reads the outline and spawns a `web-researcher` subtask for each
item (or batch of items). Each subtask searches the web, writes a structured
JSON file, and validates it against the field schema before completing.
Interrupted runs can be resumed — already-completed items are skipped.

**Output**: `AI_Agent_Demo_2025/results/*.json`

### Phase 3: Generate Report

```
/research-report
```

Reads all JSON results and generates a Python script that converts them into
a formatted Markdown report with a table of contents.

**Output**: `AI_Agent_Demo_2025/report.md`

## Repository Structure

```
├── commands/                   # Slash command definitions
│   ├── research.md
│   ├── research-deep.md
│   └── research-report.md
├── modes/
│   └── custom_modes.yaml       # research-orchestrator and web-researcher modes
└── skills/                     # Install contents to ~/.roo/skills/
    ├── web-search-modules/     # Domain-specific search strategy modules
    │   ├── general-web.md      # Reddit, Docs, HN, Medium, Dev.to, X/Twitter
    │   ├── academic-papers.md  # Scholar, arXiv, HuggingFace, ACM, IEEE
    │   ├── github-debug.md     # GitHub Issues for debugging
    │   └── stackoverflow.md    # Stack Overflow and technical forums
    ├── research/
    ├── research-add-fields/
    ├── research-add-items/
    ├── research-deep/
    └── research-report/
```

## References

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## License

MIT
