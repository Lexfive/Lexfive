# Scripts do perfil

| Script | Onde roda | O que gera |
|---|---|---|
| `build_banner.py` | no PC (precisa de Pillow) | `assets/banner-*.svg` — banner com a Samantha acenando quadro a quadro |
| `build_stats.py` | GitHub Action diária (`stats.yml`) | `assets/stats-*.svg` — contribuições, dias ativos, sequência, linguagens |
| `build_ai_activity.py` | no PC, toda segunda 10h (`atualizar-ia.cmd`) | `assets/ai-*.svg` — sessões por dia com Claude Code, Codex e Gemini (só contagens) |

Tudo em SVG com animação em CSS/SMIL, sem JavaScript e sem serviços de terceiros.
