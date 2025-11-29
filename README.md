# ReadmeStats

[![Generate GitHub Stats SVG](https://github.com/Otavio-Emanoel/ReadmeStats/actions/workflows/generate-stats.yml/badge.svg)](https://github.com/Otavio-Emanoel/ReadmeStats/actions/workflows/generate-stats.yml)

Workflow GitHub Actions que periodicamente gera um SVG com estatísticas públicas de um usuário GitHub (número de repositórios, seguidores, stars totais, avatar, pull requests, commits e issues) e calcula uma nota baseada na atividade. O SVG é salvo em `docs/stats.svg` e publicado via GitHub Pages.

## 📊 Estatísticas Geradas

O SVG inclui:
- **Repositórios**: Número total de repositórios públicos
- **Seguidores**: Número de seguidores
- **Stars**: Total de stars em todos os repositórios
- **Pull Requests**: Número de PRs criados
- **Commits**: Estimativa de commits nos repositórios
- **Issues**: Número de issues abertas
- **Avatar**: Imagem do perfil do usuário
- **Nota**: Classificação baseada na atividade (S, +A, A, +B, B, +C, C, D)

## 🎯 Sistema de Notas

| Nota | Pontuação |
|------|-----------|
| S    | 300+      |
| +A   | 200-299   |
| A    | 150-199   |
| +B   | 100-149   |
| B    | 75-99     |
| +C   | 50-74     |
| C    | 25-49     |
| D    | 0-24      |

## ⚡ Funcionalidades

- ✅ Execução periódica via cron (diariamente às 00:00 UTC)
- ✅ Execução manual via `workflow_dispatch`
- ✅ Suporte a `GITHUB_TOKEN` para autenticação
- ✅ Evita commits vazios (só comita quando há mudanças)
- ✅ Publicação automática via GitHub Pages

## 🚀 Como Usar

### 1. Fork este repositório

### 2. Ative GitHub Pages
- Vá em **Settings** > **Pages**
- Em **Source**, selecione **Deploy from a branch**
- Selecione a branch `main` e a pasta `/docs`
- Clique em **Save**

### 3. Execute o workflow
- Vá em **Actions** > **Generate GitHub Stats SVG**
- Clique em **Run workflow**
- Opcionalmente, insira um username diferente

### 4. Visualize seu SVG
Após a execução, seu SVG estará disponível em:
- Arquivo: `docs/stats.svg`
- GitHub Pages: `https://<seu-usuario>.github.io/ReadmeStats/`

## 📖 Uso no README

Para incluir o SVG no seu README:

```markdown
![GitHub Stats](https://raw.githubusercontent.com/<seu-usuario>/ReadmeStats/main/docs/stats.svg)
```

Ou use o link do GitHub Pages:

```markdown
![GitHub Stats](https://<seu-usuario>.github.io/ReadmeStats/stats.svg)
```

## 🔧 Personalização

### Alterar a frequência de atualização

Edite o cron no arquivo `.github/workflows/generate-stats.yml`:

```yaml
schedule:
  # Exemplos:
  - cron: '0 0 * * *'    # Diariamente às 00:00 UTC
  - cron: '0 */6 * * *'  # A cada 6 horas
  - cron: '0 0 * * 0'    # Semanalmente aos domingos
```

## 📁 Estrutura do Projeto

```
.
├── .github/
│   └── workflows/
│       └── generate-stats.yml    # Workflow do GitHub Actions
├── docs/
│   ├── index.html                # Página HTML para GitHub Pages
│   └── stats.svg                 # SVG gerado (após primeira execução)
├── scripts/
│   └── generate_stats.py         # Script de geração do SVG
└── README.md
```

## 📄 Licença

Este projeto está sob a licença MIT.
