#!/usr/bin/env python3
from pathlib import Path
import runpy

base = Path(__file__).with_name('publish_recipe_20260825_1000.py')
src = base.read_text(encoding='utf-8')
repls = {
"Purê de Abóbora com Carne para Bebê: Receita Cremosa e Fácil":"Creme de Lentilha com Legumes para Bebê: Receita Cremosa",
"pure-abobora-carne-bebe":"creme-lentilha-legumes-bebe",
"Purê de Abóbora com Carne para Bebê":"Creme de Lentilha com Legumes para Bebê",
"purê de abóbora com carne para bebê":"creme de lentilha com legumes para bebê",
"papinha de abóbora com carne":"creme de lentilha com legumes",
"200 g de abóbora cabotiá ou moranga, descascada e cortada em cubos":"1/2 xícara de lentilha seca, escolhida e lavada",
"100 g de carne bovina moída":"1 cenoura pequena, descascada e picada",
"2 colheres (sopa) de cebola bem picada":"1/2 abobrinha pequena, picada",
"Cozinhe a abóbora em pouca água até ficar muito macia.":"Cozinhe a lentilha, a cenoura e a abobrinha em água até todos os ingredientes ficarem muito macios.",
"Em outra panela, cozinhe a carne moída com a cebola, mexendo e desfazendo os grumos, até ficar completamente cozida.":"Amasse os legumes e parte das lentilhas com um garfo, preservando uma textura espessa e macia.",
"Amasse a abóbora com um garfo e ajuste a umidade com pequenas quantidades da água do cozimento.":"Ajuste a consistência com pequenas quantidades da própria água do cozimento, sem deixar o creme líquido.",
"Misture a carne bem desmanchada ao purê e adapte a textura às habilidades da criança.":"Misture bem e adapte a textura às habilidades da criança antes de servir.",
"Purê espesso de abóbora com carne moída bem cozida, com textura ajustável para a alimentação complementar.":"Creme espesso de lentilha com cenoura e abobrinha bem cozidas, com textura ajustável para a alimentação complementar.",
"'Purê de Abóbora com Carne para Bebê'. Show a thick, spoonable pumpkin puree with finely crumbled well-cooked ground beef visibly mixed through it, warm orange pumpkin color, realistic homemade texture.":"'Creme de Lentilha com Legumes para Bebê'. Show a thick spoonable lentil cream with visibly fork-mashed lentils, carrot and zucchini, warm earthy golden-brown and orange tones, realistic homemade texture.",
"The puree must be thick rather than liquid, with fork-mashed texture and small soft beef granules.":"The lentil cream must be thick rather than liquid, with a fork-mashed texture and small soft pieces of carrot and zucchini.",
"Este purê de abóbora com carne é uma opção simples para o almoço ou jantar quando a criança já iniciou a alimentação complementar.":"Este creme de lentilha com legumes é uma opção simples para variar o almoço ou jantar quando a criança já iniciou a alimentação complementar.",
"A proposta é deixar a abóbora bem macia e a carne moída totalmente cozida e desmanchada, formando um preparo espesso que pode ser adaptado com o garfo conforme as habilidades da criança.":"A proposta é cozinhar lentilha, cenoura e abobrinha até ficarem muito macias, formando um preparo espesso que pode ser amassado com o garfo conforme as habilidades da criança.",
"Cozinhe a abóbora em pouca água até ficar muito macia e fácil de amassar com o garfo.":"Cozinhe a lentilha, a cenoura e a abobrinha em água até tudo ficar muito macio e fácil de amassar com o garfo.",
"Enquanto isso, coloque a carne moída e a cebola em outra panela. Cozinhe em fogo médio, mexendo e desfazendo os grumos, até que a carne esteja completamente cozida.":"Durante o cozimento, mexa de vez em quando e acrescente pequenas quantidades de água se necessário para evitar que o fundo seque antes de a lentilha amaciar.",
"Escorra a maior parte da água da abóbora, reservando um pouco. Amasse com o garfo até formar um purê espesso.":"Reserve um pouco da água do cozimento e amasse os legumes e parte das lentilhas com o garfo até formar um creme espesso.",
"Misture a carne bem desmanchada ao purê.":"Misture tudo até distribuir os legumes e a lentilha de maneira uniforme.",
"A carne deve estar em grânulos pequenos e macios, sem blocos compactos.":"A lentilha e os legumes devem estar muito macios, sem pedaços firmes, e o creme deve permanecer espesso na colher.",
"desfaça muito bem os grumos da carne":"amasse muito bem a lentilha e os legumes",
"A abóbora cabotiá pode ser trocada por moranga. Para variar o preparo, outra carne bovina moída pode ser usada desde que seja completamente cozida e fique com textura macia.":"A abobrinha pode ser trocada por abóbora ou chuchu, mantendo os legumes bem cozidos e macios. Mudanças relacionadas a alergias ou necessidades específicas devem ser discutidas com profissional habilitado.",
"Como a receita contém carne moída":"Como a receita contém lentilha e legumes cozidos",
"Posso deixar a carne separada do purê?":"Posso deixar alguns legumes separados do creme?",
"purê de abóbora com carne":"creme de lentilha com legumes",
"['Alimentação complementar', 'Papinhas e purês', 'Abóbora', 'Carne']":"['Alimentação complementar', 'Papinhas e purês', 'Lentilha', 'Legumes']",
"Add unique AI food photo for pumpkin beef puree":"Add unique AI food photo for lentil vegetable cream",
"Record published pumpkin beef puree recipe":"Record published lentil vegetable cream recipe"
}
for a,b in repls.items(): src = src.replace(a,b)
# Avoid collision with today's two earlier Cluster 1 recipes and use three existing internal links.
start = src.find("<h2>Receitas relacionadas</h2>")
end = src.find("<h2>Referências oficiais</h2>")
if start != -1 and end != -1:
    related = """<h2>Receitas relacionadas</h2>\n<ul>\n<li><a href='https://www.receitasparapequenos.site/2026/08/pure-de-abobora-com-carne-para-bebe.html'>Purê de Abóbora com Carne para Bebê</a></li>\n<li><a href='https://www.receitasparapequenos.site/2026/08/pure-de-batata-doce-com-frango-desfiado.html'>Purê de Batata-Doce com Frango Desfiado para Bebê</a></li>\n<li><a href='https://www.receitasparapequenos.site/2026/07/sopa-creme-de-abobora-com-lentilha-para.html'>Sopa Creme de Abóbora com Lentilha para Bebês</a></li>\n</ul>\n"""
    src = src[:start] + related + src[end:]
# Strengthen duplicate detection for the distinct evening intent.
src = src.replace("('purê de abóbora' in title and 'carne' in title)", "('creme de lentilha' in title and 'legume' in title)")
tmp = Path(__file__).with_name('_generated_2000.py')
tmp.write_text(src, encoding='utf-8')
try:
    runpy.run_path(str(tmp), run_name='__main__')
finally:
    tmp.unlink(missing_ok=True)
