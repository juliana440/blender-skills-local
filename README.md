# Blender Skills Local

28 Blender skills for Claude Code and other coding agents that run **only in the Blender installed on your machine**. No cloud, no account, no credits: nothing leaves your computer.

This is a local-only fork of [patch-gg/cloud-blender-skills](https://github.com/patch-gg/cloud-blender-skills), which is itself based on [EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills). Both are MIT. This fork removes the cloud backend and keeps the skills, scripts, tests and the fixes made upstream.

> **PT-BR:** 28 skills de Blender para o Claude Code que rodam só no Blender do seu computador, sem nuvem e sem créditos. Instale com os dois comandos abaixo.

## Install

You need **Blender 5.2 LTS or newer** (verified on 5.3) and Python 3.9+.

In Claude Code:

```
/plugin marketplace add juliana440/blender-skills-local
/plugin install blender-skills-local@blender-skills-local
```

Start a new session afterwards. Blender is found automatically (`$BLENDER_EXE` > `PATH` > standard install folders). If it isn't found, set `BLENDER_EXE` to its path.

Other agents (Codex, Cursor, Gemini CLI, OpenCode, Copilot): clone the repo and run `install/install.sh` (or `install/install.ps1` on Windows). It copies the skills into `.agents/skills` or `.claude/skills`.

## How it runs

Every skill script runs in headless Blender through one entry point and prints a compact JSON result:

```bash
python skills/blender-core/scripts/run_in_blender.py --blend in.blend <script.py> -- --objects Chair --save out.blend
python skills/blender-core/scripts/run_in_blender.py --expr "import bpy; print(bpy.app.version_string)"
python skills/blender-core/scripts/run_in_blender.py --which      # which Blender it will use
```

Or live, in your open Blender, through a blender-mcp server (`execute_blender_code`).

## The skills

| Skill | What it does |
|---|---|
| `blender-core` | Start here: runs code, routes tasks, 5.x API rules |
| `blender-scene-setup` | Units, naming, collections, asset libraries |
| `blender-hardsurface-modeling` | Bevels, booleans, weighted normals |
| `blender-sculpting` | Organic sculpting workflow |
| `blender-retopology-uv` | Retopology, UVs, texel density |
| `blender-pbr-materials` | Correct PBR materials from textures |
| `blender-texturing` | Edge wear, grime, dust, decals, trim sheets |
| `blender-texture-baking` | Normal, AO and curvature maps, ORM |
| `blender-geometry-nodes` | Procedural modeling from simple JSON |
| `blender-character-rigging` | Rigify, skinning, game skeletons |
| `blender-facial-shapekeys` | ARKit 52 blendshapes, visemes |
| `blender-animation` | Actions, mocap retargeting, loop checks, root motion |
| `blender-clothing` | Clothes that follow the body without clipping |
| `blender-hair-grooming` | Hair, fur and game hair cards |
| `blender-game-optimization` | Budgets, LODs, draw calls |
| `blender-export-pipelines` | Roblox, Unity, Unreal, Godot, web, USD |
| `blender-rendering` | Cycles and EEVEE, batch rendering |
| `blender-lighting-lookdev` | Studio lighting, HDRI, turntables |
| `blender-stylized-npr` | Toon/anime shading and outlines |
| `blender-environment-kits` | Terrain, forests, modular level kits |
| `blender-video-editing` | Edit videos, track cameras |
| `blender-simulation` | Rigid bodies, cloth, fluids |
| `blender-time-of-day` | Golden hour, night, fog and mood lighting |
| `blender-weather-fx` | Rain, snow, wet streets, puddles, lightning |
| `blender-addon-development` | Blender extensions |
| `blender-pipeline-automation` | Batch jobs and file conversion |
| `blender-asset-qa` | Catches z-fighting, floating parts, bad normals, weights and textures |
| `blender-workflow-recipes` | Complete asset playbooks |

## What changed from cloud-blender-skills

- Removed the `blender-cloud` skill and the `pch` cloud backend.
- `run_in_blender.py` always uses the local Blender; `blender-core` and `AGENTS.md` describe only local use.
- Removed `--cloud` from the test runner and the cloud hints from the installers.
- Removed the demo clips, the Patch page files and the logo artwork, which were made for the cloud version.

## Development

```bash
python tools/validate_skills.py      # spec + token budget checks
python tools/run_tests.py            # headless Blender tests (BLENDER_EXE to override)
```

## Credits and license

MIT, like the originals (see [LICENSE](LICENSE)). The skills, scripts and tests come from [EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills); later fixes from [patch-gg/cloud-blender-skills](https://github.com/patch-gg/cloud-blender-skills). This fork is not affiliated with Patch, EL4CTEO or the Blender Foundation. Blender is a trademark of the Blender Foundation.
