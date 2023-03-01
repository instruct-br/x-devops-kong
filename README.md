### Demonstração Kong Gateway

Abaixo seguem os comandos para subir e testar algumas funcionalidades do Kong Gateway.

### Subindo aplicação

Subindo 3 APIs para teste =>
```
  $ docker-compose up -d
```

Subindo o Kong Gateway=>
```
  $ cd kong/compose/
  $ KONG_DATABASE=postgres docker compose --profile database up
```

### Serviços e Rotas

Adicionando um serviço da api teste ao kong:
```
  $ curl -i -s -X POST http://localhost:8001/services   --data name=service-test-1   --data url='http://service_test1:8081'
```
Obs: O host da url deve ser o nome do serviço (consultar o docker-compose.yml).

Adicionando a rota para acessar o serviço a partir do gateway:
```
  $ curl -i -X POST http://localhost:8001/services/service-test-1/routes   --data 'paths[]=/service1'    --data name=route_test1
```
Agora ao acessar http://localhost:8000/service1/ você obterá a mesma resposta da api que está rodando localhost:8081

obs: Repetir os passos para os outros serviços, service_test2 e service_test3.

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

obs: Também é possível utilizar o plugin apenas em serviços e rotas específicas.

### Key Authentication

Key Authentication plugin é usado para gerar e associar uma chave de API a um `consumer` (cliente). Essa chave é o segredo de autenticação apresentado pelo cliente ao fazer requisições.

Adicionando um consumer =>
```
$ curl -i -X POST http://localhost:8001/consumers/ \
    --data username=consumer-teste
```

Adicionando uma chave gerada aleatoriamente ao consumer criado =>
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

obs: Também é possível utilizar o plugin apenas em serviços e rotas específicas.

### Proxy Caching

O Proxy Cache Plugin acelera o desempenho armazenando em cache as respostas com base em códigos de resposta configuráveis, tipos de conteúdo (`content-types`) e métodos (`methods`) de solicitação.

Habilitando o plugin globalmente (qualquer rota poderá ter a resposta da requisição cacheada) =>
```
$ curl -i -X POST http://localhost:8001/plugins \
  --data "name=proxy-cache" \
  --data "config.request_method=GET" \
  --data "config.response_code=200" \
  --data "config.content_type=application/json" \
  --data "config.cache_ttl=30" \
  --data "config.strategy=memory"
```

Qualquer requisição `GET` que resulte em status 200 e que possua content-type igual a `application/json`
será armazenada em cache juntamente com o conteúdo da resposta. O campo `cache_ttl` indica em segundos
o tempo de expiração do cache. Ou seja, após 30 segundos a próxima requisição irá buscar novos dados nos
serviços.

Ao fazer a primeira requisição ao serviço 1, buscando X-cache headers =>
```
$ curl -i -s -XGET http://localhost:8000/service1/ | grep X-Cache
```

Terá esse retorno =>
```
X-Cache-Key: c9e1d4c8e5fd8209a5969eb3b0e85bc6
X-Cache-Status: Miss
```

Dentro de 30 segundos repita o mesmo comando e obterá a resposta =>
```
X-Cache-Key: c9e1d4c8e5fd8209a5969eb3b0e85bc6
X-Cache-Status: Hit
```

O status é alterado de `Miss` para `Hit`, indicando que os dados foram encontrados em cache.

obs: Também é possível utilizar o plugin apenas em serviços e rotas específicas.

### Load Balancing

Load balancing é um método de distribuição de tráfego de solicitação de API em vários serviços upstream. O Load balancing melhora a capacidade de resposta geral do sistema e reduz as falhas, evitando a sobrecarga de recursos individuais.

Primeiro passo será criar um `upstream` que representa um `virtual hostname` =>
```
$ curl -X POST http://localhost:8001/upstreams \
  --data name=localhost_upstream
```

Segundo passo será criar os `targets` que serão apontados para cada serviço teste. Esses `targets` são associados ao upstream criado =>
```
$ curl -X POST http://localhost:8001/upstreams/localhost_upstream/targets \
  --data target='service_test1:8081'

$ curl -X POST http://localhost:8001/upstreams/localhost_upstream/targets \
  --data target='service_test2:8082'

$ curl -X POST http://localhost:8001/upstreams/localhost_upstream/targets \
  --data target='service_test3:8083'
```

Terceiro passo será criar um novo serviço e uma nova rota que apontará para o mesmo. Lembre-se que o
serviço deve conter o nome do `upstream` em seu `host`, e a porta deve ser 8000 (onde o Kong Gateway está rodando) =>
```
$ curl -i -s -X POST http://localhost:8001/services   --data name=all-services   --data url='http://localhost_upstream:8000'

$ curl -i -X POST http://localhost:8001/services/all-services/routes   --data 'paths[]=/all-services'    --data name=route_all-services
```

Agora, ao acessar o endereço http://localhost:8000/all-services diversas vezes, o Kong irá alterar o tráfego das requisições para os 3 serviços que foram apontados em cada `target` no `upstream`.
