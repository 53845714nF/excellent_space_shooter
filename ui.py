"""
UI Components Module.
Provides interactive Buttons, TextInputs and UI rendering helpers.
"""
import pygame
from sprites import Sheet, get_sheet


class Button:
    """
    Interactive UI Button supporting Kenney sprite sheet textures,
    hover highlights, keyboard navigation and click events.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        style: str = "blue",
        hover_style: str = "yellow",
        text_color=(0, 0, 0),
        hover_text_color=(0, 0, 0),
        sheet: Sheet = None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.hover_text_color = hover_text_color
        self.is_hovered = False
        self.is_selected = False

        # Load button sprites if available
        self.normal_surf = None
        self.hover_surf = None
        try:
            active_sheet = sheet or get_sheet()
            normal_key = f"button{style.capitalize()}"
            hover_key = f"button{hover_style.capitalize()}"

            raw_normal = active_sheet.get_image_name(normal_key)
            raw_hover = active_sheet.get_image_name(hover_key)

            self.normal_surf = pygame.transform.smoothscale(
                raw_normal, (width, height)
            )
            self.hover_surf = pygame.transform.smoothscale(
                raw_hover, (width, height)
            )
        except Exception:
            self.normal_surf = None
            self.hover_surf = None

    def update_hover(self, mouse_pos):
        """
        Updates hover state based on mouse position.
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, event) -> bool:
        """
        Checks if mouse left-clicked on this button.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen: pygame.Surface, force_active: bool = False):
        """
        Draws the button onto the screen.
        """
        active = self.is_hovered or self.is_selected or force_active

        if active and self.hover_surf:
            screen.blit(self.hover_surf, self.rect)
        elif self.normal_surf:
            screen.blit(self.normal_surf, self.rect)
        else:
            # Fallback rect if texture not available
            bg = (240, 190, 40) if active else (50, 110, 200)
            pygame.draw.rect(screen, bg, self.rect, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=6)

        # Draw text (draw subtle shadow only for light text colors)
        color = self.hover_text_color if active else self.text_color
        txt_surf = self.font.render(self.text, True, color)

        text_x = self.rect.centerx - txt_surf.get_width() // 2
        text_y = self.rect.centery - txt_surf.get_height() // 2

        if sum(color[:3]) > 250:
            shadow_surf = self.font.render(self.text, True, (20, 20, 30))
            screen.blit(shadow_surf, (text_x + 1, text_y + 2))

        screen.blit(txt_surf, (text_x, text_y))


class TextInput:
    """
    Interactive text input field for entering highscore names.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font: pygame.font.Font,
        default_text: str = "PILOT",
        max_length: int = 10,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = default_text
        self.max_length = max_length
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 30  # Frames per blink toggle

    def handle_event(self, event) -> bool:
        """
        Handles keyboard and mouse events.
        Returns True if Enter was pressed (submit).
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:
                # Accept letters, digits, underscores and spaces
                char = event.unicode.upper()
                if char.isalnum() or char in (" ", "-", "_"):
                    self.text += char

        return False

    def update(self):
        """
        Updates blinking cursor state.
        """
        self.cursor_timer += 1
        if self.cursor_timer >= self.cursor_interval:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen: pygame.Surface):
        """
        Draws the text input field with border and blinking cursor.
        """
        self.update()

        # Background
        bg_color = (25, 30, 50, 220)
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        screen.blit(bg_surface, self.rect.topleft)

        # Border
        border_color = (255, 204, 0) if self.active else (100, 150, 220)
        border_width = 3 if self.active else 2
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=6)

        # Text display
        display_text = self.text
        if self.active and self.cursor_visible:
            display_text += "_"

        txt_surf = self.font.render(display_text, True, (255, 255, 255))
        shadow_surf = self.font.render(display_text, True, (10, 10, 20))

        text_x = self.rect.centerx - txt_surf.get_width() // 2
        text_y = self.rect.centery - txt_surf.get_height() // 2

        screen.blit(shadow_surf, (text_x + 1, text_y + 1))
        screen.blit(txt_surf, (text_x, text_y))


class VolumeSlider:
    """
    Interactive segmented volume bar supporting drag, click and direct level display.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font: pygame.font.Font,
        segments: int = 10,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.segments = segments
        self.is_dragging = False

    def handle_event(self, event, current_volume: float) -> tuple[bool, float]:
        """
        Handles mouse clicks and dragging.
        Returns (changed: bool, new_volume: float).
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                new_vol = self._calculate_volume(event.pos[0])
                return True, new_vol
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            new_vol = self._calculate_volume(event.pos[0])
            return True, new_vol
        return False, current_volume

    def _calculate_volume(self, mouse_x: int) -> float:
        rel_x = max(0, min(self.rect.width, mouse_x - self.rect.x))
        ratio = rel_x / float(self.rect.width)
        # Snap to steps of 0.05
        snapped = round(ratio * 20.0) / 20.0
        return max(0.0, min(1.0, snapped))

    def draw(self, screen: pygame.Surface, volume: float):
        """Draws the segmented volume gauge."""
        # Background
        bg_surf = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA
        )
        bg_surf.fill((20, 24, 40, 220))
        screen.blit(bg_surf, self.rect.topleft)

        # Border
        pygame.draw.rect(screen, (0, 200, 255), self.rect, 2, border_radius=6)

        # Segment blocks
        pad = 3
        inner_w = self.rect.width - pad * 2
        inner_h = self.rect.height - pad * 2
        seg_w = (inner_w - (self.segments - 1) * 2) / float(self.segments)
        active_segs = int(round(volume * self.segments))

        for i in range(self.segments):
            seg_x = int(self.rect.x + pad + i * (seg_w + 2))
            seg_rect = pygame.Rect(seg_x, self.rect.y + pad, int(seg_w), inner_h)

            if i < active_segs:
                if i < 6:
                    color = (50, 220, 100)
                elif i < 8:
                    color = (255, 204, 0)
                else:
                    color = (255, 80, 50)
                pygame.draw.rect(screen, color, seg_rect, border_radius=2)
            else:
                pygame.draw.rect(screen, (40, 50, 75), seg_rect, border_radius=2)

        # Percentage Text
        pct_text = f"{int(round(volume * 100))}%"
        txt_surf = self.font.render(pct_text, True, (255, 255, 255))
        sh_surf = self.font.render(pct_text, True, (10, 10, 20))
        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        screen.blit(sh_surf, (tx + 1, ty + 1))
        screen.blit(txt_surf, (tx, ty))


def draw_panel(
    screen: pygame.Surface,
    rect: pygame.Rect,
    bg_color=(15, 20, 35, 220),
    border_color=(0, 200, 255),
    border_width=2,
    border_radius=8,
):
    """
    Renders a semi-transparent panel with a stylized border.
    """
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel_surf.fill(bg_color)
    screen.blit(panel_surf, rect.topleft)
    if border_width > 0:
        pygame.draw.rect(
            screen, border_color, rect, border_width, border_radius=border_radius
        )


def draw_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple,
    center_pos: tuple = None,
    topleft_pos: tuple = None,
    shadow: bool = True,
    shadow_color=(10, 10, 20),
):
    """
    Helper to render text with optional shadow.
    """
    txt_surf = font.render(text, True, color)
    if center_pos:
        pos = (
            center_pos[0] - txt_surf.get_width() // 2,
            center_pos[1] - txt_surf.get_height() // 2,
        )
    elif topleft_pos:
        pos = topleft_pos
    else:
        pos = (0, 0)

    if shadow:
        sh_surf = font.render(text, True, shadow_color)
        screen.blit(sh_surf, (pos[0] + 2, pos[1] + 2))
    screen.blit(txt_surf, pos)
    return txt_surf.get_rect(topleft=pos)
