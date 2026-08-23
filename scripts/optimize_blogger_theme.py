from pathlib import Path
import re
import xml.etree.ElementTree as ET

THEME = Path("theme-7997621208047243353.xml")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 ocorrência, encontrado {count}")
    return text.replace(old, new, 1)


def replace_or_accept(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    old_count = text.count(old)
    if old_count == 1:
        return text.replace(old, new, 1)
    if old_count > 1:
        raise RuntimeError(f"{label}: encontrado mais de um trecho antigo ({old_count})")
    raise RuntimeError(f"{label}: nem o trecho antigo nem o otimizado foram encontrados")


def replace_widget_settings(text: str, widget_id: str, settings: str) -> str:
    pattern = re.compile(
        rf"(?P<open><b:widget id='{re.escape(widget_id)}'[^>]*>\s*<b:widget-settings>).*?(?P<close></b:widget-settings>)",
        re.DOTALL,
    )
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f"widget {widget_id}: esperado 1 bloco, encontrado {len(matches)}")
    match = matches[0]
    replacement = match.group("open") + "\n" + settings.rstrip() + "\n            " + match.group("close")
    return text[: match.start()] + replacement + text[match.end() :]


def set_widget_visibility(text: str, widget_id: str, visible: bool) -> str:
    pattern = re.compile(rf"(<b:widget id='{re.escape(widget_id)}'[^>]*? visible=')(?:true|false)(')")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f"widget {widget_id}: visibilidade não encontrada de forma única")
    value = "true" if visible else "false"
    return pattern.sub(rf"\1{value}\2", text, count=1)


def validate_blogger_xml(text: str) -> None:
    """Valida a estrutura XML sem rejeitar namespaces legados tolerados pelo Blogger."""
    declared = set(re.findall(r"xmlns:([A-Za-z_][\w.-]*)=", text))
    element_prefixes = set(re.findall(r"</?([A-Za-z_][\w.-]*):[A-Za-z_]", text))
    attribute_prefixes = set(re.findall(r"\s([A-Za-z_][\w.-]*):[A-Za-z_][\w.-]*\s*=", text))
    missing = sorted((element_prefixes | attribute_prefixes) - declared - {"xml", "xmlns"})

    validation_text = text
    if missing:
        namespace_attrs = "".join(
            f" xmlns:{prefix}='urn:blogger-legacy:{prefix}'" for prefix in missing
        )
        validation_text = validation_text.replace("<html ", "<html" + namespace_attrs + " ", 1)

    ET.fromstring(validation_text)


def main() -> None:
    text = THEME.read_text(encoding="utf-8")
    original = text

    # 1) Mobile e acessibilidade: não bloquear o zoom do usuário.
    text = replace_or_accept(
        text,
        "content='width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1' name='viewport'",
        "content='width=device-width, initial-scale=1' name='viewport'",
        "viewport",
    )

    # 2) Idioma do documento a partir da configuração do Blogger.
    html_old = (
        "<html b:css='false' b:defaultwidgetversion='2' b:layoutsVersion='3' "
        "b:responsive='true' b:templateVersion='1.0.0' "
        "expr:class='data:blog.languageDirection' expr:dir='data:blog.languageDirection'"
    )
    html_new = html_old + " expr:lang='data:blog.locale'"
    text = replace_or_accept(text, html_old, html_new, "html lang")

    # 3) Schema.org moderno na marcação já existente.
    text = text.replace("&quot;http://schema.org&quot;", "&quot;https://schema.org&quot;")

    # 4) Melhor carregamento da fonte sem trocar a identidade visual.
    old_font = "href='//fonts.googleapis.com/css?family=Open+Sans:400,400i,700,700i' media='all' rel='stylesheet' type='text/css'"
    new_font = "href='https://fonts.googleapis.com/css?family=Open+Sans:400,400i,700,700i&amp;display=swap' media='all' rel='stylesheet' type='text/css'"
    text = replace_or_accept(text, old_font, new_font, "Google Fonts")
    font_stylesheet = f"    <link {new_font}/>"
    preconnect = (
        "    <link href='https://fonts.googleapis.com' rel='preconnect'/>\n"
        "    <link crossorigin='anonymous' href='https://fonts.gstatic.com' rel='preconnect'/>\n"
    )
    if "href='https://fonts.googleapis.com' rel='preconnect'" not in text:
        text = replace_once(text, font_stylesheet, preconnect + font_stylesheet, "font preconnect")

    # 5) Publisher real do site em vez do publisher fictício 'Blogger'.
    publisher_pattern = re.compile(
        r"(?P<indent>[ \t]*)<b:includable id='postMetadataJSONPublisher'>.*?</b:includable>",
        re.DOTALL,
    )
    matches = list(publisher_pattern.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f"publisher metadata: esperado 1 bloco, encontrado {len(matches)}")
    current_publisher = matches[0].group(0)
    if "&quot;name&quot;: &quot;Blogger&quot;" in current_publisher:
        indent = matches[0].group("indent")
        publisher_replacement = (
            f"{indent}<b:includable id='postMetadataJSONPublisher'>\n"
            f"{indent} &quot;publisher&quot;: {{\n"
            f"{indent}    &quot;@type&quot;: &quot;Organization&quot;,\n"
            f"{indent}    &quot;name&quot;: &quot;<data:blog.title.escaped/>&quot;,\n"
            f"{indent}    &quot;url&quot;: &quot;<data:blog.homepageUrl/>&quot;\n"
            f"{indent}  }},\n"
            f"{indent}</b:includable>"
        )
        text = publisher_pattern.sub(publisher_replacement, text, count=1)
    elif not (
        "<data:blog.title.escaped/>" in current_publisher
        and "<data:blog.homepageUrl/>" in current_publisher
    ):
        raise RuntimeError("publisher metadata está em um formato inesperado")

    # 6) Remover links de demonstração do fornecedor do menu e apontar para o próprio site.
    demo_replacements = {
        "https://topseo-templatesyard.blogspot.com/p/about-us.html": "/p/sobre.html",
        "https://topseo-templatesyard.blogspot.com/p/contact-us.html": "/p/contato.html",
    }
    for old, new in demo_replacements.items():
        text = text.replace(old, new)
    text = re.sub(
        r"(<b:widget-setting name='text-\d+'>)About(</b:widget-setting>)",
        r"\1Sobre\2",
        text,
    )
    text = re.sub(
        r"(<b:widget-setting name='text-\d+'>)Contact(?: Us)?(</b:widget-setting>)",
        r"\1Contato\2",
        text,
    )

    # 7) Menu principal limpo e voltado ao nicho de finanças.
    main_menu = """               <b:widget-setting name='sorting'>NONE</b:widget-setting>
               <b:widget-setting name='text-0'>Home-icon</b:widget-setting>
               <b:widget-setting name='link-0'>/</b:widget-setting>
               <b:widget-setting name='text-1'>Cartões</b:widget-setting>
               <b:widget-setting name='link-1'>/search/label/Cartoes</b:widget-setting>
               <b:widget-setting name='text-2'>Bancos</b:widget-setting>
               <b:widget-setting name='link-2'>/search/label/Bancos</b:widget-setting>
               <b:widget-setting name='text-3'>Investimentos</b:widget-setting>
               <b:widget-setting name='link-3'>/search/label/Investimentos</b:widget-setting>
               <b:widget-setting name='text-4'>Economia</b:widget-setting>
               <b:widget-setting name='link-4'>/search/label/Economia</b:widget-setting>
               <b:widget-setting name='text-5'>Renda Extra</b:widget-setting>
               <b:widget-setting name='link-5'>/search/label/Renda%20Extra</b:widget-setting>
               <b:widget-setting name='text-6'>Sobre</b:widget-setting>
               <b:widget-setting name='link-6'>/p/sobre.html</b:widget-setting>"""
    text = replace_widget_settings(text, "LinkList74", main_menu)

    # 8) Rodapé com páginas institucionais essenciais para transparência e AdSense.
    footer_menu = """          <b:widget-setting name='sorting'>NONE</b:widget-setting>
          <b:widget-setting name='text-0'>Início</b:widget-setting>
          <b:widget-setting name='link-0'>/</b:widget-setting>
          <b:widget-setting name='text-1'>Sobre</b:widget-setting>
          <b:widget-setting name='link-1'>/p/sobre.html</b:widget-setting>
          <b:widget-setting name='text-2'>Contato</b:widget-setting>
          <b:widget-setting name='link-2'>/p/contato.html</b:widget-setting>
          <b:widget-setting name='text-3'>Privacidade</b:widget-setting>
          <b:widget-setting name='link-3'>/p/politica-de-privacidade.html</b:widget-setting>
          <b:widget-setting name='text-4'>Termos</b:widget-setting>
          <b:widget-setting name='link-4'>/p/termos-de-uso.html</b:widget-setting>
          <b:widget-setting name='text-5'>Política Editorial</b:widget-setting>
          <b:widget-setting name='link-5'>/p/politica-editorial.html</b:widget-setting>
          <b:widget-setting name='text-6'>Aviso Financeiro</b:widget-setting>
          <b:widget-setting name='link-6'>/p/aviso-financeiro.html</b:widget-setting>"""
    text = replace_widget_settings(text, "LinkList76", footer_menu)

    # 9) Ocultar perfis sociais de demonstração até existirem perfis oficiais do projeto.
    text = set_widget_visibility(text, "LinkList73", False)
    text = set_widget_visibility(text, "LinkList75", False)

    # 10) Aviso financeiro em todos os artigos, importante para conteúdo YMYL.
    body_old = """              <div class='post-body post-content' id='post-body'>
                <data:post.body/>
              </div>
                 <!-- Ads after post content. -->"""
    body_new = """              <div class='post-body post-content' id='post-body'>
                <data:post.body/>
              </div>
              <b:if cond='data:view.isPost'>
                <aside class='finance-disclaimer' role='note'><strong>Aviso:</strong> Este conteúdo tem caráter educativo e informativo e não constitui recomendação individual de investimento, crédito ou contratação de produto financeiro. Compare custos, riscos e condições e consulte profissionais habilitados quando necessário.</aside>
              </b:if>
                 <!-- Ads after post content. -->"""
    text = replace_or_accept(text, body_old, body_new, "aviso financeiro nos artigos")

    # 11) UX/acessibilidade e apresentação do aviso.
    skin_end = "]]></b:skin>"
    extra_css = """
/* SEO/UX: foco visível para navegação por teclado */
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{
    outline:2px solid $(main.color);
    outline-offset:2px
}
/* Transparência editorial para conteúdo financeiro */
.finance-disclaimer{
    margin:24px 0 0;
    padding:16px;
    background:#f7f8fa;
    border:1px solid #e4e7eb;
    border-radius:8px;
    color:#4b5563;
    font-size:13px;
    line-height:1.6
}
.finance-disclaimer strong{color:#1f2937}
""".strip()
    if "/* Transparência editorial para conteúdo financeiro */" not in text:
        # Remove a versão anterior do bloco de foco, se já existir, para não duplicar.
        text = re.sub(
            r"/\* SEO/UX: foco visível para navegação por teclado \*/\s*a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible\{.*?\}\s*",
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )
        text = replace_once(text, skin_end, extra_css + "\n" + skin_end, "CSS final")

    validate_blogger_xml(text)

    if text != original:
        THEME.write_text(text, encoding="utf-8")
        print("Tema finalizado para finanças, SEO, confiança e AdSense.")
    else:
        print("Tema já estava finalizado e validado.")


if __name__ == "__main__":
    main()
