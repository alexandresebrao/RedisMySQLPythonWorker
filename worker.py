#encoding:utf-8

import oursql
import redis
import datetime
import getpass

from question1 import question1_function
from question2 import question2_function
from question3 import question3_function
from question4 import question4_function
from question5 import question5_function
from question6 import question6_function
from question7 import question7_function
from question8 import question8_function
from question9 import question9_function

#Ao início do programa, o programa espera as informacoes da base no modelo host, user, senha e db do MYSQL,
#Caso algum dado seja digitado incorretamente, avisa o erro e tenta de novo.
#O programa então tenta conexão com o redis, caso consiga, prossegue, senão acusa o erro!

while True:
	my_SQL_host = raw_input ("Host MySQL (default: localhost): ")
	my_SQL_user = raw_input ("User MySQL: ")
	my_SQL_senha = getpass.getpass ("Password MySQL: ")
	my_SQL_db = raw_input ("Database MySQL: ")

	try:
		db_mysql = oursql.connect(host = my_SQL_host, user=my_SQL_user, passwd=my_SQL_senha, db=my_SQL_db)
		print(chr(27) + "[2J")
		print ("\n-----")
		print ("Conexão realizada com sucesso!")
		print ("-----\n")
		break
	except:
		print ("\n-----")
		print ("Dados incorretos - Por favor tente novamente")
		print ("-----\n")
		True

r = redis.StrictRedis(host='localhost', port=6379, db=0)
try:
    r.ping()
except:
    print "Não foi possivel conectar ao Redis"

#### POPULA O BANCO REDIS COM DADOS DO MYSQL!
#### Para performace time iremos coletar o inicio e final da execução
date_start = datetime.datetime.now()

## ------------- START DA QUESTÃO 1 ------------- ##

#Seleciona tudo do cad_usuário, isso vai ser usado para a questão 1 e 6
cursor = db_mysql.cursor(oursql.DictCursor)
cursor.execute("""SELECT * FROM cad_usuario""")
dados = cursor.fetchall()
lista_cpf = []

#Cria o hash no formato (cpf:"cpf_do_usuário")
for cliente in dados:
	string = "cpf:%s" %cliente['cpf']
	r.hmset(string,cliente)
	lista_cpf.append(cliente['cpf'])

#Guarda o pool de CPF
r.set('cpf',','.join(lista_cpf))
cpfs = r.get('cpf').split(',')

for cpf in cpfs:
	cursor.execute("SELECT cod_pedido FROM pedidos WHERE cad_usuario_cpf = %s" %(cpf))
	dados = cursor.fetchall()
	lista_pedido = []
	if len(dados) > 0:
		for dado in dados:
			lista_pedido.append(str(dado['cod_pedido']))
		r.set('cpf:'+cpf+':pedidos',','.join(lista_pedido))
	else:
		r.set('cpf:'+cpf+':pedidos','')

## ------------- FIM DA QUESTÃO 1 ------------- ##
## ------------- START DA QUESTÃO 2 ------------- ##

##POPULA ESTADO
#Executa o query para trazer como resultado o cpf da pessoa
#e o estado referente à pessoa;

cursor.execute("""
SELECT cad.cpf, uf.cd_uf as idUF
FROM cad_usuario cad
INNER JOIN logradouro log ON(cad.log_cd_logradouro=log.cd_logradouro)
INNER JOIN bairros b ON(log.bairros_cd_bairro=b.cd_bairro)
INNER JOIN cidades cid ON(b.cidade_cd_cidade=cid.cd_cidade)
INNER JOIN uf ON(cid.uf_cd_uf=uf.cd_uf);
""")

dados = cursor.fetchall()

#Pegamos os estados mas precisamos apagar dados antigos
chaves = r.keys('estado*')
for chave in chaves:
	r.delete(chave)
estados = []

#se existir dois no mesmo estado não duplica
for dado in dados:
	if (r.get('estado:'+str(dado['idUF']))):
		r.set('estado:'+str(dado['idUF']),r.get('estado:'+str(dado['idUF']))+','+str(dado['cpf']))
	else:
		r.set('estado:'+str(dado['idUF']),str(dado['cpf']))
		estados.append(str(dado['idUF']))
r.set('estado',','.join(estados))

## ------------- FIM DA QUESTÃO 2 ------------- ##
## ------------- START DA QUESTÃO 3 ------------- ##

cursor.execute("SELECT * FROM produto")
dados = cursor.fetchall()
produtos = []
for dado in dados:
	string = "produto:%s" %dado['cod_produto']
	r.hmset(string,dado)
	produtos.append (str(dado['cod_produto']))
r.set('produtos',','.join(produtos))

## ------------- FIM DA QUESTÃO 3 ------------- ##
## ------------- START DA QUESTÃO 4 ------------- ##

cursor.execute("SELECT * FROM pedidos")
dados = cursor.fetchall()
pedidos = []
for dado in dados:
	string = "pedido:%s" %dado['cod_pedido']
	r.hmset(string,dado)
	pedidos.append(str(dado['cod_pedido']))
r.set('pedidos',','.join(pedidos))


for pedido in pedidos:
	cursor.execute("SELECT * FROM itemped WHERE ped_codpedidos = %s" %(str(pedido)))
	dados = cursor.fetchall()
	itempedido = []
	for valor in dados:
		chave = "pedido:%s:item:%s" %(pedido,str(valor['cod_itemp']))
		r.hmset(chave,valor)
		itempedido.append(str(valor['cod_itemp']))
	r.set('pedido:'+str(pedido)+':items',','.join(itempedido))


## ------------- FIM DA QUESTÃO 4 ------------- ##
## ------------- START DA QUESTÃO 5 ------------- ##

# --- Já implementado pela questão 01 -- 

## ------------- FIM DA QUESTÃO 5 ------------- ##
## ------------- START DA QUESTÃO 6 ------------- ##

#Consultar as cidades e retornar os usuarios
cursor.execute("""
SELECT cad.cpf, cid.cd_cidade, cid.ds_cidade_nome
FROM cad_usuario cad
INNER JOIN logradouro log ON(cad.log_cd_logradouro=log.cd_logradouro)
INNER JOIN bairros b ON(log.bairros_cd_bairro=b.cd_bairro)
INNER JOIN cidades cid ON(b.cidade_cd_cidade=cid.cd_cidade)
""")

dados = cursor.fetchall()
cidades = r.keys('cidade*')
for cidade in cidades:
	r.delete(cidade)

logradouro = []
cidades = []
nomes_cidades = []
for dado in dados:
	if (r.get('cidade:'+str(dado['cd_cidade'])+':cpfs')):
		string = str(r.get('cidade:'+str(dado['cd_cidade']+':cpfs')))+str(dado['cpf'])
		r.set('cidade:'+str(dado['cd_cidade']+':cpfs',string))
	else:
		cidades.append(str(dado['cd_cidade']))
		nomes_cidades.append(str(dado['ds_cidade_nome'].encode('utf-8')))
		r.set('cidade:'+str(dado['cd_cidade'])+':cpfs',str(dado['cpf']))

r.set('cidades',','.join(cidades))

for i in range(len(nomes_cidades)):
	codigo = 'cidade:%s' %cidades[i]
	r.set(codigo,nomes_cidades[i])

## ------------- FIM DA QUESTÃO 6 ------------- ##
## ------------- START DA QUESTÃO 7 ------------- ##

#cursor.execute("""SELECT est.ds_uf_sigla FROM uf est""")

#dados = cursor.fetchall()
#total_estados = []

#sub_date_start = datetime.datetime.now()

#for dado in dados:
	#total_estados.append (str(dado['ds_uf_sigla']))
#r.set('total_estados',','.join(produtos))

#porcentagem = 0

#for var in total_estados:
	#cursor.execute(""" SELECT * FROM logradouro lo 
	#INNER JOIN bairros ba ON(lo.bairros_cd_bairro = ba.cd_bairro)
	#INNER JOIN cidades ci ON (ba.cidade_cd_cidade = ci.cd_cidade)
	#INNER JOIN uf ON (ci.uf_cd_uf = cd_uf)
	#WHERE ds_uf_sigla = "%s" """ %var)
	#dados2 = cursor.fetchall()
	#cd_logradouro_pool = []
	#porcentagem += 3.70
	#print "%s%% - Populando: %s - %s segundos" %(str(porcentagem), str(var), str())
	#for dado2 in dados2:
		#string = 'estado:%s:logradouro:%s' %(var, str(dado2['cd_logradouro']))
		#r.hmset(string,dado2)
		#cd_logradouro_pool.append(str(dado2['cd_logradouro']))
		#string2 = 'cd_logradouro_pool:%s' %(var)
		#r.set (string2,','.join(cd_logradouro_pool))

## ------------- FIM DA QUESTÃO 7 ------------- ##
### ----- TERMINA A POPULACÃO DOS DADOS ----- ###

date_finish = datetime.datetime.now()
print ("Tempo para povoar o redis: %s" %(date_finish - date_start))

### ----- COMEÇA A INTERFACE COM O USER ----- ###

menu = True
while menu:
	
	menu_choice = str(raw_input ("\n----- \nCarregar o menu? (S - Voltar ao Menu / N - Sair do Programa): "))	
	if menu_choice == "s" or menu_choice == "S":
		menu = True
	else:
		menu = False
		break
		
	print(chr(27) + "[2J")
	print ("Selecione a questão: \n")
	print ("-----")
	print ("1) Consultar o nome do usuário e retornar os pedidos deste usuário!") #FEITO (BANCO,EXECUÇÃO)
	print ("2) Consultar o estado e retornar os usuários deste estado!") #FEITO (BANCO,EXECUÇÃO)
	print ("3) Consultar o produto e retornar os dados dos produtos!") #FEITO (BANCO, EXECUÇÃO)
	print ("4) Consultar pelo pedido e retornar os dados do pedido!") #FEITO (BANCO, EXECUÇÃO)
	print ("5) Consultar o usuário e retornar os dados do usuário!") # FEITO (BANCO, EXECUÇÃO)
	print ("6) Consultar a cidade e retornar os dados do usuário!") # FEITO (BANCO, EXECUÇÃO)
	print ("7) Consultar o estado e retornar os dados de todos os logradouros deste estado!")
	print ("8) Cadastrar um novo usuário!") #FEITO (BANCO, EXECUÇÃO)
	print ("9) Inserir um pedido para determinado usuário!")
	print ("0) Sair")
	print ("-----")
	escolha = input ("\nDigite a questão: ")

	if escolha == 1:
		question1_function (r, cursor)

	elif escolha == 2:
		question2_function (r, cursor)

	elif escolha == 3:
		question3_function (r, cursor)

	elif escolha == 4:
		question4_function (r, cursor)

	elif escolha == 5:
		question5_function (r, cursor)

	elif escolha == 6:
		question6_function (r)

	elif escolha == 7:
		question7_function (r, cursor)

	elif escolha == 8:
		question8_function(r,cursor)

	elif escolha == 9:
		question9_function(r, cursor)
		
	elif escolha == 0:
		menu = False
