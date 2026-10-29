# Revisão do quarto usando as fotos

Prévia atualizada após o giro: [previa_quarto.png](previa_quarto.png). Veja também [REVISAO-GIRO-QUARTO.md](REVISAO-GIRO-QUARTO.md).

O modelo foi aproximado das fotos: guarda-roupa branco de correr com trilhos, cama de base escura e roupa cinza junto à janela, TV sobre setup com monitores, armários superiores brancos, nichos e bancada com impressora 3D. A bagunça e objetos temporários não foram reproduzidos.

As medidas são estimadas; a porta e algumas distâncias não estão claramente visíveis nas fotos. Outros cômodos não foram revisados. A aparência ainda é estilizada e não fotorrealista.

Os oito identificadores interativos foram preservados; após o giro, a TV do quarto mudou de posição e orientação. As imagens de dia, noite e as oito camadas em `planta-fixa/` foram regeneradas a partir do mesmo modelo. As luzes compostas são aproximações e não recalculam fisicamente todas as sombras.

Para testar, faça backup dos arquivos existentes no Home Assistant, copie `apartamento.obj`, `apartamento.mtl` e as texturas necessárias para `/config/www/planta3d/`, e as dez imagens atualizadas para `/config/www/planta3d/planta-fixa/`. Use os YAMLs atualizados ou ajuste a direção da luz e o ponto de controle da TV do quarto conforme REVISAO-GIRO-QUARTO.md. Recarregue o navegador ignorando o cache e teste os cliques, luzes e TVs. O arquivo `.blend` é a fonte editável e não precisa ser copiado ao Home Assistant.

Não houve acesso ao Home Assistant: teste navegação, estados e aparência no computador e no celular antes de adotar esta versão.
