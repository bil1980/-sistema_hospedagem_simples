# Sistema de Hospedagem

Projeto avaliativo de Banco de Dados.

## Tecnologias

- Python
- Tkinter
- PostgreSQL
- psycopg2

## Recursos de Banco de Dados

### View
`vw_reservas`

Utilizada na tela "Relatório de Reservas" para apresentar os dados das reservas junto com o nome do hóspede.

### Function
`calcular_valor_reserva`

Recebe a quantidade de dias e o valor da diária e retorna o valor total da hospedagem.

### Procedure
`criar_reserva`

Recebe os dados da reserva, valida o hóspede e as datas e insere uma nova reserva com status ATIVA.
