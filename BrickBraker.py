import math
import random
import pygame


# ============================================================
# BLOCK BREAKER - SOFT ARCADE / SPACE GEMS EDITION
# Kontrol: tombol panah kiri/kanan atau A/D
# Restart setelah Game Over: SPACE
# Keluar: ESC atau tombol X
# ============================================================

pygame.init()

# Ukuran layar dibuat lebih lebar agar tata letak seperti referensi.
WIDTH, HEIGHT = 900, 675
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Breaker - Soft Arcade")

clock = pygame.time.Clock()

# ----------------------------
# Palet warna
# ----------------------------
BG_TOP = (13, 20, 65)
BG_BOTTOM = (35, 31, 105)
WHITE = (248, 250, 255)
PALE_CYAN = (176, 245, 255)
CYAN = (69, 220, 255)
DARK_BLUE = (17, 29, 83)
PANEL_BLUE = (23, 39, 103)
PANEL_EDGE = (65, 207, 255)
GOLD = (255, 197, 74)
PINK = (255, 112, 178)

GEM_COLORS = [
    (255, 116, 181),  # pink
    (255, 190, 72),   # gold
    (66, 224, 215),   # mint
    (91, 174, 255),   # blue
    (180, 132, 255),  # lavender
]

font_small = pygame.font.SysFont("Arial", 17, bold=True)
font_medium = pygame.font.SysFont("Arial", 23, bold=True)
font_title = pygame.font.SysFont("Arial", 43, bold=True)
font_subtitle = pygame.font.SysFont("Arial", 39, bold=True)


# ============================================================
# Fungsi gambar umum
# ============================================================

def adjust_color(color, amount):
    """Mencerahkan atau menggelapkan warna."""
    return tuple(max(0, min(255, channel + amount)) for channel in color)


def draw_text_center(surface, text, font, color, center, outline=None):
    """Menggambar teks dengan opsi outline sederhana."""
    if outline:
        outline_surf = font.render(text, True, outline)
        outline_rect = outline_surf.get_rect(center=(center[0] + 2, center[1] + 3))
        surface.blit(outline_surf, outline_rect)

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center)
    surface.blit(text_surf, text_rect)


def make_background():
    """Membuat latar gradasi dan bintang statis."""
    background = pygame.Surface((WIDTH, HEIGHT))

    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT - 1)
        color = tuple(
            int(BG_TOP[i] * (1 - ratio) + BG_BOTTOM[i] * ratio)
            for i in range(3)
        )
        pygame.draw.line(background, color, (0, y), (WIDTH, y))

    random.seed(18)
    for _ in range(105):
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)
        radius = random.choice([1, 1, 2])
        color = random.choice([
            (112, 174, 255),
            (164, 151, 255),
            (224, 213, 255),
            (95, 224, 255),
        ])
        pygame.draw.circle(background, color, (x, y), radius)

    # Bintang berkilau berukuran kecil.
    for x, y in [(80, 145), (420, 130), (820, 165), (760, 440), (300, 520)]:
        pygame.draw.line(background, (202, 220, 255), (x - 5, y), (x + 5, y), 2)
        pygame.draw.line(background, (202, 220, 255), (x, y - 5), (x, y + 5), 2)

    return background


BACKGROUND = make_background()


def draw_planet(surface, center, radius, color, ring_color=None):
    """Planet dekoratif sederhana di sisi arena."""
    x, y = center

    # Bayangan lembut di belakang planet.
    pygame.draw.circle(surface, (24, 34, 103), (x + 5, y + 7), radius + 3)
    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(
        surface,
        adjust_color(color, 28),
        (x - radius // 3, y - radius // 3),
        max(3, radius // 3),
    )

    # Garis permukaan planet.
    pygame.draw.arc(
        surface,
        adjust_color(color, -25),
        (x - radius + 8, y - radius // 2, radius * 2 - 16, radius),
        math.radians(15),
        math.radians(165),
        3,
    )

    if ring_color:
        ring_rect = pygame.Rect(
            x - radius - 20, y - radius // 3, radius * 2 + 40, radius
        )
        pygame.draw.ellipse(surface, ring_color, ring_rect, 5)


def draw_cloud(surface, x, y, scale=1.0):
    """Awan pastel untuk memperkuat nuansa Soft Arcade."""
    color = (100, 100, 190)
    highlights = (142, 130, 224)

    circles = [
        (x, y + 12 * scale, 22 * scale),
        (x + 25 * scale, y, 28 * scale),
        (x + 54 * scale, y + 13 * scale, 23 * scale),
        (x + 30 * scale, y + 18 * scale, 28 * scale),
    ]

    for cx, cy, radius in circles:
        pygame.draw.circle(surface, color, (int(cx), int(cy)), int(radius))
        pygame.draw.circle(
            surface,
            highlights,
            (int(cx - radius * 0.15), int(cy - radius * 0.25)),
            max(2, int(radius * 0.55)),
        )


def draw_crystals(surface, x, y, scale=1.0):
    """Kristal dekoratif di sudut kanan bawah."""
    crystal_specs = [
        (0, 0, 26, (72, 213, 255)),
        (20, 12, 20, (179, 112, 255)),
        (40, 4, 30, (85, 174, 255)),
    ]

    for offset_x, offset_y, height, color in crystal_specs:
        width = height * 0.55
        points = [
            (int(x + offset_x * scale), int(y + offset_y * scale)),
            (int(x + (offset_x + width / 2) * scale), int(y - height * scale)),
            (int(x + (offset_x + width) * scale), int(y + offset_y * scale)),
            (int(x + (offset_x + width / 2) * scale), int(y + height * 0.25 * scale)),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, adjust_color(color, 55), points, 2)
        pygame.draw.line(
            surface,
            (225, 250, 255),
            points[0],
            points[1],
            2,
        )


def draw_robot(surface, x, y, scale=1.0):
    """Maskot robot kecil yang digambar langsung dengan bentuk Pygame."""
    def scaled(value):
        return int(value * scale)

    # Kaki.
    pygame.draw.ellipse(
        surface, (8, 17, 54),
        (x + scaled(14), y + scaled(73), scaled(22), scaled(12))
    )
    pygame.draw.ellipse(
        surface, (8, 17, 54),
        (x + scaled(43), y + scaled(73), scaled(22), scaled(12))
    )
    pygame.draw.rect(
        surface, (226, 243, 255),
        (x + scaled(17), y + scaled(62), scaled(17), scaled(18)),
        border_radius=scaled(7),
    )
    pygame.draw.rect(
        surface, (226, 243, 255),
        (x + scaled(45), y + scaled(62), scaled(17), scaled(18)),
        border_radius=scaled(7),
    )

    # Badan.
    body_rect = pygame.Rect(
        x + scaled(18), y + scaled(39), scaled(43), scaled(34)
    )
    pygame.draw.rect(surface, (225, 242, 255), body_rect, border_radius=scaled(12))
    pygame.draw.rect(
        surface, (100, 190, 255), body_rect, width=max(1, scaled(2)),
        border_radius=scaled(12)
    )

    # Panel dada.
    chest = [
        (x + scaled(39), y + scaled(48)),
        (x + scaled(49), y + scaled(58)),
        (x + scaled(39), y + scaled(67)),
        (x + scaled(29), y + scaled(58)),
    ]
    pygame.draw.polygon(surface, (44, 215, 224), chest)
    pygame.draw.polygon(surface, WHITE, chest, max(1, scaled(2)))

    # Lengan.
    pygame.draw.line(
        surface, (225, 242, 255),
        (x + scaled(20), y + scaled(47)),
        (x + scaled(8), y + scaled(61)),
        max(3, scaled(8)),
    )
    pygame.draw.circle(
        surface, (255, 181, 95),
        (x + scaled(8), y + scaled(62)), max(3, scaled(6))
    )
    pygame.draw.line(
        surface, (225, 242, 255),
        (x + scaled(59), y + scaled(47)),
        (x + scaled(72), y + scaled(36)),
        max(3, scaled(8)),
    )
    pygame.draw.circle(
        surface, (255, 181, 95),
        (x + scaled(73), y + scaled(35)), max(3, scaled(6))
    )

    # Kepala dan visor.
    head_rect = pygame.Rect(
        x + scaled(9), y, scaled(62), scaled(48)
    )
    pygame.draw.rect(surface, (235, 247, 255), head_rect, border_radius=scaled(17))
    pygame.draw.rect(
        surface, (89, 177, 255), head_rect,
        width=max(1, scaled(3)), border_radius=scaled(17)
    )

    visor_rect = pygame.Rect(
        x + scaled(17), y + scaled(10), scaled(46), scaled(29)
    )
    pygame.draw.rect(surface, (12, 28, 75), visor_rect, border_radius=scaled(11))

    # Mata robot.
    pygame.draw.arc(
        surface, (57, 230, 255),
        (x + scaled(25), y + scaled(17), scaled(12), scaled(12)),
        math.radians(10), math.radians(170), max(2, scaled(3))
    )
    pygame.draw.arc(
        surface, (57, 230, 255),
        (x + scaled(44), y + scaled(17), scaled(12), scaled(12)),
        math.radians(10), math.radians(170), max(2, scaled(3))
    )

    # Antena kecil.
    pygame.draw.line(
        surface, (225, 242, 255),
        (x + scaled(40), y),
        (x + scaled(40), y - scaled(8)),
        max(1, scaled(2)),
    )
    pygame.draw.circle(
        surface, (255, 190, 86),
        (x + scaled(40), y - scaled(9)), max(2, scaled(4))
    )


def draw_star(surface, center, outer_radius, color):
    """Ikon bintang untuk panel skor."""
    x, y = center
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer_radius if i % 2 == 0 else outer_radius * 0.45
        points.append((
            int(x + math.cos(angle) * radius),
            int(y + math.sin(angle) * radius),
        ))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 239, 175), points, 2)


def draw_heart(surface, center, size, color):
    """Ikon hati untuk indikator nyawa."""
    x, y = center
    r = size * 0.34

    pygame.draw.circle(surface, color, (int(x - r * 0.72), int(y - r * 0.45)), int(r))
    pygame.draw.circle(surface, color, (int(x + r * 0.72), int(y - r * 0.45)), int(r))

    points = [
        (int(x - r * 1.55), int(y - r * 0.2)),
        (int(x + r * 1.55), int(y - r * 0.2)),
        (int(x), int(y + r * 1.65)),
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 220, 238), points, 2)


def draw_decorations(surface):
    """Dekorasi latar yang tidak mengganggu area permainan."""
    # Planet kecil di sisi kanan.
    draw_planet(surface, (835, 490), 45, (64, 100, 194), (232, 173, 255))

    # Bulan kecil di pojok kiri atas.
    pygame.draw.circle(surface, (88, 119, 204), (12, 155), 42)
    pygame.draw.circle(surface, (124, 151, 226), (-4, 140), 25)

    # Awan di bawah.
    draw_cloud(surface, -18, 625, 1.1)
    draw_cloud(surface, 780, 630, 1.0)

    # Kristal di kanan bawah dan robot maskot di kiri bawah.
    draw_crystals(surface, 812, 635, 1.0)
    draw_robot(surface, 28, 566, 0.88)


# ============================================================
# Class Striker / Paddle
# ============================================================

class Striker:
    def __init__(self, posx, posy, width, height, speed, color=WHITE):
        self.posx = float(posx)
        self.posy = float(posy)
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.strikerRect = pygame.Rect(
            int(self.posx), int(self.posy), self.width, self.height
        )

    def display(self):
        rect = self.strikerRect

        # Bayangan.
        shadow = rect.move(0, 5)
        pygame.draw.rect(screen, (9, 17, 58), shadow, border_radius=12)

        # Badan paddle.
        pygame.draw.rect(
            screen, (220, 239, 255), rect, border_radius=12
        )
        pygame.draw.rect(
            screen, (81, 177, 255), rect, width=3, border_radius=12
        )

        # Ujung oranye.
        pygame.draw.rect(
            screen, (255, 174, 75),
            (rect.left, rect.top, 19, rect.height),
            border_radius=9,
        )
        pygame.draw.rect(
            screen, (255, 174, 75),
            (rect.right - 19, rect.top, 19, rect.height),
            border_radius=9,
        )

        # Garis energi di tengah paddle.
        center_rect = pygame.Rect(
            rect.centerx - 34, rect.centery - 4, 68, 8
        )
        pygame.draw.rect(
            screen, (52, 222, 255), center_rect, border_radius=5
        )
        pygame.draw.rect(
            screen, (210, 252, 255), center_rect, width=1, border_radius=5
        )

    def update(self, xFac):
        self.posx += self.speed * xFac
        self.posx = max(8, min(self.posx, WIDTH - self.width - 8))
        self.strikerRect.topleft = (round(self.posx), round(self.posy))

    def getRect(self):
        return self.strikerRect


# ============================================================
# Class Block / Gem
# ============================================================

class Block:
    def __init__(self, posx, posy, width, height, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.color = color

        # Balok lavender memiliki daya tahan dua kali benturan.
        self.health = 2 if color == GEM_COLORS[4] else 1
        self.maxHealth = self.health

        self.blockRect = pygame.Rect(
            self.posx, self.posy, self.width, self.height
        )

    def display(self):
        if self.health <= 0:
            return

        rect = self.blockRect
        color = self.color

        # Bentuk permata dengan sudut terpotong.
        points = [
            (rect.left + 10, rect.top),
            (rect.right - 10, rect.top),
            (rect.right, rect.centery),
            (rect.right - 10, rect.bottom),
            (rect.left + 10, rect.bottom),
            (rect.left, rect.centery),
        ]

        # Sedikit redup jika membutuhkan dua kali benturan dan sudah terkena.
        if self.health < self.maxHealth:
            color = tuple(max(0, int(c * 0.68)) for c in color)

        pygame.draw.polygon(screen, (8, 18, 65), [
            (px + 2, py + 4) for px, py in points
        ])
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(
            screen, adjust_color(color, 55), points, 2
        )

        # Bidang kilau di bagian atas permata.
        top_facet = [
            (rect.left + 10, rect.top + 2),
            (rect.right - 10, rect.top + 2),
            (rect.centerx, rect.centery),
        ]
        pygame.draw.polygon(
            screen, adjust_color(color, 35), top_facet
        )

        # Garis facet kiri dan kanan.
        pygame.draw.line(
            screen, adjust_color(color, 70),
            (rect.left + 10, rect.top + 3),
            (rect.centerx, rect.centery),
            2,
        )
        pygame.draw.line(
            screen, adjust_color(color, 35),
            (rect.right - 10, rect.top + 3),
            (rect.centerx, rect.centery),
            2,
        )

        # Kilau kecil di tengah.
        shine_x, shine_y = rect.center
        pygame.draw.line(
            screen, (255, 255, 255),
            (shine_x - 5, shine_y), (shine_x + 5, shine_y), 2
        )
        pygame.draw.line(
            screen, (255, 255, 255),
            (shine_x, shine_y - 5), (shine_x, shine_y + 5), 2
        )

    def hit(self):
        self.health -= 1

    def getRect(self):
        return self.blockRect

    def getHealth(self):
        return self.health


# ============================================================
# Class Ball
# ============================================================

class Ball:
    def __init__(self, posx, posy, radius, speed, color=WHITE):
        self.posx = float(posx)
        self.posy = float(posy)
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 0.34
        self.yFac = -0.94
        self.previousX = self.posx
        self.previousY = self.posy
        self.trail = []

    def display(self):
        # Jejak bola.
        for index, (tx, ty) in enumerate(self.trail):
            alpha_radius = max(2, int(self.radius * (index + 1) / 7))
            pygame.draw.circle(
                screen, (62, 173, 255),
                (round(tx), round(ty)), alpha_radius
            )

        # Glow tipis.
        pygame.draw.circle(
            screen, (65, 176, 255),
            (round(self.posx), round(self.posy)),
            self.radius + 5
        )
        pygame.draw.circle(
            screen, (218, 250, 255),
            (round(self.posx), round(self.posy)),
            self.radius + 2
        )
        pygame.draw.circle(
            screen, WHITE,
            (round(self.posx), round(self.posy)),
            self.radius
        )

    def getRect(self):
        diameter = self.radius * 2
        return pygame.Rect(
            round(self.posx - self.radius),
            round(self.posy - self.radius),
            diameter,
            diameter,
        )

    def update(self):
        self.previousX = self.posx
        self.previousY = self.posy

        self.trail.append((self.posx, self.posy))
        if len(self.trail) > 7:
            self.trail.pop(0)

        self.posx += self.xFac * self.speed
        self.posy += self.yFac * self.speed

        # Pantulan dinding kiri dan kanan.
        if self.posx - self.radius <= 0:
            self.posx = self.radius
            self.xFac = abs(self.xFac)
        elif self.posx + self.radius >= WIDTH:
            self.posx = WIDTH - self.radius
            self.xFac = -abs(self.xFac)

        # Pantulan dinding atas.
        if self.posy - self.radius <= 0:
            self.posy = self.radius
            self.yFac = abs(self.yFac)

        # Bola hilang jika melewati bagian bawah layar.
        return self.posy - self.radius > HEIGHT

    def reset(self, striker):
        self.posx = striker.posx + striker.width / 2
        self.posy = striker.posy - self.radius - 2
        self.xFac = 0.30
        self.yFac = -0.95
        self.previousX = self.posx
        self.previousY = self.posy
        self.trail.clear()

    def bounceFromStriker(self, striker):
        offset = (
            self.posx - striker.strikerRect.centerx
        ) / (striker.width / 2)

        self.xFac = max(-0.82, min(0.82, offset))
        self.yFac = -math.sqrt(max(0.25, 1 - self.xFac ** 2))

        self.posy = striker.strikerRect.top - self.radius - 1

    def hitVertical(self):
        self.yFac *= -1

    def hitHorizontal(self):
        self.xFac *= -1


# ============================================================
# Fungsi permainan
# ============================================================

def collisionChecker(rect, ballRect):
    return rect.colliderect(ballRect)


def populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap):
    listOfBlocks = []

    columns = 10
    rows = 5
    total_width = columns * blockWidth + (columns - 1) * horizontalGap
    start_x = (WIDTH - total_width) // 2
    start_y = 160

    for row in range(rows):
        for column in range(columns):
            x = start_x + column * (blockWidth + horizontalGap)
            y = start_y + row * (blockHeight + verticalGap)

            # Pola warna berulang agar susunan terlihat teratur.
            color_index = (column + row * 2) % len(GEM_COLORS)
            color = GEM_COLORS[color_index]

            listOfBlocks.append(
                Block(x, y, blockWidth, blockHeight, color)
            )

    return listOfBlocks


def draw_hud(score, lives):
    # Panel skor.
    score_panel = pygame.Rect(24, 30, 220, 66)
    pygame.draw.rect(
        screen, (8, 20, 73), score_panel, border_radius=18
    )
    pygame.draw.rect(
        screen, PANEL_EDGE, score_panel, width=3, border_radius=18
    )
    draw_star(screen, (59, 63), 21, GOLD)

    score_label = font_medium.render("Score:", True, WHITE)
    screen.blit(score_label, (91, 45))

    score_value = font_medium.render(str(score), True, GOLD)
    screen.blit(score_value, (170, 45))

    # Panel nyawa.
    lives_panel = pygame.Rect(WIDTH - 244, 30, 220, 66)
    pygame.draw.rect(
        screen, (8, 20, 73), lives_panel, border_radius=18
    )
    pygame.draw.rect(
        screen, PANEL_EDGE, lives_panel, width=3, border_radius=18
    )

    lives_label = font_medium.render("Lives:", True, WHITE)
    screen.blit(lives_label, (lives_panel.x + 17, 45))

    for i in range(3):
        heart_color = PINK if i < lives else (74, 78, 126)
        draw_heart(
            screen,
            (lives_panel.x + 119 + i * 31, 63),
            19,
            heart_color,
        )


def draw_logo():
    """Judul dua warna seperti referensi."""
    draw_text_center(
        screen, "Block", font_title, (93, 190, 255),
        (WIDTH // 2, 43), outline=(14, 54, 150)
    )
    draw_text_center(
        screen, "Breaker", font_subtitle, (255, 179, 69),
        (WIDTH // 2, 82), outline=(135, 58, 28)
    )


def draw_game_scene(score, lives, striker, ball, blocks):
    screen.blit(BACKGROUND, (0, 0))
    draw_decorations(screen)
    draw_logo()
    draw_hud(score, lives)

    for block in blocks:
        block.display()

    striker.display()
    ball.display()


def draw_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((4, 8, 35, 190))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(205, 235, 490, 205)
    pygame.draw.rect(screen, (17, 31, 91), panel, border_radius=24)
    pygame.draw.rect(screen, PANEL_EDGE, panel, width=3, border_radius=24)

    draw_text_center(
        screen, "GAME OVER", font_title, (255, 125, 177),
        (WIDTH // 2, 285), outline=(84, 31, 111)
    )
    draw_text_center(
        screen, f"Final Score: {score}", font_medium, WHITE,
        (WIDTH // 2, 345)
    )
    draw_text_center(
        screen, "SPACE: Play Again     ESC: Exit",
        font_small, (190, 231, 255),
        (WIDTH // 2, 395)
    )


def handle_block_collision(ball, block):
    """Menentukan arah pantulan berdasarkan sisi balok yang terkena."""
    previous_rect = pygame.Rect(
        round(ball.previousX - ball.radius),
        round(ball.previousY - ball.radius),
        ball.radius * 2,
        ball.radius * 2,
    )
    block_rect = block.getRect()

    if previous_rect.bottom <= block_rect.top:
        ball.posy = block_rect.top - ball.radius - 1
        ball.hitVertical()
    elif previous_rect.top >= block_rect.bottom:
        ball.posy = block_rect.bottom + ball.radius + 1
        ball.hitVertical()
    elif previous_rect.right <= block_rect.left:
        ball.posx = block_rect.left - ball.radius - 1
        ball.hitHorizontal()
    elif previous_rect.left >= block_rect.right:
        ball.posx = block_rect.right + ball.radius + 1
        ball.hitHorizontal()
    else:
        # Fallback jika bola masuk ke sisi balok pada sudut tertentu.
        ball.hitVertical()


def gameOver(score):
    """Menunggu SPACE untuk restart atau ESC untuk keluar."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        screen.blit(BACKGROUND, (0, 0))
        draw_decorations(screen)
        draw_logo()
        draw_game_over(score)

        pygame.display.flip()
        clock.tick(FPS)


# ============================================================
# Main game loop
# ============================================================

def main():
    running = True

    blockWidth = 72
    blockHeight = 32
    horizontalGap = 12
    verticalGap = 10

    while running:
        # Inisialisasi setiap sesi permainan.
        lives = 3
        score = 0

        striker = Striker(
            WIDTH // 2 - 65,
            HEIGHT - 66,
            130,
            25,
            8,
        )

        ball = Ball(
            WIDTH // 2,
            HEIGHT - 95,
            9,
            5.4,
        )

        listOfBlocks = populateBlocks(
            blockWidth,
            blockHeight,
            horizontalGap,
            verticalGap,
        )

        pressed_keys = set()
        game_running = True

        while running and game_running:
            clock.tick(FPS)

            # ------------------------
            # Event handling
            # ------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        pressed_keys.add(event.key)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        pressed_keys.add(event.key)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        game_running = False

                elif event.type == pygame.KEYUP:
                    pressed_keys.discard(event.key)

            if not running:
                break

            # Gerakkan paddle berdasarkan tombol yang ditekan.
            move_left = (
                pygame.K_LEFT in pressed_keys or pygame.K_a in pressed_keys
            )
            move_right = (
                pygame.K_RIGHT in pressed_keys or pygame.K_d in pressed_keys
            )
            strikerXFac = int(move_right) - int(move_left)

            # ------------------------
            # Update objek
            # ------------------------
            striker.update(strikerXFac)
            lifeLost = ball.update()

            if lifeLost:
                lives -= 1

                if lives > 0:
                    ball.reset(striker)
                else:
                    restart = gameOver(score)
                    if restart:
                        game_running = False
                    else:
                        running = False
                    continue

            # Tabrakan bola dengan paddle.
            if (
                ball.yFac > 0
                and collisionChecker(striker.getRect(), ball.getRect())
            ):
                ball.bounceFromStriker(striker)

            # Tabrakan bola dengan permata.
            for block in listOfBlocks[:]:
                if collisionChecker(block.getRect(), ball.getRect()):
                    handle_block_collision(ball, block)
                    block.hit()

                    if block.getHealth() <= 0:
                        listOfBlocks.remove(block)
                        score += 5

                    # Satu tabrakan diproses per frame.
                    break

            # Jika semua permata hancur, susun kembali.
            if not listOfBlocks:
                listOfBlocks = populateBlocks(
                    blockWidth,
                    blockHeight,
                    horizontalGap,
                    verticalGap,
                )

            # ------------------------
            # Render
            # ------------------------
            draw_game_scene(
                score,
                lives,
                striker,
                ball,
                listOfBlocks,
            )
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
