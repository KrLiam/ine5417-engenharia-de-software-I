
# Diagramas de Sequência

## Initialize
- Modelar a inicialização do DogActor não estando no construtor de GamePlayerInterface, mas sim em uma função (initialize)
que pode ser chamada várias vezes devido a erros de conexão.
- Modelar mount_init_screen
- Modelar mount_error_screen
- Modelar mount_start_screen

## Select Cell
- Meio torto na parte do Cell.selected. Olhar código.

## Select Destination
- get_selected_cell na verdade é get_selected_cell_pos

## Place Ring
- Mover logica pra GameMatch, exceto a parte da interface

## Move Cell Content
- Mover logica pra GameMatch, exceto a parte da interface