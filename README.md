# RedisMySQLPythonWorker

Apresentação 02/05/2016:
  - Descrição do processo migração (aplicação, consulta sql importação...), dificuldades encontradas.
  - Apresentação da base migrada.
  - A base migrada deverá possibilitar consultas:

    - Consultar o nome do usuário e retornar os pedidos deste usuário.
    - Consultar o estado e retornar os usuários deste estado.
    - Consultar o produto e retornar os dados dos produtos.
    - Consultar pelo pedido e retornar os dados do pedido.
    - Consultar o usuário e retornar os dados do usuário.
    - Consultar cidade e retornar usuários desta cidade.
    - Consultar o estado e retornar os dados de todos os logradouros deste estado.
    - Cadastrar um novo usuário.
    - Inserir um pedido para determinado usuário.


# Necessário para funcionar:

```
pip install redis
```

```
pip install oursql
```

No login, adicionar suas próprias informações, por padrão o mysql e o redis utilizam localhost, root para o administrador, e em seguida a base que você deseja acessar
```
Quando chamar a função, passar o cursor do mysql e do redis.
```
