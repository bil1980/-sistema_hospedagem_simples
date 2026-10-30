Sistema de Hospedagem

1. Sobre o projeto

Sistema desenvolvido em Python com Tkinter, integrado ao Supabase e Redis, para gerenciamento de hóspedes e reservas.

2. Tecnologias utilizadas

Python e Tkinter: desenvolvimento da aplicação e interface gráfica.

Supabase: armazenamento dos dados.

Redis: armazenamento temporário (cache).

Memurai: execução do Redis no Windows.

python-dotenv: gerenciamento das variáveis de ambiente.

3. Configuração do .env

O arquivo .env armazena as credenciais necessárias para conectar o sistema ao Supabase e ao Redis.

Crie um arquivo chamado .env na pasta principal do projeto e adicione:

SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
REDIS_URL=redis://localhost:6379/0

Substitua os valores pelas suas credenciais.

O arquivo .env não deve ser compartilhado, pois contém informações privadas. Para facilitar a configuração, o projeto pode incluir um .env.example sem credenciais reais.

4. Utilização do Redis e Memurai

Foi utilizado o Memurai para executar o Redis no Windows.

O Redis é responsável pelo cache do relatório de reservas. Quando o relatório é consultado, o sistema verifica primeiro se os dados estão armazenados no Redis.

Se estiverem, são recuperados diretamente do cache.

Caso contrário, são consultados no Supabase e armazenados no Redis por 50 segundos.

Quando um hóspede é cadastrado ou uma reserva é criada, o cache é removido para garantir que as próximas consultas utilizem informações atualizadas.

O Redis contribui para reduzir consultas repetidas ao Supabase e melhorar o tempo de resposta do relatório.

5. Instalação e execução

Instale as dependências:

pip install -r requirements.txt

Configure o .env, inicie o serviço do Memurai e execute:

python main.py

6. Funcionalidades

Cadastro de hóspedes.

Criação de reservas.

Cálculo do valor da hospedagem.

Relatório de reservas com utilização de cache.

Observação: o Supabase armazena os dados permanentemente, enquanto o Redis mantém temporariamente os resultados das consultas para melhorar o desempenho do sistema.
