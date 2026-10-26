# Instalação da planta no Home Assistant

Este é um projeto inicial para testar a geometria e as interações. As dimensões são aproximadas e a compatibilidade com a versão instalada do seu `floor3d-card` precisa ser testada. A planta não altera o dashboard existente; a proposta é criar uma aba de teste separada.

## 1. Crie a luz virtual

1. Em **Configurações → Dispositivos e serviços → Auxiliares**, escolha **Criar auxiliar → Alternar**.
2. Dê o nome `Luz virtual quarto 1` e salve. Ela não controla nenhum equipamento físico.
3. Em **Ferramentas de desenvolvedor → Estados**, confira que o ID é `input_boolean.luz_virtual_quarto_1`. Se for diferente, altere-o no arquivo `cartao-floor3d.yaml`.
4. Confira também os outros sete IDs do YAML. O arquivo usa os nomes que constavam na documentação anterior; valide-os na sua instalação antes de adicionar o cartão. Um ID ausente pode causar funcionamento incorreto do card.

## 2. Copie o modelo

Copie `apartamento.obj` e `apartamento.mtl` juntos para a pasta `www/planta3d` da configuração do Home Assistant, preservando os nomes. O caminho visto de dentro do Home Assistant normalmente é:

```text
/config/www/planta3d/apartamento.obj
/config/www/planta3d/apartamento.mtl
```

Crie a pasta, se necessário. Pode usar o File Editor, Samba ou outro método de acesso aos arquivos que você já utilize. Em Docker, `/config` é o diretório montado para dentro do contêiner; o caminho correspondente no computador ou servidor depende da sua instalação. Confira o volume configurado para o contêiner antes de copiar. Não suponha que ele seja `~/homeassistant`.

Os arquivos são disponibilizados pelo Home Assistant em `/local/planta3d/`. Para conferir a cópia, abra no navegador conectado ao Home Assistant `/local/planta3d/apartamento.obj` e `/local/planta3d/apartamento.mtl`, usando a mesma origem pela qual você acessa o painel. O navegador deve mostrar ou baixar os arquivos, não exibir erro 404.

## 3. Adicione o cartão

1. Confirme que o `floor3d-card` que você já tem está disponível como recurso frontend do Home Assistant. O projeto de referência é [adizanni/floor3d-card](https://github.com/adizanni/floor3d-card); forks e versões diferentes podem apresentar comportamento distinto.
2. Edite seu dashboard e crie uma **nova aba de teste**. Escolha o tipo **Painel** se disponível; ele acomoda um único cartão que ocupa a área da aba.
3. Adicione um cartão **Manual**, cole todo o conteúdo de `cartao-floor3d.yaml`, revise os IDs das entidades e salve. Não cole esse bloco substituindo o YAML inteiro do seu dashboard existente.
4. Atualize a página. Com o mouse, gire, aproxime e clique nas luminárias e nas telas. O clique chama o serviço `toggle` da entidade correspondente; o PS5 e o computador não possuem ações no cartão.

## 4. Teste os estados

- Alterne as cinco luzes existentes e confira se cada luminária representa o cômodo correto. Ligue/desligue uma luz por outro controle do Home Assistant e confira se a planta acompanha.
- Alterne a luz virtual; abra o painel em outro dispositivo e confira que o estado é compartilhado. Ela não deve alterar nada na casa.
- Acione cada TV e confira o reflexo azul ou laranja. O card transforma os estados `on`, `playing`, `paused`, `idle` e `buffering` em ligado para a iluminação, e outros estados, inclusive `off`, `standby` e `unavailable`, em apagado. Se a integração da sua TV usar outros estados de funcionamento, a lista em `entity_template` precisará ser adaptada.
- Faça os testes de navegação e toque no celular. O comportamento de toque pode variar conforme a versão do card e o navegador; a documentação do projeto menciona limitações em dispositivos móveis. Se o toque no objeto não funcionar, use temporariamente os controles nativos do Home Assistant.

O cartão tenta criar luzes 3D; as cores, brilho, sombras e distâncias dependem da versão do componente, da escala do modelo e da potência do dispositivo. O código da versão consultada usa atributos de cor da entidade quando disponíveis, podendo se sobrepor à cor fixa no YAML. Avalie o resultado na sua instalação e ajuste quando necessário. As telas permanecem com o material do modelo; o brilho é uma fonte de luz virtual, não uma imagem de vídeo da TV.

## Ajustes e diagnóstico

- **Card não aparece:** verifique se `floor3d-card` está instalado, carregado como recurso do dashboard e se não há erro no navegador.
- **Modelo não carrega:** confirme os dois arquivos em `/config/www/planta3d/`, seus nomes e os acessos `/local/` do passo 2. Após substituir um arquivo, atualize a página ignorando cache.
- **Luz não acompanha o dispositivo:** confira o ID, o estado em Ferramentas de desenvolvedor e o nome do objeto; ambos precisam existir. Para TVs, confira também a lista de estados no template.
- **Lentidão ou tela preta no celular:** no YAML, experimente mudar `shadow: 'yes'` para `shadow: 'no'` no nível principal. Isso desativa sombras em toda a cena e reduz a carga gráfica. Luzes continuarão existindo, mas poderão atravessar divisórias com mais facilidade.
- **Luz forte ou fraca:** ajuste `lumens`, `distance` e a intensidade ambiente `globalLightPower`. As distâncias deste modelo estão em metros; valores de exemplos que pressupõem centímetros precisam ser ajustados.
- **Objeto difícil de tocar:** aproxime a câmera e toque na luminária ou na tela, não na parede ou na moldura.

As opções do cartão e o tratamento de estados acima foram conferidos na [documentação](https://github.com/adizanni/floor3d-card) e no [código-fonte](https://github.com/adizanni/floor3d-card/blob/master/src/floor3d-card.ts) do projeto. O seu Home Assistant não foi acessado e a instalação não foi executada automaticamente.
