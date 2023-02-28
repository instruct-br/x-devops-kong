### Subindo aplicação

Subindo a api teste =>
```
  $ docker-compose up --build service_test1
```

Subindo o kong =>
```
  $ cd kong/compose/
  $ KONG_DATABASE=postgres docker compose --profile database up
```

### Serviços e Rotas

Adicionando o serviço da api teste ao kong:
```
  $ curl -i -s -X POST http://localhost:8001/services   --data name=service_test1   --data url='http://(endereco_rede_da_sua_maquina):8082'
```
Obs: Para encontrar um endereço, use o comando: hostname -I e escolha uma das opções

Adicionando a rota para acessar o serviço a partir do gateway:
```
  $ curl -i -X POST http://localhost:8001/services/service_test1/routes   --data 'paths[]=/service1'    --data name=route_test1
```
Agora ao acessar http://localhost:8000/service1/ você obterá a mesma resposta da api que está rodando localhost:8082

### Rate Limiting

Rate Limiting Plugin é usado para controlar a taxa de requisições enviadas para um serviço.

Habilitando o plugin globalmente (qualquer requisição será limitada a 5 tentativas por minuto) =>
```
$ curl -i -X POST http://localhost:8001/plugins \
    --data name=rate-limiting \
    --data config.minute=5 \
    --data config.policy=local

```

Para testar, acesse http://localhost:8000/service1/ 6 vezes dentro de 1 minuto. A última resposta será:
```
{
  "message": "API rate limit exceeded"
}
```

obs: É possível utilizar o plugin apenas em serviços/rotas específicas.

### Key Authentication

Key Authentication plugin é usado para gerar e associar uma chave de API a um `consumer`. Essa chave é o segredo de autenticação apresentado pelo cliente ao fazer requisições.

Adicionando um consumer =>
```
$ curl -i -X POST http://localhost:8001/consumers/ \
    --data username=consumer-teste
```

Adicionando uma chave gerada aleatóriamente ao consumer criado =>
```
$ curl -i -X POST http://localhost:8001/consumers/consumer-teste/key-auth
```

Habilitando o plugin globalmente (qualquer requisição será protegida por autenticação chave) =>
```
$ curl -X POST http://localhost:8001/plugins/ \
    --data "name=key-auth"  \
    --data "config.key_names=apikey"
```
Ao tentar acessar o serviço http://localhost:8000/service1/ sem a chave, será retornado a resposta:
```
HTTP/1.1 401 Unauthorized
...
{
  "message": "No API key found in request"
}
```

Ao tentar acessar o serviço http://localhost:8000/service1/ com a chave errada, será retornado a resposta:
```
HTTP/1.1 401 Unauthorized
...
{
  "message":"Invalid authentication credentials"
}
```

obs: É possível utilizar o plugin apenas em serviços/rotas específicas.

### Proxy Caching
### Load Balancing
