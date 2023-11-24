import pygame
import os
import sys
from random import randint
from pygame.locals import *
from sys import exit

pygame.init()

#Resolução da tela
width = 1280
height = 720

size = width, height
screen = pygame.display.set_mode((size))

#Nome do jogo
pygame.display.set_caption ('Rambo: Programado para explodir')

#Frames por segundo
clock = pygame.time.Clock()
FPS = 60

#Variaveis de ações do jogador
mover_esquerda = False
mover_direita = False

#Definindo o Background

BG = (144, 201, 120)
def Carregar_Background():
	screen.fill(BG)

#Classe para criação de personagem
class Soldado(pygame.sprite.Sprite):
	def __init__(self, tipo_personagem, x, y, scale, velocidade):
		pygame.sprite.Sprite.__init__(self)
		self.tipo_personagem = tipo_personagem
		self.velocidade = velocidade
		self.direcao = 1
		self.flip = False
		self.lista_animacao = []
		self.index = 0
		for i in range(8):
			personagem = pygame.image.load(f'C:/Users/pedro/OneDrive/Área de Trabalho/Rambo_Programado_Para_Explodir/{self.tipo_personagem}/Descanso/{i}.png')
			personagem = pygame.transform.scale(personagem, (int(personagem.get_width() * scale), int(personagem.get_height() * scale)))
			self.lista_animacao.append(personagem)
		self.personagem = self.lista_animacao[self.index]
		self.rect = self.personagem.get_rect()
		self.rect.center = (x , y)

	def Mover(self, mover_esquerda, mover_direita):
		#Atribuindo variáveis ​​de movimento
		dy = 0
		dx = 0

		if mover_esquerda:
			dx = -self.velocidade
			self.flip = True
			self.direcao = -1
		if mover_direita:
			dx = self.velocidade
			self.flip = False
			self.direcao = 1

		#Atualizar a posição
		self.rect.x += dx
		self.rect.y += dy

	def Carregar(self):
		#Carregar o personagem
		screen.blit(pygame.transform.flip(self.personagem, self.flip, False), self.rect)

#Criando personagens
#Tipo, posição X, posição Y, escala, velocidade
jogador = Soldado('Rambo', width/2, height/2, 0.5, 5)

while True:

	clock.tick(FPS)

	Carregar_Background()
	jogador.Carregar()
	jogador.Mover(mover_esquerda, mover_direita)

	for event in pygame.event.get():
		#Sair do jogo
		if event.type == QUIT:
			pygame.quit()
			exit()

		#Teclas precionadas
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				mover_esquerda = True
			if event.key == pygame.K_d:
				mover_direita = True
			if event.key == pygame.K_ESCAPE:
				sys.exit()

		#Teclas não precionadas
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				mover_esquerda = False
			if event.key == pygame.K_d:
				mover_direita = False
			
	#Atualizar a tela
	pygame.display.update()
