# core/engine.py
import pygame
import sys
from .constants import *
from .utils import *
from .assets import AssetManager
from .models import Fly
from .network import upload_score, flush_pending

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Frog Jump Game")
        
        # 아이콘 설정
        try:
            icon = pygame.image.load(os.path.join(ASSETS_DIR, "frog.ico"))
            pygame.display.set_icon(icon)
        except: pass

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("malgungothic", 36)
        self.big_font = pygame.font.SysFont("malgungothic", 72)

        self.assets = AssetManager()
        
        # 상태 및 프로필 로드
        self.profile = load_profile()
        if self.profile and self.profile.get("nickname", "").strip():
            self.nickname = self.profile["nickname"].strip()
            self.state = STATE_PROLOGUE
        else:
            self.nickname = "PLAYER"
            self.state = STATE_NAME_ENTRY

        self.reset_round_vars()
        self.init_name_entry()

        # 프롤로그 페이드
        self.fade_alpha = 255
        self.fade_speed = 3
        self.fade_done_time = None

        # 업로드 상태
        self.score_uploaded = False
        self.upload_status = ""
        self.upload_status_time = 0

        # 초기 큐 정리
        try: flush_pending(force=True)
        except: pass

    def reset_round_vars(self):
        self.score = 0
        self.remaining_time = GAME_TIME
        self.ground_y = (SCREEN_HEIGHT - 170) - self.assets.frog_normal.get_rect().height
        self.flies = [Fly(self.assets.fly_origin, self.ground_y) for _ in range(6)]
        
        self.frog_rect = self.assets.frog_normal.get_rect()
        self.frog_rect.x = SCREEN_WIDTH // 2
        self.frog_rect.y = self.ground_y
        
        self.start_ticks = pygame.time.get_ticks()
        self.charging = self.jumping = self.falling = False
        self.velocity_y = self.jump_height = 0
        self.target_y = self.ground_y
        self.character_img = self.assets.frog_normal
        self.ranking = []
        self.score_uploaded = False
        self.upload_status = ""
        self.upload_status_time = 0

    def init_name_entry(self):
        self.name_text = ""
        if self.state == STATE_NAME_ENTRY:
            pygame.key.start_text_input()
            pygame.key.set_text_input_rect(NAME_BOX_RECT)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if self.state == STATE_NAME_ENTRY:
                self.handle_name_entry_event(event)
            elif self.state == STATE_START:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = STATE_GAME; self.reset_round_vars()
            elif self.state == STATE_GAME:
                self.handle_game_event(event)
            elif self.state == STATE_GAMEOVER:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.state = STATE_GAME; self.reset_round_vars()

    def handle_name_entry_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if OK_BTN_RECT.collidepoint(event.pos) or EXIT_BTN_RECT.collidepoint(event.pos):
                self.confirm_nickname()
        elif event.type == pygame.TEXTINPUT:
            if len(self.name_text) < 16: self.name_text += event.text
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE: self.name_text = self.name_text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE): self.confirm_nickname()

    def confirm_nickname(self):
        self.nickname = self.name_text.strip() or "PLAYER"
        save_profile(self.nickname)
        pygame.key.stop_text_input(); self.state = STATE_PROLOGUE

    def handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.jumping:
                self.charging = True; self.jump_height = 0
                self.character_img = self.assets.frog_prepare
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and self.charging:
                self.charging = False; self.jumping = True
                self.target_y = self.ground_y - self.jump_height
                self.velocity_y = -JUMP_SPEED
                self.character_img = self.assets.frog_jump

    def update(self):
        if self.state == STATE_GAME:
            elapsed = (pygame.time.get_ticks() - self.start_ticks) // 1000
            self.remaining_time = max(0, GAME_TIME - elapsed)
            if self.remaining_time == 0: self.game_over(); return

            for fly in self.flies: fly.update()

            keys = pygame.key.get_pressed()
            move = MOVE_SPEED if not self.jumping else MOVE_SPEED * AIR_CONTROL
            if keys[pygame.K_LEFT]:
                self.frog_rect.x -= move
                if not self.jumping and not self.charging: self.character_img = self.assets.frog_left
            elif keys[pygame.K_RIGHT]:
                self.frog_rect.x += move
                if not self.jumping and not self.charging: self.character_img = self.assets.frog_right
            elif not self.jumping and not self.charging: self.character_img = self.assets.frog_normal
            
            self.frog_rect.x = max(0, min(self.frog_rect.x, SCREEN_WIDTH - self.frog_rect.width))

            if self.charging:
                ratio = self.jump_height / MAX_JUMP_HEIGHT
                self.jump_height = min(self.jump_height + max(5, int(18 * (1 - ratio)) + 1), MAX_JUMP_HEIGHT)

            if self.jumping:
                self.frog_rect.y += self.velocity_y
                if not self.falling and self.frog_rect.y <= self.target_y:
                    self.frog_rect.y = self.target_y; self.falling = True
                if self.falling: self.velocity_y += GRAVITY
                if self.frog_rect.y >= self.ground_y:
                    self.frog_rect.y = self.ground_y; self.jumping = self.falling = False
                    self.velocity_y = 0; self.character_img = self.assets.frog_normal

            for fly in self.flies[:]:
                if self.frog_rect.colliderect(fly.rect):
                    self.score += 2 if fly.big else 1
                    self.flies.remove(fly)
                    self.flies.append(Fly(self.assets.fly_origin, self.ground_y))

    def game_over(self):
        self.ranking = save_score_local(self.score)
        if not self.score_uploaded:
            if upload_score(self.nickname, self.score): self.upload_status = "UPLOADED"
            else: self.upload_status = "QUEUED"
            self.upload_status_time = pygame.time.get_ticks()
            self.score_uploaded = True
        self.state = STATE_GAMEOVER

    def draw(self):
        if self.state == STATE_NAME_ENTRY: self.draw_name_entry()
        elif self.state == STATE_PROLOGUE: self.draw_prologue()
        elif self.state == STATE_START: self.screen.blit(self.assets.start_bg, (0, 0))
        elif self.state in (STATE_GAME, STATE_GAMEOVER): self.draw_game_main()
        pygame.display.update()

    def draw_name_entry(self):
        self.screen.blit(self.assets.name_entry_bg, (0, 0))
        caret = "|" if (pygame.time.get_ticks() // 350) % 2 == 0 else ""
        show_text = (self.name_text + caret) if self.name_text else ("Enter Name..." + caret)
        txt_surf = self.font.render(show_text, True, (255, 255, 255) if self.name_text else (220, 220, 220))
        self.screen.blit(txt_surf, txt_surf.get_rect(midleft=(NAME_BOX_RECT.left + 20, NAME_BOX_RECT.centery)))

    def draw_prologue(self):
        self.screen.blit(self.assets.prologue_bg, (0, 0))
        fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); fade.fill((0,0,0)); fade.set_alpha(self.fade_alpha)
        self.screen.blit(fade, (0,0))
        self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
        if self.fade_alpha == 0:
            if not self.fade_done_time: self.fade_done_time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.fade_done_time >= 1000: self.state = STATE_START

    def draw_game_main(self):
        self.screen.blit(self.assets.background, (0, 0))
        for fly in self.flies:
            if fly.glow: self.screen.blit(fly.glow, fly.glow.get_rect(center=fly.rect.center))
            self.screen.blit(fly.image, fly.rect)
        self.screen.blit(self.character_img, self.frog_rect)
        if self.charging and self.state == STATE_GAME: self.draw_gauge()
        timer_color = (255, 80, 80) if (self.remaining_time <= 10 and (pygame.time.get_ticks() // 300) % 2 == 0) else (255, 255, 255)
        self.screen.blit(self.font.render(f"Time : {self.remaining_time}", True, timer_color), (SCREEN_WIDTH - 150, 20))
        self.screen.blit(self.font.render(f"Score : {self.score}", True, (255, 255, 255)), (20, 20))
        if self.state == STATE_GAMEOVER: self.draw_gameover()

    def draw_gauge(self):
        w, h, x, y = 120, 14, SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 35
        ratio = self.jump_height / MAX_JUMP_HEIGHT
        color = (0, 200, 0) if ratio < 0.6 else (230, 180, 0) if ratio < 0.85 else (230, 50, 50)
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, w, h))
        pygame.draw.rect(self.screen, color, (x, y, int(w * ratio), h))

    def draw_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(180); overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))
        self.screen.blit(self.big_font.render("TIME OVER", True, (255, 80, 80)), (SCREEN_WIDTH // 2 - 180, 80))
        y = 180
        for i, s in enumerate(self.ranking):
            color = (255, 200, 0) if s == self.score else (255, 255, 255)
            self.screen.blit(self.font.render(f"{i+1} : {s}", True, color), (SCREEN_WIDTH // 2 - 70, y)); y += 35
        self.screen.blit(self.font.render("Press R : REPLAY", True, (200, 200, 200)), (SCREEN_WIDTH // 2 - 110, y + 30))
        if self.upload_status and (pygame.time.get_ticks() - self.upload_status_time) < 5000:
            self.screen.blit(self.font.render(f"SERVER: {self.upload_status}", True, (180, 180, 180)), (SCREEN_WIDTH // 2 - 90, y + 70))

    def run(self):
        while True:
            self.clock.tick(60)
            self.handle_events()
            self.update(); self.draw()
