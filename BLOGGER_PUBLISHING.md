# Publicação segura no Blogger

O repositório está preparado para manter o tema, as páginas institucionais e os artigos do blog de finanças.

## O que já está pronto

- Tema otimizado para SEO técnico, mobile, acessibilidade e confiança editorial.
- Menu principal de finanças.
- Rodapé com páginas institucionais.
- Aviso financeiro nos artigos.
- Widgets e links demonstrativos do template ocultados.
- 6 páginas institucionais em `content/blogger_pages.json`.
- 8 artigos evergreen em `content/blogger_posts.json`.
- Publicador em `scripts/publish_blogger.py`.
- Workflow manual em `.github/workflows/publish-blogger.yml`.

## Autorização necessária

A API oficial do Blogger exige OAuth 2.0 com o escopo:

`https://www.googleapis.com/auth/blogger`

Nunca coloque a senha da conta Google no código, em commit, issue ou arquivo do repositório.

Crie um cliente OAuth do tipo **Desktop app** no Google Cloud e execute localmente:

```bash
GOOGLE_CLIENT_ID="..." GOOGLE_CLIENT_SECRET="..." python scripts/get_blogger_refresh_token.py
```

O script abre a tela oficial de consentimento do Google e, ao final, mostra os blogs autorizados e o `BLOGGER_BLOG_ID` correto.

## Segredos do GitHub Actions

Cadastre em **Settings → Secrets and variables → Actions**:

- `BLOGGER_BLOG_ID`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

Depois, o workflow **Publish Blogger content** publica/atualiza as páginas e os artigos de forma idempotente.

## Tema do Blogger

A Blogger API v3 não oferece recurso oficial para publicar o tema/template XML. Por isso, o arquivo `theme-7997621208047243353.xml` precisa ser importado no painel **Blogger → Tema** quando houver uma nova versão de layout.

## Antes de solicitar AdSense

Além do código, o site deve ter conteúdo útil e original suficiente, navegação funcional, páginas de transparência publicadas, autoria identificável, política de privacidade atualizada e nenhuma página quebrada ou placeholder de demonstração. A aprovação nunca é garantida e depende da análise do Google.
