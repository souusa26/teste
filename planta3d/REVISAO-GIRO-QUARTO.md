# Giro horário do quarto

O quarto foi reorganizado 90° no sentido horário visto de cima. A porta e a luminária continuam nas posições anteriores; TV, setup e armários aéreos foram para a antiga parede do guarda-roupa; o guarda-roupa foi para a antiga parede da cama; a cama e a janela foram para a parede seguinte. A antiga abertura da janela foi fechada no modelo, e uma abertura nova foi criada na parede correspondente.

As dimensões continuam aproximadas. Foi feita checagem geométrica estática entre cama, cadeira, mesa, guarda-roupa e porta sem interseções, mas a abertura real da porta e o movimento da cadeira não foram simulados. A cadeira fica próxima da cama; confirme as medidas reais antes de usar o modelo para planejar uma mudança física.

Os oito identificadores interativos foram mantidos. A TV do quarto mudou de lugar e orientação: nos cartões `floor3d-card`, seu `light_direction` agora é `x: -1`, `y: 0`, `z: 0`. Na planta fixa, o ponto de controle da TV do quarto mudou para `left: 62.66%`, `top: 50.81%`. As imagens das plantas fixa opaca e transparente e os YAMLs de exemplo foram atualizados; mantenha as dez imagens de cada versão juntas e copie o YAML apropriado ou aplique essas mudanças ao seu cartão personalizado.

O Home Assistant não foi acessado nem alterado. Faça backup e teste arquivos, interação das TVs/luzes, posição do ícone e desempenho no celular quando instalar. As telas decorativas são exibidas na planta fixa; a versão 3D não simula o conteúdo da TV.
