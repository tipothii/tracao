# Magni

App de calistenia **Magni** (força do próprio corpo) instalável (PWA): programas, escadas de progressão, player de treino com cronômetro e progresso. Não pede conta, e os dados ficam só no aparelho.

- Funciona no **iPhone** (Safari → Compartilhar → Adicionar à Tela de Início), no **Android** (Instalar app) e no computador.
- Funciona **sem internet** depois de aberto uma vez.
- Pesa cerca de **460 KB** no total, contando fontes e ícones.

## Estrutura

| Caminho | O que é |
|---|---|
| `index.html` | O app inteiro: telas, dados de exercícios e programas, animações e player. É a única fonte a editar. |
| `pwa/` | Manifest, service worker, ícones (SVG e PNG) e fontes locais. |
| `build.py` | Gera `docs/` a partir de `index.html` + `pwa/`. |
| `docs/` | Versão publicada pelo GitHub Pages. Não edite à mão. |
| `VERSION` | Número da versão mostrado em Ajustes. |

## Como publicar uma nova versão

1. Edite `index.html`.
2. Suba o número em `VERSION` (por exemplo, `1.0.1`).
3. Rode `python3 build.py`.
4. Faça commit e push. O GitHub Pages atualiza em cerca de 1 minuto.

Quem já tem o app instalado vê o aviso **Nova versão disponível** ao abrir e atualiza com um toque, sem perder dados.

## GitHub Pages (uma vez só)

No repositório: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `docs`**.

## Ícones

Os ícones saem da runa do logo (`pwa/brand/rune-mask.png`, extraída de `pwa/brand/logo-original.png`) em bronze sobre verde-pinho. Para outra versão, gere novos PNGs em `pwa/icons/` com os mesmos nomes.
