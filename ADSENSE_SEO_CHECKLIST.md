# Checklist de SEO e preparação para AdSense

Este projeto usa Blogger. O tema ajuda no SEO técnico, mas aprovação no AdSense também depende fortemente da qualidade, originalidade, confiança e utilidade do conteúdo publicado.

## Antes de solicitar o AdSense

- Publicar conteúdo original, útil e suficientemente aprofundado. Evitar páginas rasas, reescritas genéricas e textos feitos apenas para ranquear.
- Para conteúdo financeiro, revisar com cuidado informações que possam afetar decisões de dinheiro, crédito, investimentos, impostos ou benefícios.
- Ter páginas institucionais fáceis de encontrar: Sobre, Contato, Política de Privacidade, Termos de Uso e Política Editorial.
- Incluir um aviso claro de que o conteúdo financeiro é informativo e não constitui recomendação individual de investimento, quando aplicável.
- Exibir autor e, quando fizer sentido, informações sobre quem revisou o conteúdo.
- Mostrar data de publicação e data de atualização quando o artigo for revisado.
- Corrigir links quebrados e páginas 404 importantes.
- Manter navegação simples por categorias e links internos entre artigos relacionados.
- Não exagerar em anúncios, pop-ups, elementos enganosos ou botões que pareçam anúncios.
- Garantir que o site funcione bem no celular e não tenha conteúdo cortado.

## SEO por artigo

- Um único título principal claro e descritivo.
- Título e introdução devem responder ao tema da busca sem enrolação.
- Usar subtítulos que organizem de fato o conteúdo.
- Incluir exemplos, números, tabelas ou fontes quando realmente ajudarem.
- Adicionar links internos para artigos relacionados.
- Usar texto alternativo descritivo em imagens relevantes.
- Evitar repetir a mesma palavra-chave artificialmente.
- Atualizar artigos financeiros quando regras, taxas, valores ou datas mudarem.

## Configurações do Blogger

- Ativar HTTPS e redirecionamento HTTPS.
- Configurar uma descrição do blog coerente com o assunto do site.
- Verificar domínio/propriedade no Google Search Console.
- Enviar o sitemap do Blogger no Search Console.
- Conferir cobertura/indexação e corrigir erros antes de escalar a produção de conteúdo.
- Não forçar indexação de páginas de busca interna ou páginas sem conteúdo próprio.

## Alterações técnicas automatizadas no tema

O script `scripts/optimize_blogger_theme.py` foi criado para aplicar somente mudanças conservadoras e validar o XML antes do commit. Ele:

- libera zoom no mobile;
- adiciona idioma ao elemento HTML usando a localidade do Blogger;
- atualiza o contexto Schema.org para HTTPS;
- melhora o carregamento da fonte Open Sans com `display=swap` e `preconnect`;
- corrige o publisher estruturado que estava identificado como Blogger;
- restaura foco visível para navegação por teclado.

Não são inseridos meta robots globais, canonical duplicado, blocos de anúncio ou marcações de autor/logo inventadas.
