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
    """Aplica a troca uma vez ou aceita o estado já otimizado."""
    # Checar primeiro o estado novo evita duplicar quando `old` é prefixo de `new`.
    if new in text:
        return text
    old_count = text.count(old)
    if old_count == 1:
        return text.replace(old, new, 1)
    if old_count > 1:
        raise RuntimeError(f"{label}: encontrado mais de um trecho antigo ({old_count})")
    raise RuntimeError(f"{label}: nem o trecho antigo nem o otimizado foram encontrados")


def validate_blogger_xml(text: str) -> None:
    """Valida o XML sem rejeitar namespaces legados tolerados pelo Blogger.

    Alguns temas antigos usam tags como <g:plusone> sem declarar xmlns:g.
    Para validar a estrutura sem alterar o arquivo real, declaramos namespaces
    ausentes somente numa cópia temporária usada pelo parser.
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
    text = replace_or_accept(
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
    text = replace_or_accept(text, html_old, html_new, "html lang")

    # 3) Schema.org moderno na marcação WebSite já existente.
    text = text.replace("&quot;http://schema.org&quot;", "&quot;https://schema.org&quot;")

    # 4) Melhorar carregamento da fonte sem alterar a tipografia do tema.
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

    # 5) Corrigir publisher dos dados estruturados dos artigos.
    publisher_pattern = re.compile(
        r"(?P<indent>[ \t]*)<b:includable id='postMetadataJSONPublisher'>.*?</b:includable>",
        re.DOTALL,
    )
    matches = list(publisher_pattern.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(
            f"publisher metadata: esperado 1 bloco, encontrado {len(matches)}"
        )

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

    # 6) Restaurar foco visível para navegação por teclado.
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

    # Sempre validar, inclusive quando o tema já está otimizado.
    validate_blogger_xml(text)

    if text != original:
        THEME.write_text(text, encoding="utf-8")
        print("Tema otimizado e XML validado com sucesso.")
    else:
        print("Tema já estava otimizado; XML validado com sucesso.")


if __name__ == "__main__":
    main()
