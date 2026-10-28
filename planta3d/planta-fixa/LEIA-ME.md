# Planta fixa do apartamento

Esta é uma segunda visualização: o `floor3d-card` continua podendo ser usado na aba 3D. A planta fixa usa uma imagem-base de dia ou de noite, selecionada pelo estado de `sun.sun`, e camadas independentes para mostrar as luzes e TVs. Como as camadas são imagens estáticas, a combinação de reflexos é uma aproximação visual; não calcula iluminação física em tempo real.

## Instalação

1. Instale o **config-template-card** pelo HACS e verifique que o recurso está carregado no dashboard. A fonte é https://github.com/iantrich/config-template-card. O cartão `picture-elements` e o cartão de clima são nativos do Home Assistant.
2. Copie **toda esta pasta** para `/config/www/planta3d/planta-fixa/` no Home Assistant, preservando os nomes. Em Docker, `/config` é o volume montado no contêiner. Assim, os arquivos ficam disponíveis no navegador em `/local/planta3d/planta-fixa/`.
3. Confira, em **Ferramentas de desenvolvedor → Estados**, se existem `sun.sun`, `weather.forecast_home`, as cinco luzes, as duas TVs e `input_boolean.luz_virtual_quarto_1`. O ID da previsão do tempo pode ser outro na sua instalação: nesse caso, altere `weather.forecast_home` no YAML.
4. Caso não exista, crie em **Configurações → Dispositivos e serviços → Auxiliares → Criar auxiliar → Alternar** um auxiliar com o ID `input_boolean.luz_virtual_quarto_1`. Ele não aciona dispositivo físico e é compartilhado com a visualização 3D.
5. Em uma nova aba de testes, adicione um **cartão manual** e cole o conteúdo completo de `cartao-planta-fixa.yaml`. Salve, recarregue a página e teste no computador e no celular. Esta operação não altera seu dashboard existente automaticamente.

## Como funciona

- `sun.sun` em `above_horizon` seleciona `dia.png`; outros estados selecionam `noite.png`. Quando `sun.sun` estiver ausente ou indisponível, a visualização usa a imagem noturna como padrão até que a entidade volte a funcionar.
- Os oito ícones usam as entidades reais fornecidas; toque alterna e toque prolongado abre os detalhes. O estado da luz virtual é compartilhado nas duas plantas. As TVs reconhecem `on`, `playing`, `paused`, `idle` e `buffering` como ligadas para exibir suas camadas. Seus ícones executam `toggle` nas entidades reais.
- No quarto, brilho e `hs_color` da entidade `light.luz_do_quarto`, quando disponíveis, alteram a intensidade e a tonalidade da camada. A cor resultante é uma aproximação CSS e pode divergir de uma lâmpada real; com atributos ausentes, usa-se a cor e a intensidade padrão da camada.
- Os ícones são posicionados por `top`/`left` em percentuais dentro da imagem. Ajuste essas posições na seção `Controle` do YAML se apontarem para o lugar errado. Elas devem ser conferidas com o enquadramento final e em diferentes tamanhos de tela.
- Se uma entidade estiver indisponível, sua camada não é mostrada; consulte o estado no próprio Home Assistant. A representação não deve ser interpretada como confirmação de que o aparelho físico esteja desligado.
- Esta versão envolve o cartão inteiro com `config-template-card`, que recria o cartão interno quando uma das entidades observadas muda. O próprio projeto recomenda usá-lo dentro dos elementos de uma planta; nesta implementação o encaixe completo facilita trocar a base de dia/noite, mas pode produzir piscar, uso extra de recursos ou recarregamentos frequentes (inclusive pelas atualizações de `sun.sun`). Teste o comportamento no seu celular e computador.

## Verificação

Abra no navegador do Home Assistant `/local/planta3d/planta-fixa/dia.png` e `/local/planta3d/planta-fixa/noite.png`: se algum retornar 404, confira a pasta de cópia. O mesmo vale para as oito imagens de luz/TV nomeadas no YAML. Se o painel indicar `Custom element doesn't exist`, confira a instalação e os recursos do `config-template-card`. Se uma cor não acompanhar a luz do quarto, verifique se a entidade expõe `brightness` e `hs_color` em Ferramentas de desenvolvedor → Estados. Teste as TVs ligando-as e desligando-as no painel e também por outros controles.

As medidas e a posição dos móveis são estimadas; a aparência e o comportamento precisam ser conferidos no seu Home Assistant. O arquivo não configura a visualização 3D e não inclui capturas de imagem reais das TVs.
