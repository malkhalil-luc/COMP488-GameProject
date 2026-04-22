import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, HUD_H, BOSS_BAR_H, COLOR_LEADER


class GameViewMixin:
    def _draw_menu_options(
        self,
        panel: pygame.Rect,
        options: list[str],
        selected_index: int,
        top: int,
    ) -> None:
        for index, option in enumerate(options):
            is_selected = index == selected_index
            color = (255, 240, 150) if is_selected else (210, 210, 210)
            prefix = "> " if is_selected else "  "
            option_surf = self.font_sub.render(f"{prefix}{option}", True, color)
            self.screen.blit(
                option_surf,
                option_surf.get_rect(centerx=panel.centerx, top=top + index * 34),
            )

    def _draw_hud(self) -> None:
        score_surf = self.font.render(f"Score: {self.runtime.score}", True, (240, 240, 240))
        self.screen.blit(score_surf, score_surf.get_rect(topleft=(12, 14)))

        level_label = f"L{self.current_level_index + 1}  W{self.current_wave_index + 1}"
        if self.runtime.leader_alive:
            level_label = f"L{self.current_level_index + 1}  LEADER"
        level_surf = self.font.render(level_label, True, (200, 200, 200))
        self.screen.blit(level_surf, level_surf.get_rect(center=(SCREEN_WIDTH // 2, 24)))

        for i in range(self.runtime.lives):
            hx = SCREEN_WIDTH - 20 - i * 26
            if self.life_icon_img is not None:
                self.screen.blit(self.life_icon_img, (hx - 20, 12))

        pygame.draw.line(
            self.screen, (60, 60, 80),
            (0, HUD_H - 1), (SCREEN_WIDTH, HUD_H - 1), 2
        )

        powerup_surf = self.font.render(
            f"Powerups: {self._get_powerup_status()}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(powerup_surf, powerup_surf.get_rect(topleft=(12, 36)))

        audio_surf = self.font.render(
            f"Audio: {self._get_audio_status()}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(audio_surf, audio_surf.get_rect(topright=(SCREEN_WIDTH - 12, 36)))

        if self.runtime.pickup_text_timer > 0 and self.runtime.pickup_text:
            self._draw_attention_banner(
                self.runtime.pickup_text,
                (235, 245, 255),
                (70, 120, 180),
                HUD_H + 8,
            )

        if self.runtime.status_text_timer > 0 and self.runtime.status_text:
            self._draw_attention_banner(
                self.runtime.status_text,
                (255, 245, 170),
                (160, 120, 40),
                HUD_H + 44,
            )

        if self.runtime.leader_alive:
            self._draw_boss_bar()

    def _draw_boss_bar(self) -> None:
        from components.health import HealthComponent
        from components.tag import TagComponent

        leader_entities = self.world.get_entities_with(TagComponent, HealthComponent)
        leader_hp = 0
        leader_max = 1

        for eid in leader_entities:
            tag = self.world.get_component(eid, TagComponent)
            if tag.label == "leader":
                health = self.world.get_component(eid, HealthComponent)
                leader_hp = health.hp
                leader_max = health.max_hp
                break

        bar_w = 300
        bar_h = 18
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y = SCREEN_HEIGHT - BOSS_BAR_H + (BOSS_BAR_H - bar_h) // 2

        track_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(self.screen, (60, 20, 20), track_rect)

        pct = leader_hp / leader_max
        fill_w = int(bar_w * pct)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
        pygame.draw.rect(self.screen, COLOR_LEADER, fill_rect)

        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, 2)

        label = self.font.render(f"LEADER  {leader_hp}/{leader_max}", True, (240, 240, 240))
        self.screen.blit(label, label.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=bar_y - 4,
        ))

    def _draw_feedback_overlay(self) -> None:
        if self.runtime.screen_flash_timer <= 0:
            return

        if self.runtime.state not in ("play", "paused", "transition"):
            return

        alpha = min(120, self.runtime.screen_flash_timer * 10)
        if self.reduced_flash:
            alpha = min(36, self.runtime.screen_flash_timer * 8)
        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flash.fill((*self.runtime.screen_flash_color, alpha))
        self.screen.blit(flash, (0, 0))

    def _get_audio_status(self) -> str:
        if not self.audio.enabled:
            return "OFF"
        if self.audio.muted:
            return f"MUTED {self.audio.get_volume_percent()}%"
        return f"ON {self.audio.get_volume_percent()}%"

    def _get_accessibility_status(self) -> str:
        if self.reduced_flash:
            return "Flash: Reduced"
        return "Flash: Normal"

    def _get_powerup_status(self) -> str:
        active = []

        if self.runtime.rapid_fire_timer > 0:
            active.append(f"Rapid {self.runtime.rapid_fire_timer / 60:.1f}s")
        if self.runtime.shield_timer > 0:
            active.append(f"Shield {self.runtime.shield_timer / 60:.1f}s")
        if self.runtime.pickup_text_timer > 0 and self.runtime.pickup_text == "EXTRA LIFE":
            active.append("Life +1")

        if not active:
            return "None"

        return ", ".join(active)

    def _draw_debug_panel(self) -> None:
        panel = pygame.Rect(10, SCREEN_HEIGHT - 168, 280, 154)
        surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        surf.fill((8, 8, 18, 190))
        self.screen.blit(surf, panel.topleft)
        pygame.draw.rect(self.screen, (90, 90, 130), panel, 2)

        wave_text = f"{self.current_wave_index + 1}"
        if self.runtime.leader_alive:
            wave_text = "Leader"

        lines = [
            f"DEBUG  FPS: {self.clock.get_fps():.1f}",
            f"State: {self.runtime.state}",
            f"Level: {self.current_level_index + 1}   Wave: {wave_text}",
            f"Lives: {self.runtime.lives}   Audio: {self._get_audio_status()}",
            f"Powerups: {self._get_powerup_status()}",
            f"Rapid Left: {self.runtime.rapid_fire_timer / 60:.1f}s",
            f"Shield Left: {self.runtime.shield_timer / 60:.1f}s",
            self._get_accessibility_status(),
        ]

        y = panel.top + 10
        for line in lines:
            text = self.font.render(line, True, (230, 230, 230))
            self.screen.blit(text, (panel.left + 10, y))
            y += 17

    def _draw_attention_banner(
        self,
        text: str,
        text_color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        top_y: int,
    ) -> None:
        banner = pygame.Rect(SCREEN_WIDTH // 2 - 140, top_y, 280, 28)
        shade = pygame.Surface((banner.width, banner.height), pygame.SRCALPHA)
        shade.fill((12, 16, 26, 210))
        self.screen.blit(shade, banner.topleft)
        pygame.draw.rect(self.screen, border_color, banner, 2)

        shadow = self.font.render(text, True, (20, 20, 20))
        shadow_rect = shadow.get_rect(center=(banner.centerx + 1, banner.centery + 1))
        self.screen.blit(shadow, shadow_rect)

        surf = self.font.render(text, True, text_color)
        rect = surf.get_rect(center=banner.center)
        self.screen.blit(surf, rect)

    def _draw_overlay_panel(self, height: int = 240) -> pygame.Rect:
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - height // 2, 440, height)
        dark = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        dark.fill((10, 10, 20, 210))
        self.screen.blit(dark, panel.topleft)
        pygame.draw.rect(self.screen, (100, 100, 140), panel, 2)
        return panel

    def _draw_title_overlay(self) -> None:
        panel = self._draw_overlay_panel(400)

        title = self.font_title.render("INVASION SPACERS", True, (0, 200, 255))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        self._draw_menu_options(panel, self.menu_options, self.menu_selected, panel.top + 96)

        score_title = self.font.render("Top 5 Scores", True, (220, 220, 220))
        self.screen.blit(score_title, score_title.get_rect(centerx=panel.centerx, top=panel.top + 216))

        score_box = pygame.Rect(panel.left + 54, panel.top + 238, panel.width - 108, 102)
        box_fill = pygame.Surface((score_box.width, score_box.height), pygame.SRCALPHA)
        box_fill.fill((18, 22, 34, 170))
        self.screen.blit(box_fill, score_box.topleft)
        pygame.draw.rect(self.screen, (80, 90, 120), score_box, 1)

        rank_x = score_box.left + 16
        name_x = score_box.left + 58
        score_x = score_box.right - 16

        rank_head = self.font.render("#", True, (170, 170, 185))
        name_head = self.font.render("Name", True, (170, 170, 185))
        score_head = self.font.render("Score", True, (170, 170, 185))
        self.screen.blit(rank_head, rank_head.get_rect(left=rank_x, top=score_box.top + 8))
        self.screen.blit(name_head, name_head.get_rect(left=name_x, top=score_box.top + 8))
        self.screen.blit(score_head, score_head.get_rect(right=score_x, top=score_box.top + 8))

        if self.high_scores:
            for index, item in enumerate(self.high_scores[:5]):
                row_y = score_box.top + 28 + index * 14
                rank_text = self.font.render(f"{index + 1}.", True, (200, 200, 210))
                name_text = self.font.render(str(item["name"]), True, (200, 200, 210))
                score_text = self.font.render(str(item["score"]), True, (200, 200, 210))

                self.screen.blit(rank_text, rank_text.get_rect(left=rank_x, top=row_y))
                self.screen.blit(name_text, name_text.get_rect(left=name_x, top=row_y))
                self.screen.blit(score_text, score_text.get_rect(right=score_x, top=row_y))
        else:
            empty = self.font.render("No scores saved yet", True, (180, 180, 190))
            self.screen.blit(empty, empty.get_rect(center=score_box.center))

        hint = self.font.render("Menu: Up / Down    Confirm: Enter", True, (140, 140, 160))
        self.screen.blit(hint, hint.get_rect(centerx=panel.centerx, top=panel.top + 352))

        hint2 = self.font.render("M: Mute  - / +: Volume  F: Reduced Flash", True, (140, 140, 160))
        self.screen.blit(hint2, hint2.get_rect(centerx=panel.centerx, top=panel.top + 372))

    def _draw_controls_overlay(self) -> None:
        panel = self._draw_overlay_panel(330)

        title = self.font_title.render("CONTROLS", True, (240, 240, 240))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        lines = [
            "Move: Arrow Keys / WASD",
            "Fire: Space / Left Shift / Right Shift",
            "Pause / Resume: P or ESC",
            "Mute Audio: M",
            "Volume: - / +",
            "Reduced Flash: F",
            "Debug Toggle: F1",
            "Quit from Menus: Q",
        ]

        for index, line in enumerate(lines):
            surf = self.font.render(line, True, (210, 210, 210))
            self.screen.blit(surf, surf.get_rect(centerx=panel.centerx, top=panel.top + 86 + index * 22))

        back = self.font.render("Press ESC, Backspace, or Enter to return", True, (180, 180, 180))
        self.screen.blit(back, back.get_rect(centerx=panel.centerx, top=panel.top + 286))

    def _draw_pause_overlay(self) -> None:
        panel = self._draw_overlay_panel(300)

        paused = self.font_title.render("PAUSED", True, (240, 240, 100))
        self.screen.blit(paused, paused.get_rect(centerx=panel.centerx, top=panel.top + 30))

        self._draw_menu_options(panel, self.pause_options, self.pause_selected, panel.top + 98)

        controls = self.font.render("Menu: Up / Down    Confirm: Enter", True, (180, 180, 180))
        self.screen.blit(controls, controls.get_rect(centerx=panel.centerx, top=panel.top + 244))

        hint = self.font.render("ESC or P also resumes    M: Mute    F1: Debug", True, (180, 180, 180))
        self.screen.blit(hint, hint.get_rect(centerx=panel.centerx, top=panel.top + 266))

    def _draw_transition_overlay(self) -> None:
        panel = self._draw_overlay_panel(250)

        title = self.font_title.render(self.transition_text, True, (240, 240, 240))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 42))

        ready = self.font_sub.render("Get Ready", True, (200, 200, 120))
        self.screen.blit(ready, ready.get_rect(centerx=panel.centerx, top=panel.top + 116))

    def _draw_gameover_overlay(self) -> None:
        panel = self._draw_overlay_panel(420)

        tint = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        tint.fill((90, 20, 20, 70))
        self.screen.blit(tint, panel.topleft)
        pygame.draw.rect(self.screen, (150, 70, 70), panel, 2)

        title = self.font_title.render("GAME OVER", True, (245, 245, 245))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.runtime.score}", True, (245, 245, 245))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 98))

        name_box = pygame.Rect(panel.centerx - 110, panel.top + 140, 220, 28)
        pygame.draw.rect(self.screen, (22, 26, 40), name_box)
        pygame.draw.rect(self.screen, (150, 150, 190), name_box, 2)

        typed_name = self.runtime.score_name_input or "TYPE NAME"
        name_color = (240, 240, 240) if self.runtime.score_name_input else (150, 150, 165)
        name_text = self.font.render(typed_name, True, name_color)
        self.screen.blit(name_text, name_text.get_rect(center=name_box.center))

        save_text = "Saved" if self.runtime.score_saved else "Type your name, then choose Save Score"
        save_hint = self.font.render(save_text, True, (220, 220, 220))
        self.screen.blit(save_hint, save_hint.get_rect(centerx=panel.centerx, top=panel.top + 182))

        self._draw_menu_options(panel, self.end_options, self.gameover_selected, panel.top + 238)

        quit_text = self.font.render("Menu: Up / Down    Confirm: Enter", True, (230, 230, 230))
        self.screen.blit(quit_text, quit_text.get_rect(centerx=panel.centerx, top=panel.top + 384))

    def _draw_victory_overlay(self) -> None:
        panel = self._draw_overlay_panel(420)

        title = self.font_title.render("VICTORY!", True, (100, 220, 100))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.runtime.score}", True, (240, 240, 240))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 98))

        name_box = pygame.Rect(panel.centerx - 110, panel.top + 140, 220, 28)
        pygame.draw.rect(self.screen, (22, 26, 40), name_box)
        pygame.draw.rect(self.screen, (150, 150, 190), name_box, 2)

        typed_name = self.runtime.score_name_input or "TYPE NAME"
        name_color = (240, 240, 240) if self.runtime.score_name_input else (150, 150, 165)
        name_text = self.font.render(typed_name, True, name_color)
        self.screen.blit(name_text, name_text.get_rect(center=name_box.center))

        save_text = "Saved" if self.runtime.score_saved else "Type your name, then choose Save Score"
        save_hint = self.font.render(save_text, True, (220, 220, 220))
        self.screen.blit(save_hint, save_hint.get_rect(centerx=panel.centerx, top=panel.top + 182))

        self._draw_menu_options(panel, self.end_options, self.victory_selected, panel.top + 238)

        quit_text = self.font.render("Menu: Up / Down    Confirm: Enter", True, (180, 180, 180))
        self.screen.blit(quit_text, quit_text.get_rect(centerx=panel.centerx, top=panel.top + 384))
