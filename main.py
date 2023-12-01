import pygame
import os
import sys
import csv
from random import randint
from pygame.locals import *
from sys import exit

pygame.init()

#Resolução da tela
width = 1924
height = 1080

size = width, height
screen = pygame.display.set_mode((size))

#Nome do jogo
pygame.display.set_caption ("Saving the John Lennon")

#Frames por segundo
clock = pygame.time.Clock()
FPS = 60

#Linhas e colunas
linhas = 20
colunas = 100

#TILE_SIZE
TILE_SIZE = height//linhas
TILE_TYPES = len(os.listdir(f'Matrizes/Grades'))

#Niveis
level = 1

#Gravidade
GRAVIDADE = 0.5

#Variaveis de ações do jogador
mover_esquerda = False
mover_direita = False
atirar = False

#Armazenar tiles em uma lista
lista_sprites = []
for i in range(TILE_TYPES):
	sprite = pygame.image.load(f'Matrizes/Grades/{i}.png')
	sprite = pygame.transform.scale(sprite, (TILE_SIZE, TILE_SIZE))
	lista_sprites.append(sprite)

#Cores
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (80, 80, 80)

#Definindo o Background
BG = (145, 201, 125)

def Carregar_Background():
	screen.fill(BG)

#Definindo a HUD (vulgo interface)// Temporariamente em desuso
font = pygame.font.SysFont('Futura', 50)
def Carregar_HUD(text, font, text_col, x, y):
	sprite = font.render(text, True, text_col)
	screen.blit(sprite, (x, y))

#Classe para criação de personagem
class Soldado(pygame.sprite.Sprite):
	def __init__(self, tipo_personagem, x, y, scale, velocidade, qtd_vida):
		pygame.sprite.Sprite.__init__(self)

		#Variveis exclusivas para IA's
		self.contador_passos = 0
		self.inativo = False
		self.contador_inativo = 0
		self.visao = pygame.Rect(0, 0, 450, 20)
		
		#Variavel que verifica se o personagem está "vivo"
		self.vida = True

		#Variavel da quantiade de vida
		self.qtd_vida = qtd_vida
		self.qtd_max_vida = self.qtd_vida
		
		#Tipo de personagem, importante para mudar o sprite entre inimigo a jogador
		self.tipo_personagem = tipo_personagem
		
		#Velocidade do personagem
		self.velocidade = velocidade
		
		#Variaveis para inverter a direção do sprite
		self.direcao = 1
		self.flip = False

		#Variavel para limitar a quantidade de projeteis
		self.limitador_projeteis = 0

		#Variavel para animação de pulo
		self.vetor_y = 0
		self.pular = False
		self.no_ar = True

		#Variaveis pra rodar as animações
		self.lista_animacao = []
		self.frame_index = 0
		self.action = 0
		self.atualizacao_tempo = pygame.time.get_ticks()
		
		#Selecionando o sprite do personagem dependendo da movimentação
		tipos_animacoes = ['Parado', 'Andar', 'Pular', 'Morte']
		for animacao in tipos_animacoes:
			#Redefinir lista temporária de imagens
			temp_list = []
			#Contador da quantidade de arquivos em uma pasta
			num_quadros = len(os.listdir(f'{self.tipo_personagem}/{animacao}'))
			for i in range(num_quadros):

				sprite = pygame.image.load(f'{self.tipo_personagem}/{animacao}/{i}.png').convert_alpha()
				sprite = pygame.transform.scale_by(sprite, scale)
				temp_list.append(sprite)
			self.lista_animacao.append(temp_list)
		
		self.image = self.lista_animacao[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x , y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		#Atualizar a animação
		self.Atualizacao_Animacao()
		self.Verificar_Saude()

		#Atualizar o limitador de projeteis
		if self.limitador_projeteis > 0:
			self.limitador_projeteis -= 1

		#Carregar o sprite
		self.Carregar()


	def Mover(self, mover_esquerda, mover_direita):
		#Atribuindo variáveis ​​de movimento
		dy = 0
		dx = 0

		#Animação para mover para esquerda
		if mover_esquerda:
			dx = -self.velocidade
			self.flip = True
			self.direcao = -1

		#Animação para mover para esquerda
		if mover_direita:
			dx = self.velocidade
			self.flip = False
			self.direcao = 1

		#Animação para pular
		if self.pular == True and self.no_ar == False:
			self.vetor_y = -15
			self.pular = False
			self.no_ar = True

		#Aplicando gravidade
		self.vetor_y += GRAVIDADE
		if self.vetor_y > 10: #Limita a velocidade da queda
			self.vetor_y
		dy += self.vetor_y

		#Verificador de colisão
		for tile in mapa.lista_obstaculo:
			#Para o vetor X
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
			#Para o vetor y
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#Verificando se ele está em cima ou em baixo de uma grade
				if self.vetor_y < 0:
					self.vetor_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vetor_y >= 0:
					self.no_ar = False
					self.vetor_y = 0
					dy = tile[1].top - self.rect.bottom	

		#Atualizar a posição
		self.rect.x += dx
		self.rect.y += dy


	def Atirar(self, scale):
		self.scale = scale
     
		max_limitador_projeteis = 60
     
		if self.limitador_projeteis == 0:
			self.limitador_projeteis = max_limitador_projeteis
			projetil = Projetil(self.rect.centerx, self.rect.centery, self.direcao, self.tipo_personagem, self.scale)
			grupo_projeteis.add(projetil)
		

	def Atualizacao_Animacao(self):

		#Tempo da animação
		TEMPO_RESPOSTA_ANIMACAO = 100

		#Atualizar a imagem de acordo com as taxas de quadros
		self.sprite = self.lista_animacao[self.action][self.frame_index]

		#Verificar se já passou tempo suficiente desde a última atualização
		if pygame.time.get_ticks() - self.atualizacao_tempo > TEMPO_RESPOSTA_ANIMACAO:
			self.atualizacao_tempo = pygame.time.get_ticks()
			self.frame_index += 1

		#Resetar a animação caso ela acabe
		if self.frame_index >= len(self.lista_animacao[self.action]):
			if self.action == 3:
				self.frame_index = len(self.lista_animacao[self.action]) - 1
			else:
				self.frame_index = 0


	def Atualizar_Acao(self, new_action):
		#Checar se a uma nova ação
		if new_action != self.action:
			self.action = new_action
			#Atualizando as configurações das animações
			self.frame_index = 0
			self.atualizacao_tempo = pygame.time.get_ticks()


	def Verificar_Saude(self):
		if self.qtd_vida <= 0:
			self.qtd_vida = 0
			self.velocidade = 0
			self.vida = False
			self.Atualizar_Acao(3)


	def Carregar(self):
		#Carregar o personagem
		screen.blit(pygame.transform.flip(self.sprite, self.flip, False), self.rect)

		#Para ver as hitbox
		pygame.draw.rect(screen, RED, self.rect, 1)

	def IA_Vietnamita(self):
		#Função para fazer as IA's do Vietnamitas
		#Verificador de inatividade
	
		if self.vida and jogador.vida:
			#Gerador de número aleatório
			if self.inativo == False and randint(1, 200) == 1:
				#Animação de parado
				self.Atualizar_Acao(0)#0: Parado
				self.inativo = True
				self.contador_inativo = randint(50, 120)

			#Quando o inimigo avistar o jogador, ele vai parar e atira
			if self.visao.colliderect(jogador.rect):
				self.Atualizar_Acao(0)#0: Parado
				self.Atirar(0.07)
			else:
				#Verificador de inatividade
				if self.inativo == False:
					#Verificando a direção do personagem
					if self.direcao == 1:
						IA_mover_direita = True
					else:
						IA_mover_direita = False
					IA_mover_esquerda = not IA_mover_direita
					#Função que controla a movimentação
					self.Mover(IA_mover_esquerda, IA_mover_direita)
					#Animação de andar
					self.Atualizar_Acao(1)#1: Andar

					#Contando os passos
					self.contador_passos += 1

					#Caixa de visão
					self.visao.center = (self.rect.centerx + 200 * self.direcao, self.rect.centery)

					#Detectando o limite de passos dados
					if self.contador_passos > TILE_SIZE:
						self.direcao *= -1
						self.contador_passos *= -1
				else:
						self.contador_inativo -= 1
						if self.contador_inativo <= 0:
							self.inativo = False


#Clase para a barra de recarregar a arma
class BarraRealoading():
	def __init__(self, x, y, limitador_projeteis):
		self.x = x
		self.y = y
		self.limitador_projeteis = limitador_projeteis


	def Carregar(self, limitador_projeteis):
     
		max_limitador_projeteis = 60
     
		porcentagem = limitador_projeteis / max_limitador_projeteis

		pygame.draw.rect(screen, BLACK, (self.x - 200, self.y - 100, 450, 200))
		pygame.draw.rect(screen, GRAY, (self.x - 5, self.y + 20, 230, 60))
		pygame.draw.rect(screen, YELLOW, ((self.x, self.y + 25, 220 * porcentagem, 50)))



#Classe para a criação de projetil
class Projetil(pygame.sprite.Sprite):
	def __init__(self, x , y, direcao, tipo_personagem, scale):
		pygame.sprite.Sprite.__init__(self)
		#Velocidade
		self.speed = 25

		#Variavel para inverter a direção do sprite
		self.direcao = direcao
		self.flip = False

		#Escala
		self.scale = scale

		#Variaveis pra rodar as animações
		self.lista_animacao = []
		self.frame_index = 0
		self.atualizacao_tempo = 0

		#Variavel que muda o projetil dependendo do tipo do personagem
		self.tipo_personagem = tipo_personagem
		
		#Selecionando o sprite
		num_quadros = len(os.listdir(f'{tipo_personagem}/Projetil'))
		for i in range(num_quadros):
			sprite = pygame.image.load(f'{tipo_personagem}/Projetil/{i}.png').convert_alpha()
			sprite = pygame.transform.scale_by(sprite, scale)
			self.lista_animacao.append(sprite)
		self.image = self.lista_animacao[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x + 90 * self.direcao, y + -5)


	def update(self):

		#Atualizar animação
		self.Atualizacao_Animacao()

		#Movimentação do projetil
		self.rect.x += (self.direcao * self.speed)

		#Verificar se o projetil saiu da tela
		if self.rect.right < 0 or self.rect.left > width:
			self.kill()

		#Verificar colisão entre grades
		for inimigo in grupo_inimigos:
			for tile in mapa.lista_obstaculo:
				if tile[1].colliderect(self.rect):
					self.kill()
					if self.tipo_personagem == 'Personagem_Rambo':
						explosao = Explosao(self.rect.x, self.rect.y, 1)
						grupo_explosoes.add(explosao)
						#Aplicando dano em área para os personagens
						if abs(self.rect.centerx - inimigo.rect.centerx) < TILE_SIZE * 3 and abs(self.rect.centery - inimigo.rect.centery) < TILE_SIZE * 3:
							inimigo.qtd_vida -= 30

		#Verificar colisões entre personagens e projeteis
		if pygame.sprite.spritecollide(jogador, grupo_projeteis, False):
			if jogador.vida:
				jogador.qtd_vida -= 10
				self.kill()
		for inimigo in grupo_inimigos:
			if pygame.sprite.spritecollide(inimigo, grupo_projeteis, False):
				if inimigo.vida:
					inimigo.qtd_vida -= 20
					jogador.qtd_vida += 10
					if jogador.qtd_vida > jogador.qtd_max_vida:
						jogador.qtd_vida = jogador.qtd_max_vida
					self.kill()
					explosao = Explosao(self.rect.x, self.rect.y, 1.5)
					grupo_explosoes.add(explosao)
					#Aplicando dano em área para os personagens
					if abs(self.rect.centerx - inimigo.rect.centerx) < TILE_SIZE * 3 and abs(self.rect.centery - inimigo.rect.centery) < TILE_SIZE * 3:
						inimigo.qtd_vida -= 30

		#Carregar o sprite
		self.Direcao()
		self.Carregar()


	def Atualizacao_Animacao(self):

		#Tempo da animação
		TEMPO_RESPOSTA_ANIMACAO = 1

		#Atualizar a imagem de acordo com as taxas de quadros
		self.image = self.lista_animacao[self.frame_index]
		self.atualizacao_tempo += 1

		#Verificar se já passou tempo suficiente desde a última atualização
		if self.atualizacao_tempo > TEMPO_RESPOSTA_ANIMACAO:
			self.atualizacao_tempo = 0
			self.frame_index += 1

		#Resetar a animação caso ela acabe
		if self.frame_index >= len(self.lista_animacao):
			self.frame_index = 0


	def Direcao(self):

		if self.direcao == -1:
			self.flip = True
		else:
			self.flip = False


	def Carregar(self):
		#Carregar o personagem
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
		
		#Para ver as hitbox
		#pygame.draw.rect(screen, RED, self.rect, 1)

class Explosao(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		#Variaveis pra rodar as animações
		self.lista_animacao = []
		self.frame_index = 0
		self.atualizacao_tempo = 0
		
		#Selecionando o sprite
		num_quadros = len(os.listdir(f'Objeto_Explosao/Explosao'))
		for i in range(num_quadros):
			sprite = pygame.image.load(f'Objeto_Explosao/Explosao/{i}.png').convert_alpha()
			sprite = pygame.transform.scale_by(sprite, scale)
			self.lista_animacao.append(sprite)
		self.image = self.lista_animacao[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


	def update(self):
		#Tempo da animação
		TEMPO_RESPOSTA_ANIMACAO = 4

		#Atualizar a imagem de acordo com as taxas de quadros
		self.atualizacao_tempo += 1

		#Verificar se já passou tempo suficiente desde a última atualização
		if self.atualizacao_tempo > TEMPO_RESPOSTA_ANIMACAO:
			self.atualizacao_tempo = 0
			self.frame_index += 1
			#Resetar a animação caso ela acabe
			if self.frame_index >= len(self.lista_animacao):
				self.kill()
			else:
				self.image = self.lista_animacao[self.frame_index]

		self.Carregar()


	def Carregar(self):
		screen.blit(self.image, self.rect)

		#Para ver as hitbox
		#pygame.draw.rect(screen, RED, self.rect, 1)

class Mapa():
	def __init__(self):
		self.lista_obstaculo = []

	def process_data(self, data):
		for y, linha in enumerate(data):
			for x, tile in enumerate(linha):
				if tile >= 0:
					sprite = lista_sprites[tile]
					sprite_rect = sprite.get_rect()
					sprite_rect.x = x * TILE_SIZE
					sprite_rect.y = y * TILE_SIZE
					tile_data = (sprite, sprite_rect)
					
					#Grades com colisões
					if tile >= 0 and tile <= 10:#Grades com colisões
						self.lista_obstaculo.append(tile_data)
					#Grades decorativas
					elif tile >= 11 and tile <= 25:#Grades decorativas
						decoracao = Decoracao(sprite, x *TILE_SIZE, y * TILE_SIZE)
						grupo_decoracoes.add(decoracao)
					#Fim da fase
					elif tile == 26:#Fim da fase
						saida = Saida(sprite, x *TILE_SIZE, y * TILE_SIZE)
						grupo_saidas.add(saida)
					#Criar jogador
					elif tile == 27:
						jogador = Soldado('Personagem_Rambo', x * TILE_SIZE, y * TILE_SIZE, 0.4, 15, 100)#Criar jogador
						barra_recarregar_arma = BarraRealoading(170, 60, jogador.limitador_projeteis)
					elif tile == 28:#Criar inimigo
						inimigo = Soldado('Personagem_Vietnamita', x *TILE_SIZE, y * TILE_SIZE, 0.4, 5, 50)#Criar inimigos
						grupo_inimigos.add(inimigo)

		return jogador, barra_recarregar_arma
	
	def Carregar(self):
		for tile in self.lista_obstaculo:
			screen.blit(tile[0], tile[1])

class Decoracao(pygame.sprite.Sprite):
	def __init__(self, image, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

class Saida(pygame.sprite.Sprite):
	def __init__(self, image, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

#Criando grupos
grupo_inimigos = pygame.sprite.Group()
grupo_projeteis = pygame.sprite.Group()
grupo_explosoes = pygame.sprite.Group()
grupo_decoracoes = pygame.sprite.Group()
grupo_saidas = pygame.sprite.Group()

#Criar listas de blocos vazios
world_data = []
for linha in range(linhas):
	R = [-1] * colunas
	world_data.append(R)

#Carregar os dados e criar um mundo
with open(f'Matrizes/level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, linha in enumerate(reader):
		for y, tile in enumerate(linha):
			world_data[x][y] = int(tile)

mapa = Mapa()
jogador, barra_recarregar_arma = mapa.process_data(world_data)
while True:

	#Taxas de quadros por segundo
	clock.tick(FPS)

	#Atualizando o background
	Carregar_Background()

	
	#Atualizando o mapap
	mapa.Carregar()

	#Atualizando grades
	grupo_decoracoes.update()
	grupo_saidas.update()
	grupo_decoracoes.draw(screen)
	grupo_saidas.draw(screen)


	#Atualizar projeteis
	grupo_projeteis.update()


	#Atualizar personagens
	jogador.update()
	for inimigo in grupo_inimigos:
		inimigo.IA_Vietnamita()
		inimigo.update()
  
	#Atualizar explosão
	grupo_explosoes.update()


	#Atualizando a HUD
	#HUD da arma recarregando
	barra_recarregar_arma.Carregar(jogador.limitador_projeteis)
	#HUD da vida
	Carregar_HUD(f'VIDAS: {jogador.qtd_vida}/{jogador.qtd_max_vida}', font, WHITE, 150, 20)


	#Se o protagonista está vivo
	if jogador.vida:
		#Atirando projetis
		if atirar:
			jogador.Atirar(0.2)
		#Controlando quando ativa qual animação
		if jogador.no_ar:
			jogador.Atualizar_Acao(2)#2: Animação de pular
		elif mover_esquerda or mover_direita:
			jogador.Atualizar_Acao(1)#1: Animação de andar
		else:
			jogador.Atualizar_Acao(0)#0: Animação de parado
		jogador.Mover(mover_esquerda, mover_direita)


	#Sair do jogo
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			exit()


		#Teclas precionadas
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				mover_esquerda = True
			if event.key == pygame.K_d:
				mover_direita = True
			if event.key == pygame.K_k:
				atirar = True
			if event.key == pygame.K_SPACE and jogador.vida:
				jogador.pular = True
			if event.key == pygame.K_ESCAPE:
				sys.exit()

		#Teclas não precionadas
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				mover_esquerda = False
			if event.key == pygame.K_d:
				mover_direita = False
			if event.key == pygame.K_k:
				atirar = False
			
	#Atualizar a tela
	pygame.display.update()
