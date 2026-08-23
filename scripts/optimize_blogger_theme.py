from pathlib import Path
import re
import xml.etree.ElementTree as ET

THEME = Path("theme-7997621208047243353.xml")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 ocorrência, encontrado {count}")
    return text.replace(old, new, 1)


def validate_blogger_xml(text: str) -> None:
    """Valida o XML sem rejeitar namespaces legados que o Blogger tolera.

    Alguns templates antigos usam tags como <g:plusone> sem declarar xmlns:g.
    Isso já existe no arquivo original e o Blogger aceita. Para validar a estrutura
    sem mascarar erros novos, declaramos apenas namespaces ausentes numa cópia
    temporária antes de passar o texto ao parser XML.
    """
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

    # 1) Mobile/acessibilidade: não bloquear o zoom do usuário.
    text = replace_once(
        text,
        "content='width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1' name='viewport'",
        "content='width=device-width, initial-scale=1' name='viewport'",
        "viewport",
    )

    # 2) Declarar o idioma do documento usando a localidade configurada no Blogger.
    html_old = (
        "<html b:css='false' b:defaultwidgetversion='2' b:layoutsVersion='3' "
        "b:responsive='true' b:templateVersion='1.0.0' "
        "expr:class='data:blog.languageDirection' expr:dir='data:blog.languageDirection'"
    )
    html_new = html_old + " expr:lang='data:blog.locale'"
    text = replace_once(text, html_old, html_new, "html lang")

    # 3) Schema.org moderno na marcação WebSite já existente.
    text = text.replace("&quot;http://schema.org&quot;", "&quot;https://schema.org&quot;")

    # 4) Melhorar carregamento da fonte sem alterar a tipografia do tema.
    text = replace_once(
        text,
        "href='//fonts.googleapis.com/css?family=Open+Sans:400,400i,700,700i' media='all' rel='stylesheet' type='text/css'",
        "href='https://fonts.googleapis.com/css?family=Open+Sans:400,400i,700,700i&amp;display=swap' media='all' rel='stylesheet' type='text/css'",
        "Google Fonts",
    )

    font_stylesheet = "    <link href='https://fonts.googleapis.com/css?family=Open+Sans:400,400i,700,700i&amp;display=swap' media='all' rel='stylesheet' type='text/css'/>"
    preconnect = (
        "    <link href='https://fonts.googleapis.com' rel='preconnect'/>\n"
        "    <link crossorigin='anonymous' href='https://fonts.gstatic.com' rel='preconnect'/>\n"
    )
    text = replace_once(text, font_stylesheet, preconnect + font_stylesheet, "font preconnect")

    # 5) Corrigir publisher dos dados estruturados dos artigos.
    # O tema atribuía todos os artigos ao publisher “Blogger”, com o logo do Blogger.
    # Mantemos o formato JSON original do includable e usamos o nome/URL do próprio site.
    publisher_pattern = re.compile(
        r"(?P<indent>[ \t]*)<b:includable id='postMetadataJSONPublisher'>.*?</b:includable>",
        re.DOTALL,
    )
    matches = list(publisher_pattern.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(
            f"publisher metadata: esperado 1 bloco, encontrado {len(matches)}"
        )
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

    # 6) Restaurar foco visível para navegação por teclado.
    # O reset do tema remove outline de vários elementos.
    skin_end = "]]></b:skin>"
    focus_css = """
/* SEO/UX: foco visível para navegação por teclado */
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{
    outline:2px solid $(main.color);
    outline-offset:2px
}
""".strip()
    if focus_css not in text:
        text = replace_once(text, skin_end, focus_css + "\n" + skin_end, "focus CSS")

    if text == original:
        raise RuntimeError("Nenhuma alteração foi aplicada")

    # Validação estrutural antes de escrever o arquivo alterado.
    validate_blogger_xml(text)
    THEME.write_text(text, encoding="utf-8")
    print("Tema otimizado e XML validado com sucesso.")


if __name__ == "__main__":
    main()
