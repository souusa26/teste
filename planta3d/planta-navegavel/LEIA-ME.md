# Planta 3D navegável: dia e noite

Esta é uma configuração alternativa para testar em **uma nova aba**, mantendo seu cartão atual intacto. Ela mostra o `floor3d-card` de dia ou de noite conforme o estado da entidade `sun.sun`: `above_horizon` e `below_horizon`. A planta e os dispositivos continuam usando os arquivos e entidades existentes. O cartão diurno usa fundo `#b3b9c9` e luz ambiente `0.20`, conforme a configuração informada; o noturno usa fundo mais escuro e luz ambiente `0.08`.

1. Verifique em **Ferramentas de desenvolvedor → Estados** se `sun.sun` existe e tem um dos dois estados. A integração Sol do Home Assistant usa a localização configurada. Se a entidade estiver ausente ou indisponível, nenhuma das duas condições será exibida.
2. Confira se os arquivos OBJ, MTL e suas texturas continuam na pasta `www/planta3d` da configuração do Home Assistant, como no guia original.
3. Em uma aba de teste, adicione um cartão manual e cole o conteúdo de `cartao-dia-noite.yaml`. Confirme os IDs, principalmente o auxiliar `input_boolean.luz_virtual_quarto_1`.
4. Salve, recarregue e confirme as interações das luzes e TVs. Na troca do período, a posição e o zoom da câmera podem ser reiniciados; o cartão também pode precisar de recarga se aparecer vazio ao se tornar visível. Isso depende da versão do Home Assistant e do floor3d-card e requer teste na sua instalação.

O facho direcional das TVs e a ação de ligar/desligar são preservados. **Limitação:** este cartão não troca a textura da tela 3D para a interface Samsung/Roku; os arquivos do modelo e a integração do card ainda não fornecem essa função. Associar dois efeitos ao mesmo objeto sem adaptação pode executar dois toggles em um clique. Não foram adicionadas associações duplicadas. A tela com interface decorativa deve ser validada na planta fixa.

Se o cartão falhar ou ficar vazio, volte ao cartão anterior e verifique o console do navegador e os estados das entidades; não houve acesso à sua instalação e esta configuração ainda não foi executada no seu Home Assistant. As opções de cor e potência de ambiente podem ser ajustadas nos dois blocos do YAML.
