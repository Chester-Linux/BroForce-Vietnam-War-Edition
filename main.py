import pygame
import os
import sys
import csv
from pygame import mixer
from random import randint
from pygame.locals import *
from sys import exit

mixer.init()
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
colunas = 150

#TILE_SIZE
TILE_SIZE = height//linhas
TILE_TYPES = len(os.listdir(f'Matrizes/Grades'))

#Armazenar tiles em uma lista
lista_sprites = []
for i in range(TILE_TYPES):
	sprite = pygame.image.load(f'Matrizes/Grades/{i}.png')
	sprite = pygame.transform.scale(sprite, (TILE_SIZE, TILE_SIZE))
	lista_sprites.append(sprite)

#Niveis
level = 0
MAX_LEVELS = 3

#Variaveis de menu
start_game = False
tipo_menu = "menu_principal"

#Carregar músicas
#Trilha sonora
pygame.mixer.music.load('Musicas_efeitos_sonoros/Forest.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

#Efeito sonoros
jump_sound = pygame.mixer.Sound('Musicas_efeitos_sonoros/Jump_Sound.wav')
jump_sound.set_volume(0.2)
walk_sound = pygame.mixer.Sound('Musicas_efeitos_sonoros/Walk_Sound.wav')
walk_sound.set_volume(0.2)
eat_sound = pygame.mixer.Sound('Musicas_efeitos_sonoros/Eating_Sound.ogg')
eat_sound.set_volume(0.2)
missle_shot_sound = pygame.mixer.Sound('Musicas_efeitos_sonoros/Missle_Sound.wav')
missle_shot_sound.set_volume(0.3)
bullet_shot_sound = pygame.mixer.Sound('Musicas_efeitos_sonoros/Bullet_Sound.mp3')
bullet_shot_sound.set_volume(0.3)
explosion_sound = pygame.mixer.Sound('Musicas_efeitos_sonoros/Explosion_Sound.wav')
explosion_sound.set_volume(0.3)

#Gravidade
GRAVIDADE = 0.6

#Variaveis de ações do jogador
mover_esquerda = False
mover_direita = False
atirar = False

#Cores
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (80, 80, 80)
BLUE = (0, 0, 255)

#Variaveis para mover a câmera
SCROLL_THRESH = 200
screen_scroll = 0
bg_scroll = 0

#Carregando dos botões
start_image = pygame.image.load('Botoes/Start.png').convert_alpha()
exit_image = pygame.image.load('Botoes/Exit.png').convert_alpha()
reset_image = pygame.image.load('Botoes/Reset.png').convert_alpha()
controles_image = pygame.image.load('Botoes/Controles.png').convert_alpha()
back_image = pygame.image.load('Botoes/Back.png').convert_alpha()

#Carregando imagens para o menu de controles
menu_controles_image = pygame.image.load('Botoes/menu_controles.png').convert_alpha()
andando_image = pygame.image.load('Personagem_Rambo/Andar/0.png').convert_alpha()
andando_image = pygame.transform.scale_by(andando_image, 0.3)
pulando_image = pygame.image.load('Personagem_Rambo/pular/0.png').convert_alpha()
pulando_image = pygame.transform.scale_by(pulando_image, 0.3)
rocket_image = pygame.image.load('Personagem_Rambo/Projetil/0.png').convert_alpha()
rocket_image = pygame.transform.scale_by(rocket_image, 0.3)


#Carregando imagens do background
sky_image = pygame.image.load('Matrizes/Background/sky.png').convert_alpha()
mountain_image = pygame.image.load('Matrizes/Background/mountain.png').convert_alpha()
forest1_image = pygame.image.load('Matrizes/Background/forest1.png').convert_alpha()
forest2_image = pygame.image.load('Matrizes/Background/forest2.png').convert_alpha()
forest3_image = pygame.image.load('Matrizes/Background/forest3.png').convert_alpha()

def Carregar_Background():
	width = sky_image.get_width()
	for i in range(5):
		screen.blit(sky_image, ((i * width) - bg_scroll * 0.5, 0))
		screen.blit(mountain_image, ((i * width) - bg_scroll * 0.6, height - mountain_image.get_height()))
		screen.blit(forest1_image, ((i * width) - bg_scroll * 0.7, height - forest1_image.get_height() - 100))
		screen.blit(forest2_image, ((i * width) - bg_scroll * 0.8, height - forest2_image.get_height() - 60))
		screen.blit(forest3_image, ((i * width) - bg_scroll * 0.9, height - forest3_image.get_height() - 50))

#Definindo a HUD (vulgo interface)// Temporariamente em desuso
font = pygame.font.SysFont('Futura', 50)
def Carregar_HUD(text, font, text_col, x, y):
	sprite = font.render(text, True, text_col)
	screen.blit(sprite, (x, y))

#Classe para os botões
class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

#Função para resetar o level
def reset_level():
	grupo_inimigos.empty()
	grupo_projeteis.empty()
	grupo_explosoes.empty()
	grupo_decoracoes.empty()
	grupo_saidas.empty()

	#Criando novas listas vazias
	data = []
	for linha in range(linhas):
		R = [-1] * colunas
		data.append(R)

	return data

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
		screen_scroll = 0
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
			jump_sound.play()

		#Aplicando gravidade
		self.vetor_y += GRAVIDADE
		if self.vetor_y > 10: #Limita a velocidade da queda
			self.vetor_y
		dy += self.vetor_y

		#Verificar colisão
		for tile in mapa.lista_obstaculo:
			#Para o vetor X
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#Verificando se ele está em cima ou em baixo de uma grade
				if self.vetor_y < 0:
					self.vetor_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vetor_y >= 0:
					self.no_ar = False
					self.vetor_y = 0
					dy = tile[1].top - self.rect.bottom

		#Verificar se ele chegou no fim do level
		level_completo = False
		if pygame.sprite.spritecollide(self, grupo_saidas, False):
			level_completo = True		
		
		#Verificar se ele caiu fora do mapa
		if self.rect.bottom > height:
			self.qtd_vida = 0

		#Verificar se o personagem está saindo do mapa
		if self.tipo_personagem == 'Personagem_Rambo':
			if self.rect.left + dx < 0 or self.rect.right + dx > width:
				dx = 0

		#Atualizar a posição
		self.rect.x += dx
		self.rect.y += dy

		#Atualizar a câmera
		if self.tipo_personagem == 'Personagem_Rambo':
			if (self.rect.right > width - SCROLL_THRESH and bg_scroll < (mapa.largura_level * TILE_SIZE) - width) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_completo


	def Atirar(self, scale):
		self.scale = scale
     
		max_limitador_projeteis = 60
     
		if self.limitador_projeteis == 0:
			self.limitador_projeteis = max_limitador_projeteis
			projetil = Projetil(self.rect.centerx, self.rect.centery, self.direcao, self.tipo_personagem, self.scale)
			grupo_projeteis.add(projetil)
			if self.tipo_personagem == 'Personagem_Rambo':
				missle_shot_sound.play()
			else:
				bullet_shot_sound.play()
		

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
		#pygame.draw.rect(screen, RED, self.rect, 1)

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

		#Atualizando a posição de acordo com a câmera
		self.rect.x += screen_scroll


#Clase para a barra de recarregar a arma
class BarraRealoading():
	def __init__(self, x, y, limitador_projeteis):
		self.x = x
		self.y = y
		self.limitador_projeteis = limitador_projeteis
		self.image = pygame.image.load('Personagem_Rambo/Rosto_HUD/Rosto_Rambo.png').convert_alpha()
		self.image = pygame.transform.scale_by(self.image, 1)


	def Carregar(self, limitador_projeteis):
     
		max_limitador_projeteis = 60
     
		porcentagem = limitador_projeteis / max_limitador_projeteis

		pygame.draw.rect(screen, BLACK, (self.x - 200, self.y - 100, 450, 200))
		pygame.draw.rect(screen, GRAY, (self.x - 5, self.y + 20, 230, 60))
		pygame.draw.rect(screen, YELLOW, ((self.x, self.y + 25, 220 * porcentagem, 50)))
		screen.blit(self.image, (self.x - 150, self.y - 40))



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
		self.rect.x += (self.direcao * self.speed) + screen_scroll

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
					self.kill()	
					explosion_sound.play()
					if self.tipo_personagem == 'Personagem_Rambo':
						explosion_sound.play()
						explosao = Explosao(self.rect.x, self.rect.y, 1)
						grupo_explosoes.add(explosao)
						#Aplicando dano em área para os personagens
						if abs(self.rect.centerx - inimigo.rect.centerx) < TILE_SIZE * 5 and abs(self.rect.centery - inimigo.rect.centery) < TILE_SIZE * 5:
							inimigo.qtd_vida -= 100

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

		#Atualizando a posição de acordo com a câmera
		self.rect.x += screen_scroll


	def Carregar(self):
		screen.blit(self.image, self.rect)

		#Para ver as hitbox
		#pygame.draw.rect(screen, RED, self.rect, 1)

class Mapa():
	def __init__(self):
		self.lista_obstaculo = []

	def process_data(self, data):
		self.largura_level = len(data[0])

		for y, linha in enumerate(data):
			for x, tile in enumerate(linha):
				if tile >= 0:
					sprite = lista_sprites[tile]
					sprite_rect = sprite.get_rect()
					sprite_rect.x = x * TILE_SIZE
					sprite_rect.y = y * TILE_SIZE
					tile_data = (sprite, sprite_rect)
					
					#Grades com colisões
					if tile >= 0 and tile <= 6:#Grades com colisões
						self.lista_obstaculo.append(tile_data)
					#Grades decorativas
					elif tile >= 7 and tile <= 15:#Grades decorativas
						decoracao = Decoracao(sprite, x *TILE_SIZE, y * TILE_SIZE)
						grupo_decoracoes.add(decoracao)
					#Fim da fase
					elif tile == 16:#Fim da fase
						saida = Saida(sprite, x *TILE_SIZE, y * TILE_SIZE)
						grupo_saidas.add(saida)
					#Criar jogador
					elif tile == 17:
						jogador = Soldado('Personagem_Rambo', x * TILE_SIZE, y * TILE_SIZE, 0.4, 15, 100)#Criar jogador
						barra_recarregar_arma = BarraRealoading(170, 60, jogador.limitador_projeteis)
					elif tile == 18:#Criar inimigo
						inimigo = Soldado('Personagem_Vietnamita', x *TILE_SIZE, y * TILE_SIZE, 0.4, 5, 50)#Criar inimigos
						grupo_inimigos.add(inimigo)

		return jogador, barra_recarregar_arma
	
	def Carregar(self):
		for tile in self.lista_obstaculo:
			#Atualizando a posição de acordo com a câmera
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])

class Decoracao(pygame.sprite.Sprite):
	def __init__(self, image, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		#Atualizando a posição de acordo com a câmera
		self.rect.x += screen_scroll

class Saida(pygame.sprite.Sprite):
	def __init__(self, image, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		#Atualizando a posição de acordo com a câmera
		self.rect.x += screen_scroll


#Criando os botões
botao_start = Button(width//2 - 200, height//2 - 400, start_image, 2)
botao_exit = Button(width//2 - 200, height//2, exit_image, 2)
botao_reset = Button(width//2 - 200, height//2, reset_image, 2)
botao_controles = Button(width//2 - 200, height//2 - 200, controles_image, 2)
botao_back = Button(width//2 - 200, height//2 + 300, back_image, 2)


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


	if start_game == False:
		#Cor de fundo do menu
		screen.fill(BLUE)

		#Verificar qual menu está sendo chamado
		if tipo_menu == "menu_principal":
		#Botões
			if botao_start.draw(screen):
				start_game = True
			if botao_controles.draw(screen):
				tipo_menu = "menu_controles"
			if botao_exit.draw(screen):
				pygame.quit()
				exit()
		if tipo_menu == "menu_controles":
			screen.blit(menu_controles_image, (150, 200))
			screen.blit(andando_image, (150, 330))
			screen.blit(pulando_image, (150, 490))
			screen.blit(rocket_image, (150, 620))
			if botao_back.draw(screen):
				tipo_menu = "menu_principal"
	else:
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
			screen_scroll, level_completo = jogador.Mover(mover_esquerda, mover_direita)
			bg_scroll -= screen_scroll

			#Verificar se o jogador terminou o level
			if level_completo:
				level += 1
				world_data = reset_level()
				if level <= MAX_LEVELS:
					with open(f'Matrizes/level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, linha in enumerate(reader):
							for y, tile in enumerate(linha):
								world_data[x][y] = int(tile)
					mapa = Mapa()
					jogador, barra_recarregar_arma = mapa.process_data(world_data)

		else:
			screen_scroll = 0
			if botao_reset.draw(screen):
				bg_scroll = 0
				world_data = reset_level()
				#Carregar os dados e criar um mundo
				with open(f'Matrizes/level{level}_data.csv', newline='') as csvfile:
					reader = csv.reader(csvfile, delimiter=',')
					for x, linha in enumerate(reader):
						for y, tile in enumerate(linha):
							world_data[x][y] = int(tile)
				mapa = Mapa()
				jogador, barra_recarregar_arma = mapa.process_data(world_data)


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
