# Planta fixa com fundo transparente

As dez imagens RGBA desta pasta têm o mesmo enquadramento de 1000 x 1000 da versão de `planta-fixa`: duas bases e oito camadas. Após o giro do quarto, o botão da TV do quarto deve usar `left: 62.66%` e `top: 50.81%`; use o YAML atualizado desta pasta. Os outros sete botões permanecem nas mesmas posições. As imagens foram geradas do modelo mais recente da branch `quarto-fotos`; se a instalação atual usar um modelo anterior, a aparência da casa mudará.

## Aplicação em uma pasta nova

1. Extraia `imagens-transparentes.zip` para `/config/www/planta3d/planta-fixa-transparente/` no Home Assistant. A pasta deve conter diretamente os dez PNG, sem uma subpasta extra.
2. Faça uma cópia do YAML atual. No cartão da planta fixa, substitua todas as 10 ocorrências de `/local/planta3d/planta-fixa/` por `/local/planta3d/planta-fixa-transparente/`. Atualize o ponto da TV do quarto conforme indicado acima, e mantenha `opacity`, as entidades e `mix-blend-mode: screen` existentes.
3. Salve e recarregue sem cache. Se o tema ainda desenhar uma cor ou desfoque por trás da casa, e você já tiver o **card-mod** instalado, adicione o trecho abaixo dentro de `card:`, no mesmo nível de `type: picture-elements` e `image:`. Mantenha o restante do cartão atual.

```yaml
card:
  type: picture-elements
  card_mod:
    style: |
      ha-card {
        background: transparent !important;
        border: none;
        box-shadow: none;
        backdrop-filter: none;
      }
  image: ...
  elements: ...
```

As reticências representam o código que você já tem; não são valores para colar. Caso `card-mod` não esteja instalado, use um tema que deixe o fundo do cartão transparente ou instale e configure o recurso conforme a documentação do projeto. O fundo do cartão é independente da transparência dos PNG.

Teste dia e noite, cada luz, ambas TVs e o visual no celular. Se alguma camada fizer um retângulo ou o fundo permanecer colorido, confira a pasta, o cache, o suporte a `mix-blend-mode: screen` do navegador e a configuração do tema/card-mod. As camadas usam máscara conservadora nas bordas para reduzir halos; a iluminação é aproximada.

Não houve acesso ou alterações ao Home Assistant. As imagens foram conferidas sobre fundos claros, escuros e coloridos em simulação, mas precisam de teste na instalação real. Não altere a configuração nem imagens da planta 3D navegável para usar esta opção.
