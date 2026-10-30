# Sistema de Hospedagem

## 1. Sobre o projeto

O Sistema de Hospedagem é uma aplicação desenvolvida em Python com interface gráfica utilizando Tkinter. O sistema permite cadastrar hóspedes, criar reservas, calcular valores de hospedagem e consultar relatórios.

O projeto utiliza o Supabase como banco de dados principal e o Redis como mecanismo de cache, buscando melhorar o desempenho das consultas.

## 2. Tecnologias utilizadas

- **Python:** linguagem utilizada no desenvolvimento.
- **Tkinter:** criação da interface gráfica.
- **Supabase:** banco de dados na nuvem.
- **Redis:** armazenamento temporário de dados (cache).
- **Memurai:** servidor compatível com Redis para execução no Windows.

## 3. Funcionalidades

- Cadastro de hóspedes.
- Criação de reservas.
- Cálculo do valor total da hospedagem.
- Consulta de reservas por meio de relatório.
- Integração com funções e Views do Supabase.
- Utilização do Redis para armazenar temporariamente os resultados das consultas.
- Exibição do banco utilizado e do tempo de consulta.

## 4. Estrutura do banco de dados

O sistema utiliza duas tabelas principais:

### Tabela hospede

Armazena as informações dos hóspedes.

- id
- nome
- email
- telefone

### Tabela reserva

Armazena as informações das reservas.

- id
- id_hospede
- check_in
- check_out
- valor_diaria
- status

A tabela reserva possui relacionamento com a tabela hospede por meio da chave estrangeira id_hospede.

O projeto também utiliza:

- **View vw_reservas:** reúne informações dos hóspedes e suas reservas.
- **Function criar_reserva:** realiza o cadastro de uma reserva.
- **Function calcular_valor_reserva:** calcula o valor da hospedagem.

## 5. Instalação das dependências

É necessário ter Python instalado no computador.

No terminal do VS Code, execute:

```bash
pip install supabase redis
```

## 6. Configuração do Supabase

1. Acesse o painel do Supabase.
2. Abra o projeto utilizado pela aplicação.
3. Acesse Project Settings e depois API Keys.
4. Copie a URL do projeto e a chave publishable.
5. Insira as informações no código Python.

Exemplo:

```python
SUPABASE_URL = "SUA_URL_DO_PROJETO"
SUPABASE_KEY = "SUA_CHAVE_PUBLISHABLE"
```

A chave deve pertencer ao mesmo projeto informado na URL.

## 7. Instalação e configuração do Redis

Para executar o Redis no Windows, o projeto utiliza o Memurai, uma implementação compatível com o protocolo Redis.

1. Acesse https://www.memurai.com/get-memurai.
2. Baixe e instale a versão para desenvolvimento.
3. Abra os serviços do Windows utilizando `services.msc`.
4. Localize o serviço Memurai e inicie-o.

Depois, configure a conexão no Python:

```python
REDIS_URL = "redis://localhost:6379/0"
```

O sistema verifica a conexão utilizando o comando `ping()`.

## 8. Como o Redis funciona no projeto

O Redis é utilizado para armazenar temporariamente os dados do relatório de reservas.

O funcionamento acontece em três etapas:

1. Quando o usuário abre o relatório, o sistema verifica se os dados estão armazenados no Redis.
2. Se os dados estiverem disponíveis, são recuperados diretamente do cache.
3. Se não estiverem disponíveis, o
