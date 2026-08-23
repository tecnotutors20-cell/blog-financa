from pathlib import Path
import re
import xml.etree.ElementTree as ET

THEME = Path("theme-7997621208047243353.xml")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 ocorrência, encontrado {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = THEME.read_text(encoding="utf-8")
    original = text

    # Acessibilidade e mobile: não impedir o usuário de ampliar a página.
    text = replace_once(
        text,
        "content='width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1' name='viewport'",
        "content='width=device-width, initial-scale=1' name='viewport'",
        "viewport",
    )

    # Schema.org moderno na marcação WebSite existente.
    text = text.replace("&quot;http://schema.org&quot;", "&quot;https://schema.org&quot;")

    # Melhorar carregamento da fonte sem alterar a tipografia do tema.
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

    # O tema informava incorretamente que o publisher de todo artigo era “Blogger”.
    # Substituímos por nome e URL do próprio site, sem inventar logo ou organização.
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
        f"{indent}  <meta expr:content='data:blog.homepageUrl' property='url'/>\n"
        f"{indent}  <meta expr:content='data:blog.title' property='name'/>\n"
        f"{indent}</b:includable>"
    )
    text = publisher_pattern.sub(publisher_replacement, text, count=1)

    if text == original:
        raise RuntimeError("Nenhuma alteração foi aplicada")

    # O template Blogger é XML; falhar aqui impede commit de arquivo malformado.
    ET.fromstring(text)
    THEME.write_text(text, encoding="utf-8")
    print("Tema otimizado e XML validado com sucesso.")


if __name__ == "__main__":
    main()
