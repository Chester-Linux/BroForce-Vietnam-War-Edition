import pygame
import os
import sys
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
pygame.display.set_caption ("Imagine War: Rambo's Last Verse")

#Frames por segundo
clock = pygame.time.Clock()
FPS = 60

#Gravidade
GRAVIDADE = 0.5

#Variaveis de ações do jogador
mover_esquerda = False
mover_direita = False
atirar = False

#Definindo o Background
BG = (145, 201, 125)
CHAO = (255, 0, 0)

def Carregar_Background():
	screen.fill(BG)
	pygame.draw.line(screen, CHAO, (0, 1000), (width, 1000))


#Classe para criação de personagem
class Soldado(pygame.sprite.Sprite):
	def __init__(self, tipo_personagem, x, y, scale, velocidade, qtd_vida):
		pygame.sprite.Sprite.__init__(self)

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

		#Verificador de colisão com o chão, Obs: É provisorio
		if self.rect.bottom + dy > 1000:
			dy = 1000 - self.rect.bottom
			self.no_ar = False


		#Atualizar a posição
		self.rect.x += dx
		self.rect.y += dy

	def Atirar(self):
		if self.limitador_projeteis == 0:
			self.limitador_projeteis = 60
			projetil = Projetil(self.rect.centerx, self.rect.centery, self.direcao)
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

#Classe para a criação de projetil
class Projetil(pygame.sprite.Sprite):
	def __init__(self, x , y, direcao):
		pygame.sprite.Sprite.__init__(self)
		#Velocidade
		self.speed = 25

		#Variavel para inverter a direção do sprite
		self.direcao = direcao
		self.flip = False

		#Escala
		scale = 0.2

		#Variaveis pra rodar as animações
		self.lista_animacao = []
		self.frame_index = 0
		self.atualizacao_tempo = 0
		
		#Selecionando o sprite
		num_quadros = len(os.listdir(f'Municao_Explosao/Projetil'))
		for i in range(num_quadros):
			sprite = pygame.image.load(f'Municao_Explosao/Projetil/{i}.png').convert_alpha()
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

		#Verificar colisões entre personagens e projeteis
		if pygame.sprite.spritecollide(jogador, grupo_projeteis, False):
			if jogador.vida:
				jogador.qtd_vida -= 10
				self.kill()
		if pygame.sprite.spritecollide(inimigo, grupo_projeteis, False):
			if inimigo.vida:
				inimigo.qtd_vida -= 25
				self.kill()

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

class Explosao(pygame.sprite.Sprite):
	def __init__(self, x, y, scale, dano):
		pygame.sprite.Sprite.__init__(self)
		#Escala
		self.scale = scale

		#Variaveis pra rodar as animações
		self.lista_animacao = []
		self.frame_index = 0
		self.atualizacao_tempo = pygame.time.get_ticks()
		
		#Selecionando o sprite
		num_quadros = len(os.listdir(f'Municao_Explosao/Explosao'))
		for i in range(num_quadros):
			sprite = pygame.image.load(f'Municao_Explosao/Explosao/{i}.png').convert_alpha()
			sprite = pygame.transform.scale_by(sprite, scale)
			self.lista_animacao.append(sprite)
		self.image = self.lista_animacao[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


#Criando grupos
grupo_projeteis = pygame.sprite.Group()
grupo_explosoes = pygame.sprite.Group()


#Criando personagens
#Tipo, posição X, posição Y, escala, velocidade, qtd_vida
jogador = Soldado('Rambo', width/2, height/2, 0.4, 10, 100)
inimigo = Soldado('Beatles', width/4, 900, 0.4, 10, 50)

while True:

	#Taxas de quadros por segundo
	clock.tick(FPS)

	#Atualização do background
	Carregar_Background()
	
	#Atualizando o projetil
	grupo_projeteis.update()

	#Atualizando o jogador
	jogador.update()
	inimigo.update()

	
	#Se o protagonista está vivo
	if jogador.vida:
		#Atirando projetis
		if atirar:
			jogador.Atirar()
		#Controlando quando ativa qual animação
		if jogador.no_ar:
			jogador.Atualizar_Acao(2)#2: Animação de pular
		elif mover_esquerda or mover_direita:
			jogador.Atualizar_Acao(1)#1: Animação de andar
		else:
			jogador.Atualizar_Acao(0)#0: Animação de descanso
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
