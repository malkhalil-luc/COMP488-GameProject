# game constants

# window:
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Invasion Spacers"

# play area bounds,
# play area starts after the HUD, S

HUD_H = 48
BOSS_BAR_H = 48

FIELD_TOP = HUD_H # 48 of 600
FIELD_BOTTOM = SCREEN_HEIGHT - BOSS_BAR_H 

#COLORS
COLOR_BG         = (10, 10, 10)
COLOR_PLAYER     = (0, 200,225)
COLOR_ENEMY      = (220, 60,  60)   # red invaders
COLOR_LEADER     = (255, 160,  0)   # orange boss
COLOR_BULLET     = (255, 255, 100)  # yellow projectile
COLOR_WHITE      = (255, 255, 255)  # HUD text
COLOR_LIVES      = (255,  80,  80)  # heart icons
COLOR_HUD_LINE   = (60,   60,  80)  # separator line under HUD strip
COLOR_BOSS_EMPTY = (60,   20,  20)  # empty portion of boss HP bar
COLOR_BOSS_FILL  = (220,  40,  40)  # filled portion of boss HP bar

# PLayer
PLAYER_WIDTH  = 50     # width  in pixels
PLAYER_HEIGHT = 30     # height in pixels
PLAYER_SPEED  = 5      # pixels moved per frame when a key is held

#Enemies
ENEMY_WIDTH   = 36
ENEMY_HEIGHT  = 24
ENEMY_ROWS    = 3
ENEMY_COLS    = 8
ENEMY_GAP_X   = 14     # horizontal gap between enemies
ENEMY_GAP_Y   = 14     # vertical gap between rows
ENEMY_SPEED   = 0.31      # pixels moved downward per frame

# enemy leader
LEADER_WIDTH      = 60
LEADER_HEIGHT      = 40
LEADER_SPEED  = 0.9      # faster than regular enemies
LEADER_HP     = 4      # takes 4 hits to destroy
LEADER_SPEED_X = 4
LEADER_SPEED_Y = 2

#projectiles

BULLET_W      = 4
BULLET_H      = 14
BULLET_SPEED  = 8      # pixels moved upward per frame  (applied as -8 on y)

# HUD  (text sizes in points)
# All text must be ≥ 18 px per accessibility requirement in the spec
FONT_SIZE       = 20
FONT_TITLE_SIZE = 38
FONT_SUB_SIZE   = 22


# 
# Game rules
# Changing these numbers re-balances the game without touching any logic
STARTING_LIVES  = 3
MAX_WAVES       = 3    # how many enemy waves before the boss spawns
SCORE_ENEMY     = 1    # points per regular enemy killed
SCORE_LEADER    = 10   # points per hit on the Enemy Leader
