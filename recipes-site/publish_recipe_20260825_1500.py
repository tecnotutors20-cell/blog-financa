#!/usr/bin/env python3
# Afternoon long-tail companion for Cluster 1.
# Reuse the proven Blogger/OAuth/image pipeline from the morning publisher while changing the editorial payload.
from pathlib import Path
import runpy

base = Path(__file__).with_name('publish_recipe_20260825_1000.py')
src = base.read_text(encoding='utf-8')
repls = {
"Purê de Abóbora com Carne para Bebê: Receita Cremosa e Fácil":"Purê de Batata-Doce com Frango Desfiado para Bebê: Receita Fácil",
"pure-abobora-carne-bebe":"pure-batata-doce-frango-bebe",
"Purê de Abóbora com Carne para Bebê":"Purê de Batata-Doce com Frango Desfiado para Bebê",
"purê de abóbora com carne para bebê":"purê de batata-doce com frango desfiado para bebê",
"papinha de abóbora com carne":"purê de batata-doce com frango",
"200 g de abóbora cabotiá ou moranga, descascada e cortada em cubos":"200 g de batata-doce, descascada e cortada em cubos",
"100 g de carne bovina moída":"100 g de peito ou sobrecoxa de frango sem osso e sem pele",
"2 colheres (sopa) de cebola bem picada":"2 colheres (sopa) de cenoura bem picada",
"Cozinhe a abóbora em pouca água até ficar muito macia.":"Cozinhe a batata-doce e a cenoura em pouca água até ficarem muito macias.",
"Em outra panela, cozinhe a carne moída com a cebola, mexendo e desfazendo os grumos, até ficar completamente cozida.":"Em outra panela, cozinhe o frango completamente e desfie muito bem com dois garfos.",
"Amasse a abóbora com um garfo e ajuste a umidade com pequenas quantidades da água do cozimento.":"Amasse a batata-doce e a cenoura com um garfo e ajuste a umidade com pequenas quantidades da água do cozimento.",
"Misture a carne bem desmanchada ao purê e adapte a textura às habilidades da criança.":"Misture o frango bem desfiado ao purê e adapte a textura às habilidades da criança.",
"Purê espesso de abóbora com carne moída bem cozida, com textura ajustável para a alimentação complementar.":"Purê espesso de batata-doce com frango bem desfiado, com textura ajustável para a alimentação complementar.",
"'Purê de Abóbora com Carne para Bebê'. Show a thick, spoonable pumpkin puree with finely crumbled well-cooked ground beef visibly mixed through it, warm orange pumpkin color, realistic homemade texture.":"'Purê de Batata-Doce com Frango Desfiado para Bebê'. Show a thick, spoonable sweet potato puree with very finely shredded well-cooked chicken visibly mixed through it, warm golden-orange color, realistic homemade texture.",
"The puree must be thick rather than liquid, with fork-mashed texture and small soft beef granules.":"The puree must be thick rather than liquid, with fork-mashed texture and small soft strands of shredded chicken.",
"Este purê de abóbora com carne é uma opção simples para o almoço ou jantar quando a criança já iniciou a alimentação complementar.":"Este purê de batata-doce com frango desfiado é uma opção simples para variar o almoço ou jantar quando a criança já iniciou a alimentação complementar.",
"A proposta é deixar a abóbora bem macia e a carne moída totalmente cozida e desmanchada, formando um preparo espesso que pode ser adaptado com o garfo conforme as habilidades da criança.":"A proposta é deixar a batata-doce e a cenoura bem macias e o frango totalmente cozido e muito bem desfiado, formando um preparo espesso que pode ser adaptado com o garfo conforme as habilidades da criança.",
"200 g de abóbora cabotiá ou moranga, descascada e cortada em cubos":"200 g de batata-doce, descascada e cortada em cubos",
"100 g de carne bovina moída":"100 g de peito ou sobrecoxa de frango sem osso e sem pele",
"2 colheres (sopa) de cebola bem picada":"2 colheres (sopa) de cenoura bem picada",
"Cozinhe a abóbora em pouca água até ficar muito macia e fácil de amassar com o garfo.":"Cozinhe a batata-doce e a cenoura em pouca água até ficarem muito macias e fáceis de amassar com o garfo.",
"Enquanto isso, coloque a carne moída e a cebola em outra panela. Cozinhe em fogo médio, mexendo e desfazendo os grumos, até que a carne esteja completamente cozida.":"Enquanto isso, cozinhe o frango completamente em outra panela. Retire e desfie muito bem com dois garfos, deixando fios curtos e macios.",
"Escorra a maior parte da água da abóbora, reservando um pouco. Amasse com o garfo até formar um purê espesso.":"Escorra a maior parte da água da batata-doce e da cenoura, reservando um pouco. Amasse com o garfo até formar um purê espesso.",
"Misture a carne bem desmanchada ao purê.":"Misture o frango bem desfiado ao purê.",
"A carne deve estar em grânulos pequenos e macios, sem blocos compactos.":"O frango deve estar em fios curtos, pequenos e macios, sem pedaços secos ou compactos.",
"desfaça muito bem os grumos da carne":"desfie muito bem o frango",
"A abóbora cabotiá pode ser trocada por moranga. Para variar o preparo, outra carne bovina moída pode ser usada desde que seja completamente cozida e fique com textura macia.":"A batata-doce pode ser trocada por mandioquinha. A cenoura pode ser omitida ou trocada por abóbora, mantendo os ingredientes bem cozidos e macios.",
"Como a receita contém carne moída":"Como a receita contém frango cozido",
"Posso deixar a carne separada do purê?":"Posso deixar o frango separado do purê?",
"purê de abóbora com carne":"purê de batata-doce com frango",
}
for a,b in repls.items(): src = src.replace(a,b)
# Replace related links with three distinct, existing companion recipes.
start = src.find("<h2>Receitas relacionadas</h2>")
end = src.find("<h2>Referências oficiais</h2>")
if start != -1 and end != -1:
    related = """<h2>Receitas relacionadas</h2>\n<ul>\n<li><a href='https://www.receitasparapequenos.site/2026/08/pure-de-abobora-com-carne-para-bebe.html'>Purê de Abóbora com Carne para Bebê</a></li>\n<li><a href='https://www.receitasparapequenos.site/2026/07/pure-de-feijao-com-abobora-para-bebes.html'>Purê de Feijão com Abóbora para Bebês</a></li>\n<li><a href='https://www.receitasparapequenos.site/2026/07/sopa-creme-de-abobora-com-lentilha-para.html'>Sopa Creme de Abóbora com Lentilha para Bebês</a></li>\n</ul>\n"""
    src = src[:start] + related + src[end:]
# Use a distinct recipe yield but do not add nutrition or fabricated timing.
src = src.replace("'recipeYield': '2 porções pequenas'", "'recipeYield': '2 porções pequenas'")
# Write an ephemeral generated module and execute it.
tmp = Path(__file__).with_name('_generated_1500.py')
tmp.write_text(src, encoding='utf-8')
try:
    runpy.run_path(str(tmp), run_name='__main__')
finally:
    tmp.unlink(missing_ok=True)
