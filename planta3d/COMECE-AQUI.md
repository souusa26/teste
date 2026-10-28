# Plantas do apartamento para Home Assistant

O projeto contém duas opções, que podem ser colocadas em abas separadas:

1. [Planta fixa em perspectiva](planta-fixa/LEIA-ME.md): imagens de dia e noite, iluminação por ambiente, telas decorativas das TVs, ícones e clima. Depende do recurso HACS `config-template-card`.
2. [Planta 3D navegável](planta-navegavel/LEIA-ME.md): cartão `floor3d-card` com configurações diurna e noturna, controladas por `sun.sun`.

Leia os guias antes de copiar os arquivos e confirme os IDs das entidades. Os cartões não foram executados na sua instalação e precisam de testes no Home Assistant, inclusive de toque e desempenho no celular.

A planta fixa e a iluminação por camadas são aproximações visuais: múltiplas luzes não recalculam todos os reflexos e sombras de forma física. O modelo existente continua estilizado, com dimensões e alguns móveis aproximados.

As telas decorativas são exibidas na planta fixa; a troca de textura das telas na planta 3D ainda não está implementada. A iluminação projetada das TVs permanece no cartão 3D.
