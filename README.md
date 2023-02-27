Subindo a api teste =>

  $ docker-compose up --build service_test1

Subindo o kong =>

  $ cd kong/compose/
  $ KONG_DATABASE=postgres docker compose --profile database up

Adicionando o serviço da api teste ao kong:

  $ curl -i -s -X POST http://localhost:8001/services   --data name=service_test1   --data url='http://(endereco_rede_da_sua_maquina):8082'

Obs: Para encontrar um endereço, use o comando: hostname -I e escolha uma das opções

Adicionando a rota para acessar o serviço a partir do gateway:

  $ curl -i -X POST http://localhost:8001/services/service_test1/routes   --data 'paths[]=/service1'   --data name=route_test1

Agora ao acessar http://localhost:8000/service1/ você obterá a mesma resposta da api que está rodando localhost:8082