"""İman kelimesinin sesleri — 3Blue1Brown tarzı Manim animasyonu.

Her sahne `narration.py` içindeki satırları seslendirir; animasyon süreleri
`audio/durations.json` içindeki gerçek ses sürelerine göre ayarlanır.
"""
import json
import os

import numpy as np
from manim import *

from narration import SCENES

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ROOT, "audio")
CUES = os.path.join(ROOT, "media", "cues")
with open(os.path.join(AUDIO, "durations.json")) as f:
    DURS = json.load(f)

# ---------------------------------------------------------------- stil
BG = "#101217"
HEMZE = "#F7D96F"   # sarı  — güç, başlangıç
MIM = "#5CD0B3"     # turkuaz — güven, toparlanma
NUN = "#58C4DD"     # mavi  — süreklilik
WARN = "#FC6255"
DIM = "#6B6F7A"
WALL = "#8A8F9C"
LIP = "#E3A3A3"
LATIN = "CMU Serif"
ARABIC = "Amiri"


def tr(s, size=40, color=WHITE, **kw):
    return Text(s, font=LATIN, font_size=size, color=color, **kw)


def ar(s, size=90, color=WHITE):
    # LRM işaretleri: Pango kısa sağdan-sola metinleri tuvalin dışına yerleştirip boş SVG üretebiliyor.
    return Text("\u200e" + s + "\u200e", font=ARABIC, font_size=size, color=color)


def check_mark(color=GREEN_C, size=0.35):
    return VMobject(stroke_color=color, stroke_width=6).set_points_as_corners(
        [[-0.5, 0, 0], [-0.1, -0.4, 0], [0.6, 0.45, 0]]
    ).scale(size)


def tile(letter, color, name=None, w=1.25, h=1.45, size=80):
    box = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color,
                           stroke_width=3, fill_color=color, fill_opacity=0.08)
    g = VGroup(box, ar(letter, size, color).move_to(box))
    if name:
        g.add(tr(name, 28, color).next_to(box, DOWN, buff=0.18))
    return g


def root_tiles(**kw):
    """أ م ن — sağdan sola dizilmiş kök harfleri."""
    t = VGroup(tile("أ", HEMZE, "hemze", **kw), tile("م", MIM, "mîm", **kw), tile("ن", NUN, "nûn", **kw))
    return t.arrange(LEFT, buff=0.35, aligned_edge=UP)


def top_tiles(focus=None):
    t = root_tiles(w=0.95, h=1.05, size=58).scale(0.85).to_edge(UP, buff=0.3)
    for i, g in enumerate(t):
        g[2].scale(0.85, about_edge=UP)
        if focus is not None and i != focus:
            g.set_opacity(0.25)
        if focus == i:
            g[0].set_fill(opacity=0.2)
    return t


def focus_anims(tiles, i):
    anims = []
    for j, g in enumerate(tiles):
        anims.append(g.animate.set_opacity(1.0 if j == i else 0.25))
    return anims


def wave(func, width=4.0, height=1.6, color=WHITE, stroke=3):
    return ParametricFunction(lambda t: np.array([(t - 0.5) * width, func(t) * height / 2, 0]),
                              t_range=[0, 1, 0.0015], color=color, stroke_width=stroke)


def elif_wave(t):
    return 0.32 * np.sin(2 * PI * 4 * t) * np.sin(PI * t) ** 1.5


def hemze_wave(t):
    s = t - 0.3
    return 0.0 if s < 0 else 1.0 * np.exp(-s * 7) * np.sin(2 * PI * 10 * s)


def nun_wave(t):
    return 0.55 * (1 - np.exp(-t * 18)) * (0.85 + 0.15 * np.sin(2 * PI * 1.5 * t)) * np.sin(2 * PI * 9 * t)


def cut_wave(t):
    return 0.0 if t > 0.32 else 0.55 * (1 - np.exp(-t * 18)) * np.sin(2 * PI * 9 * t)


def roots(origin, depth=5, length=0.85, seed=3, color=NUN):
    rng = np.random.default_rng(seed)
    levels = [[] for _ in range(depth)]

    def rec(p, ang, length, d):
        if d == 0:
            return
        q = p + length * np.array([np.cos(ang), np.sin(ang), 0])
        levels[depth - d].append(Line(p, q, stroke_width=0.8 + 1.1 * d, color=color))
        n = 2 if d > 1 else 1
        for k in ([-1, 1] if n == 2 else [0]):
            rec(q, ang + k * rng.uniform(0.25, 0.6) + rng.normal(0, 0.08), length * rng.uniform(0.62, 0.78), d - 1)

    rec(origin, -PI / 2, length, depth)
    return [VGroup(*lv) for lv in levels]


# ---------------------------------------------------------- ses yolu şeması
class VocalTract(VGroup):
    """Boğaz → ağız (dudaklar) ve boğaz → geniz kanallarının sade bir şeması."""

    W = 38  # kanal genişliği (stroke)

    def __init__(self, labels=True, **kw):
        super().__init__(**kw)
        x0 = -1.5
        G = np.array([x0, -2.3, 0])
        J = np.array([x0, 0.0, 0])
        T = np.array([x0, 1.2, 0])
        self.glottis = G
        pharynx = Line(G, T)
        oral = VMobject()
        oral.append_points(CubicBezier(J, J + UP * 0.45, [x0 + 0.15, 0.6, 0], [x0 + 0.6, 0.6, 0]).points)
        oral.append_points(Line([x0 + 0.6, 0.6, 0], [1.55, 0.6, 0]).points)
        nasal = VMobject()
        nasal.append_points(CubicBezier(T, T + UP * 0.45, [x0 + 0.15, 1.8, 0], [x0 + 0.6, 1.8, 0]).points)
        nasal.append_points(Line([x0 + 0.6, 1.8, 0], [1.2, 1.8, 0]).points)
        nasal.append_points(CubicBezier([1.2, 1.8, 0], [1.55, 1.8, 0], [1.7, 1.65, 0], [1.75, 1.32, 0]).points)
        self._origin = G
        paths = [pharynx, oral, nasal]
        self.outer = VGroup(*[p.copy().set_stroke(WALL, self.W + 7) for p in paths])
        self.phar_in, self.oral_in, self.nasal_in = [p.copy().set_stroke(BG, self.W) for p in paths]
        # boğaz kanalı en üstte çizilir ki kavşaklarda renk kesintisiz olsun
        self.inner = VGroup(self.oral_in, self.nasal_in, self.phar_in)
        self.folds = Line(G + LEFT * 0.2, G + RIGHT * 0.2, stroke_color=WALL, stroke_width=7)
        self.upper_lip = Ellipse(width=0.26, height=0.38, fill_color=LIP, fill_opacity=1,
                                 stroke_width=0).move_to([1.72, 0.98, 0])
        self.lower_lip = self.upper_lip.copy().move_to([1.72, 0.22, 0])
        self.add(self.outer, self.inner, self.folds, self.upper_lip, self.lower_lip)

        # akış yolları (parçacık animasyonu için)
        self.flow_nasal = VMobject()
        self.flow_nasal.append_points(Line(G + UP * 0.05, T).points)
        self.flow_nasal.append_points(nasal.points)
        self.flow_oral = VMobject()
        self.flow_oral.append_points(Line(G + UP * 0.05, J).points)
        self.flow_oral.append_points(oral.points)
        self.flow_nasal.set_stroke(opacity=0)
        self.flow_oral.set_stroke(opacity=0)
        self.add(self.flow_nasal, self.flow_oral)

        self.labels = VGroup(
            tr("boğaz", 26, GREY_B).next_to(G, RIGHT, buff=0.45).shift(UP * 0.1),
            tr("dudaklar", 26, GREY_B).next_to([1.85, 0.6, 0], RIGHT, buff=0.15),
            tr("geniz", 26, GREY_B).next_to([0.0, 1.8, 0], UP, buff=0.32),
        )
        if labels:
            self.add(self.labels)

    def at(self, p):
        """Şemanın ilk koordinatlarındaki bir noktayı, kaydırılmış şemadaki yerine çevirir."""
        return np.array(p, dtype=float) - self._origin + self.folds.get_center()

    @property
    def oral_center(self):
        return self.at([0.4, 0.6, 0])

    def close_lips(self):
        return [self.upper_lip.animate.move_to(self.at([1.72, 0.79, 0])),
                self.lower_lip.animate.move_to(self.at([1.72, 0.41, 0]))]

    def closed(self):
        self.upper_lip.move_to(self.at([1.72, 0.79, 0]))
        self.lower_lip.move_to(self.at([1.72, 0.41, 0]))
        return self

    @property
    def glottis_point(self):
        return self.folds.get_center()

    @property
    def lips(self):
        return VGroup(self.upper_lip, self.lower_lip)

    def nostril_point(self):
        return self.flow_nasal.get_end()

    def oral_points(self):
        return self.flow_oral


def draw_tract(t, run_time=1.5):
    return AnimationGroup(
        Create(t.outer, lag_ratio=0), Create(t.inner, lag_ratio=0), FadeIn(t.folds),
        FadeIn(t.upper_lip), FadeIn(t.lower_lip), FadeIn(t.labels, lag_ratio=0.2),
        run_time=run_time,
    )


def nasal_ripples(point, n=4, color=NUN):
    arcs = []
    for i in range(n):
        a = Arc(radius=0.18, start_angle=-PI / 4 - 0.7, angle=1.4, arc_center=point,
                color=color, stroke_width=4)
        arcs.append(a)
    return arcs


# ------------------------------------------------------------- temel sahne
class Narrated(Scene):
    key = ""

    def setup(self):
        self.camera.background_color = BG
        self._end = 0.0
        self.cues = []

    def now(self):
        return self.renderer.time

    def say(self, k):
        name = f"{self.key}__{k}"
        self.add_sound(os.path.join(AUDIO, name + ".wav"))
        start = self.now()
        self._end = start + DURS[name]
        self.cues.append((k, start, self._end))
        return DURS[name]

    def until(self, t_from_start):
        """Mevcut satırın başlangıcından `t` saniye sonrasına kadar bekle."""
        start = self.cues[-1][1]
        dt = start + t_from_start - self.now()
        if dt > 0.02:
            self.wait(dt)

    def rest(self, gap=0.45):
        dt = self._end - self.now() + gap
        if dt > 0.02:
            self.wait(dt)

    def tear_down(self):
        os.makedirs(CUES, exist_ok=True)
        texts = dict(SCENES[self.key])
        with open(os.path.join(CUES, self.key + ".json"), "w") as f:
            json.dump({"duration": self.now(),
                       "cues": [{"text": texts[k], "start": s, "end": e} for k, s, e in self.cues]},
                      f, ensure_ascii=False, indent=1)


def header_pair():
    left = VGroup(ar("ا", 130, WHITE), tr("elif", 40, GREY_A)).arrange(DOWN, buff=0.15).move_to([-3.6, 2.2, 0])
    right = VGroup(ar("ء", 130, HEMZE), tr("hemze", 40, HEMZE)).arrange(DOWN, buff=0.15).move_to([3.6, 2.2, 0])
    right.align_to(left, UP)
    neq = tr("≠", 72, GREY_B).move_to([0, left[0].get_center()[1], 0])
    return left, neq, right


# ================================================================ SAHNELER
class S01_Duzeltme(Narrated):
    key = "S01_Duzeltme"

    def construct(self):
        word = ar("إِيمَان", 190)
        latin = tr("iman", 44, GREY_A).next_to(word, DOWN, buff=0.25)
        self.wait(0.4)
        self.say("intro")
        self.play(Write(word, run_time=2.2))
        self.play(FadeIn(latin, shift=UP * 0.2), run_time=0.8)
        self.rest(0.2)

        title = VGroup(word, latin)
        self.play(title.animate.scale(0.45).to_edge(UP, buff=0.35), run_time=0.9)

        # Kök: elif, mîm, nûn değil → hemze, mîm, nûn
        wrong = VGroup(tile("ا", WHITE), tile("م", MIM), tile("ن", NUN)).arrange(LEFT, buff=0.35).shift(UP * 0.3)
        right = root_tiles().shift(UP * 0.3)
        right.align_to(wrong, UP)
        kok = tr("kök", 30, GREY_B).next_to(wrong, LEFT, buff=0.5)
        self.say("kok")
        self.wait(0.5)
        self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.2) for g in wrong], lag_ratio=0.25),
                  FadeIn(kok), run_time=1.2)
        cross = Cross(wrong[0], stroke_color=WARN, stroke_width=7, scale_factor=0.85)
        self.play(Create(cross), run_time=0.4)
        self.play(FadeOut(cross), ReplacementTransform(wrong[0], VGroup(*right[0][:2])), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(g[2], shift=UP * 0.15) for g in right], lag_ratio=0.2), run_time=0.8)
        self.remove(*wrong)
        self.add(right)
        self.rest()

        # Kök anlamı değişmiyor
        meaning = tr("kök anlamı:  güven · emniyet", 36, GREY_A).next_to(right, DOWN, buff=0.7)
        ok = check_mark().next_to(meaning, RIGHT, buff=0.35)
        self.say("anlam")
        self.play(FadeIn(meaning, shift=UP * 0.2), run_time=0.9)
        self.until(2.0)
        self.play(Create(ok), run_time=0.6)
        self.rest()

        # Fonetik bakışta elif ile hemze farkı önem kazanıyor
        self.say("fakat")
        ear = VGroup(*[Arc(radius=r, start_angle=-0.7, angle=1.4, stroke_width=4, color=GREY_B)
                       for r in (0.25, 0.45, 0.65)]).next_to(meaning, DOWN, buff=0.5)
        fonetik = tr("fonetik", 32, GREY_B).next_to(ear, RIGHT, buff=0.25)
        self.play(FadeOut(ok), meaning.animate.set_opacity(0.4),
                  LaggedStart(*[Create(a) for a in ear], lag_ratio=0.3), FadeIn(fonetik), run_time=1.2)
        self.until(2.7)
        left, neq, rgt = header_pair()
        self.play(
            FadeOut(VGroup(title, kok, meaning, ear, fonetik, right[1], right[2], right[0][0], right[0][2])),
            FadeIn(left, shift=RIGHT * 0.3),
            ReplacementTransform(right[0][1], rgt[0]),
            FadeIn(rgt[1]),
            run_time=1.4,
        )
        self.play(Write(neq), run_time=0.6)
        self.rest(0.3)


class S02_ElifHemze(Narrated):
    key = "S02_ElifHemze"

    def construct(self):
        left, neq, right = header_pair()
        self.add(left, neq, right)
        base_l = Line([-5.8, -0.3, 0], [-1.4, -0.3, 0], stroke_color=DIM, stroke_width=1.5)
        base_r = base_l.copy().move_to([3.6, -0.3, 0])
        w_elif = wave(elif_wave, 4.2, 2.2, WHITE).shift([-3.6, -0.3, 0])
        w_hemze = wave(hemze_wave, 4.2, 2.2, HEMZE, stroke=3.5).shift([3.6, -0.3, 0])

        l_words = VGroup(*[tr(s, 32, GREY_A) for s in ("açık", "yumuşak", "zayıf")]).arrange(RIGHT, buff=0.5)
        l_words.move_to([-3.6, -2.1, 0])
        r_top = tr("boğazın en derin bölgesi", 30, HEMZE).move_to([3.6, -2.0, 0])
        r_words = VGroup(*[tr(s, 32, HEMZE) for s in ("keskin", "kuvvetli")]).arrange(RIGHT, buff=0.5)
        r_words.next_to(r_top, DOWN, buff=0.3)

        self.say("elif")
        self.play(Create(base_l), Create(w_elif, rate_func=linear), run_time=1.6)
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in l_words], lag_ratio=0.45), run_time=1.2)
        self.rest()

        self.say("hemze")
        self.play(FadeIn(r_top, shift=UP * 0.2), Create(base_r), run_time=0.9)
        self.until(1.4)
        self.play(Create(w_hemze, rate_func=linear), run_time=1.3)
        spike = w_hemze.point_from_proportion(0.33)
        self.play(Flash(spike, color=HEMZE, line_length=0.35, flash_radius=0.35), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in r_words], lag_ratio=0.4), run_time=0.9)
        self.rest(1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S03_IbnCinni(Narrated):
    key = "S03_IbnCinni"

    def construct(self):
        name_ar = ar("ابن جني", 96, GREY_A)
        name_tr = tr("İbn Cinnî", 56)
        name = VGroup(name_ar, name_tr).arrange(DOWN, buff=0.2)

        ses_c = Circle(radius=1.15, stroke_color=NUN, stroke_width=4, fill_color=NUN, fill_opacity=0.07)
        ses = VGroup(ses_c, tr("ses", 48, NUN)).move_to([-3.4, -0.2, 0])
        mana_c = Circle(radius=1.15, stroke_color=MIM, stroke_width=4, fill_color=MIM, fill_opacity=0.07)
        mana = VGroup(mana_c, tr("mana", 48, MIM)).move_to([3.4, -0.2, 0])
        link = DoubleArrow(ses_c.get_right(), mana_c.get_left(), buff=0.2, stroke_width=5,
                           color=GREY_B, tip_length=0.25)

        self.say("giris")
        self.play(FadeIn(name_ar, shift=DOWN * 0.2), Write(name_tr), run_time=1.6)
        self.play(name.animate.scale(0.6).to_edge(UP, buff=0.35), run_time=0.8)
        self.play(GrowFromCenter(ses), GrowFromCenter(mana), run_time=0.9)
        self.play(GrowFromCenter(link), run_time=0.7)
        self.rest()

        feats = VGroup(*[tr(s, 30, GREY_A) for s in ("çıkış yeri", "kuvvet", "telaffuz biçimi")])
        feats.arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(ses, DOWN, buff=0.4)
        anlam = tr("kelimenin anlamı", 30, GREY_A).next_to(mana, DOWN, buff=0.4)
        uyum = tr("uyum", 40, HEMZE).next_to(link, UP, buff=0.25)

        self.say("uyum")
        self.until(1.4)
        for i, t in enumerate((1.4, 2.4, 3.1)):
            self.until(t)
            self.play(FadeIn(feats[i], shift=RIGHT * 0.2), run_time=0.5)
        self.until(4.3)
        self.play(FadeIn(anlam, shift=LEFT * 0.2), Indicate(mana_c, color=MIM, scale_factor=1.05), run_time=0.8)
        self.until(5.3)
        self.play(link.animate.set_color(HEMZE), Write(uyum), run_time=0.9)
        self.rest(1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S04_Hemze(Narrated):
    key = "S04_Hemze"

    def construct(self):
        word = ar("إِيمَان", 170)
        tiles = top_tiles()
        self.say("bakalim")
        self.play(FadeIn(word, scale=0.9), run_time=1.0)
        self.play(ReplacementTransform(word, tiles), run_time=1.1)
        self.rest(0.2)

        self.say("ilk")
        self.play(*focus_anims(tiles, 0), tiles[0][0].animate.set_fill(opacity=0.2), run_time=0.8)
        self.rest(0.2)

        tract = VocalTract().shift(LEFT * 3.4 + DOWN * 0.75)
        self.say("guclu")
        self.play(draw_tract(tract, 1.4))
        gp = tract.glottis_point
        glow = VGroup(*[Dot(gp, radius=r, color=HEMZE).set_opacity(o) for r, o in ((0.32, 0.15), (0.2, 0.3), (0.1, 1))])
        self.play(FadeIn(glow, scale=0.5), tract.folds.animate.set_color(HEMZE),
                  tract.labels[0].animate.set_color(HEMZE), run_time=0.6)
        w = wave(hemze_wave, 4.4, 2.4, HEMZE, stroke=3.5).shift([3.0, -0.3, 0])
        base = Line([0.8, -0.3, 0], [5.2, -0.3, 0], stroke_color=DIM, stroke_width=1.5)
        self.play(Create(base), Create(w, rate_func=linear),
                  tract.phar_in.animate.set_stroke(interpolate_color(ManimColor(BG), ManimColor(HEMZE), 0.25)),
                  run_time=1.2)
        self.play(Flash(w.point_from_proportion(0.33), color=HEMZE, line_length=0.35, flash_radius=0.35),
                  Flash(gp, color=HEMZE, line_length=0.3, flash_radius=0.4), run_time=0.5)
        self.rest()

        # tasdik: silik ve pasif değil — güçlü ve kararlı bir başlangıç
        tasdik = tr("imandaki tasdik", 40).move_to([3.0, 1.0, 0])
        pasif = tr("silik, pasif bir kabul", 34, DIM).move_to([3.0, -0.3, 0])
        strike = Line(pasif.get_left() + LEFT * 0.1, pasif.get_right() + RIGHT * 0.1, stroke_color=WARN, stroke_width=5)
        guclu = tr("güçlü, kararlı bir başlangıç", 36, HEMZE).move_to([3.0, -1.5, 0])
        start_dot = Dot(color=HEMZE, radius=0.11).next_to(guclu, LEFT, buff=0.25)

        self.say("tasdik")
        self.play(FadeOut(VGroup(w, base)), run_time=0.6)
        self.play(FadeIn(tasdik, shift=DOWN * 0.2), run_time=0.7)
        self.until(1.9)
        self.play(FadeIn(pasif), run_time=0.7)
        self.until(3.6)
        self.play(Create(strike), run_time=0.5)
        self.until(4.3)
        self.play(FadeIn(guclu, shift=RIGHT * 0.3), GrowFromCenter(start_dot),
                  Flash(gp, color=HEMZE, line_length=0.3, flash_radius=0.4), run_time=0.9)
        self.play(Indicate(guclu, color=HEMZE, scale_factor=1.06), run_time=0.9)
        self.rest(0.9)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not tiles])), run_time=0.8)


class S05_IkiHemze(Narrated):
    key = "S05_IkiHemze"

    def construct(self):
        tiles = top_tiles(focus=0)
        self.add(tiles)
        big = root_tiles().move_to(UP * 0.6)

        self.say("ayrinti")
        self.play(ReplacementTransform(tiles, big), run_time=1.3)
        self.rest(0.1)

        self.say("zaten")
        self.play(Circumscribe(big[0][0], color=HEMZE, buff=0.12), run_time=1.2)
        self.rest(0.1)

        # if‘âl bâbı: bir hemze daha
        bab = tr("if‘âl bâbı", 40, GREY_A).to_edge(UP, buff=0.5)
        extra = tile("أ", HEMZE, "eklenen", w=1.25, h=1.45, size=80)
        extra[2].set_color(GREY_A)
        self.say("ifal")
        self.play(FadeIn(bab, shift=DOWN * 0.2), run_time=0.7)
        self.play(big.animate.shift(LEFT * 0.8), run_time=0.6)
        extra.next_to(big, RIGHT, buff=0.35).align_to(big, UP)
        start = extra.copy().shift(RIGHT * 3).set_opacity(0)
        self.play(Transform(start, extra), run_time=0.9)
        self.remove(start)
        self.add(extra)
        self.play(Flash(extra[0].get_center(), color=HEMZE, flash_radius=0.9, line_length=0.3), run_time=0.5)
        self.rest()

        # âmene = أَأْمَنَ
        written = ar("آمَنَ", 110)
        parts = VGroup(ar("مَنَ", 110), ar("أْ", 110, HEMZE), ar("أَ", 110, HEMZE)).arrange(RIGHT, buff=0.14, aligned_edge=DOWN)
        eq = tr("=", 64, GREY_B)
        row = VGroup(written, eq, parts).arrange(RIGHT, buff=0.7).move_to(DOWN * 2.2)
        parts[0].align_to(written, DOWN)
        lbl = tr("âmene", 30, GREY_A).next_to(written, DOWN, buff=0.1)
        two = tr("iki hemze", 30, HEMZE).next_to(parts, DOWN, buff=0.1)
        self.say("amene")
        self.play(FadeIn(written, shift=UP * 0.2), FadeIn(lbl), run_time=0.9)
        self.until(1.5)
        self.play(Write(eq), FadeIn(parts[0]), run_time=0.6)
        self.play(TransformFromCopy(big[0][1], parts[1]), TransformFromCopy(extra[1], parts[2]), run_time=0.9)
        self.play(FadeIn(two, shift=UP * 0.1), run_time=0.5)
        self.rest()

        # kuvvet katlanıyor
        keep = VGroup(big, extra, bab, row, lbl, two)
        self.say("kat")
        self.play(keep.animate.scale(0.7).to_edge(LEFT, buff=0.6), run_time=0.9)
        floor_y = -2.2
        bar1 = Rectangle(width=1.1, height=1.7, fill_color=HEMZE, fill_opacity=0.75, stroke_color=HEMZE)
        bar1.move_to([4.2, floor_y + 0.85, 0])
        bar2 = bar1.copy().next_to(bar1, UP, buff=0.06)
        ground = Line([3.0, floor_y, 0], [5.4, floor_y, 0], stroke_color=DIM)
        kuvvet = tr("kuvvet", 32, GREY_A).next_to(ground, DOWN, buff=0.25)
        times2 = tr("× 2", 54, HEMZE).next_to(VGroup(bar1, bar2), RIGHT, buff=0.4)
        self.play(Create(ground), FadeIn(kuvvet), GrowFromEdge(bar1, DOWN), run_time=1.0)
        self.until(2.6)
        self.play(GrowFromEdge(bar2, DOWN), run_time=0.9)
        self.until(3.9)
        self.play(Write(times2), Flash(bar2.get_top(), color=HEMZE, flash_radius=0.5), run_time=0.8)
        self.rest(1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S06_Mim(Narrated):
    key = "S06_Mim"

    def construct(self):
        tiles = top_tiles(focus=0)
        self.say("ikinci")
        self.play(FadeIn(tiles), run_time=0.5)
        self.play(*focus_anims(tiles, 1), tiles[1][0].animate.set_fill(opacity=0.2),
                  tiles[0][0].animate.set_fill(opacity=0.08), run_time=0.7)
        self.rest(0.2)

        tract = VocalTract().shift(LEFT * 3.4 + DOWN * 0.75)
        self.say("dudak")
        self.play(draw_tract(tract, 1.1))
        self.play(*tract.close_lips(), tract.labels[1].animate.set_color(MIM), run_time=0.6)
        rng = np.random.default_rng(1)
        oc = tract.oral_center
        dots = VGroup(*[Dot([oc[0] + rng.uniform(-1.3, 1.0), oc[1] + rng.uniform(-0.1, 0.1), 0],
                            radius=0.045, color=MIM) for _ in range(14)])
        self.play(FadeIn(dots, lag_ratio=0.1),
                  tract.oral_in.animate.set_stroke(interpolate_color(ManimColor(BG), ManimColor(MIM), 0.22)),
                  run_time=0.6)
        self.play(*[d.animate.move_to(oc + RIGHT * 0.6 + rng.normal(0, 0.05, 3) * [1, 1, 0]) for d in dots],
                  run_time=0.8)
        self.rest()

        # kökün güven ve emniyet anlamıyla uyum
        root_txt = ar("أ م ن", 100, MIM).move_to([3.0, 1.0, 0])
        arrow = Arrow([3.0, 0.2, 0], [3.0, -0.7, 0], color=GREY_B, buff=0)
        guven = tr("güven · emniyet", 44, MIM).move_to([3.0, -1.3, 0])
        kapanma = tr("kapanma · toparlanma", 26, GREY_A).next_to(tract.lips, DOWN, buff=0.6).align_to(tract.lips, RIGHT).shift(RIGHT * 0.5)
        self.say("emniyet")
        self.play(FadeIn(kapanma, shift=UP * 0.15), run_time=0.8)
        self.until(2.4)
        self.play(FadeIn(root_txt, shift=DOWN * 0.2), run_time=0.8)
        self.until(3.6)
        self.play(GrowArrow(arrow), FadeIn(guven, shift=DOWN * 0.2), run_time=0.9)
        self.until(5.2)
        link = DashedLine(kapanma.get_right() + RIGHT * 0.1, guven.get_left() + LEFT * 0.1, color=MIM, dash_length=0.1)
        self.play(Create(link), Indicate(guven, color=MIM, scale_factor=1.05), run_time=1.0)
        self.rest()

        # insan güvene kavuşunca güvenli bir alana sığınır
        self.say("siginma")
        self.play(FadeOut(VGroup(tract, dots, root_txt, arrow, guven, kapanma, link)), run_time=0.6)
        safe = Circle(radius=1.5, stroke_color=MIM, stroke_width=5, fill_color=MIM, fill_opacity=0.08).move_to([2.6, -0.4, 0])
        person = Dot([-3.2, -0.4, 0], radius=0.14, color=WHITE)
        self.play(Create(safe), GrowFromCenter(person), run_time=0.8)
        threats = VGroup(
            tr("korku", 34, WARN).move_to([-4.6, 0.7, 0]),
            tr("şüphe", 34, WARN).move_to([-1.9, 0.9, 0]),
            tr("zarar", 34, WARN).move_to([-3.4, -1.8, 0]),
        )
        for i, t in enumerate((1.7, 2.5, 3.4)):
            self.until(t)
            self.play(FadeIn(threats[i], scale=1.2), person.animate.shift(rng.normal(0, 0.06, 3) * [1, 1, 0]), run_time=0.45)
        self.until(4.9)
        self.play(
            person.animate.move_to(safe.get_center()),
            *[t.animate.shift((t.get_center() - person.get_center()) * 0.6).set_opacity(0) for t in threats],
            run_time=1.6,
        )
        self.play(safe.animate.set_fill(opacity=0.18), Flash(safe.get_center(), color=MIM, flash_radius=1.7, line_length=0.3), run_time=0.8)
        self.rest()

        # mîm sesi dışarıdan içeriye topluyor
        self.say("muhafaza")
        c = safe.get_center()
        parts = VGroup()
        for i in range(36):
            ang = TAU * i / 36 + rng.uniform(-0.1, 0.1)
            r = rng.uniform(3.0, 4.2)
            parts.add(Dot(c + r * np.array([np.cos(ang), np.sin(ang), 0]), radius=0.05, color=MIM))
        self.play(FadeIn(parts, lag_ratio=0.02), run_time=0.6)
        self.play(*[p.animate.move_to(c + rng.uniform(0.25, 1.2) * normalize(p.get_center() - c)) for p in parts],
                  run_time=2.0, rate_func=smooth)
        guvenli = tr("güvenli alan", 34, MIM).next_to(safe, DOWN, buff=0.3)
        self.play(safe.animate.set_stroke(width=9), FadeIn(guvenli, shift=UP * 0.15), run_time=0.8)
        self.rest(1.0)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not tiles])), run_time=0.8)


class S07_Nun(Narrated):
    key = "S07_Nun"

    def construct(self):
        tiles = top_tiles(focus=1)
        self.add(tiles)
        self.say("son")
        self.play(*focus_anims(tiles, 2), tiles[2][0].animate.set_fill(opacity=0.2),
                  tiles[1][0].animate.set_fill(opacity=0.08), run_time=0.8)
        self.rest(0.2)

        who = tr("İbn Cinnî'ye göre nûn:", 34, GREY_A)
        tags = VGroup(*[
            VGroup(RoundedRectangle(corner_radius=0.2, width=2.6, height=0.9, stroke_color=NUN, fill_color=NUN, fill_opacity=0.12),
                   tr(s, 40, NUN)) for s in ("cehrî", "gunneli")
        ])
        for g in tags:
            g[1].move_to(g[0])
        tags.arrange(RIGHT, buff=0.6)
        block = VGroup(who, tags).arrange(DOWN, buff=0.4)
        self.say("tanim")
        self.play(FadeIn(who), run_time=0.6)
        self.until(1.2)
        self.play(LaggedStart(*[GrowFromCenter(t) for t in tags], lag_ratio=0.5), run_time=1.2)
        self.rest()

        # genizde yankılanarak devam eder
        tract = VocalTract().closed().shift(LEFT * 3.4 + DOWN * 0.75)
        tract.labels[1].set_opacity(0)
        self.say("geniz")
        self.play(block.animate.scale(0.7).move_to([3.0, 1.6, 0]), draw_tract(tract, 1.0), run_time=1.0)
        flow = tract.flow_nasal
        movers = VGroup(*[Dot(radius=0.06, color=NUN).move_to(flow.get_start()) for _ in range(7)])
        self.add(movers)
        base = Line([0.8, -0.5, 0], [5.2, -0.5, 0], stroke_color=DIM, stroke_width=1.5)
        w_cut = wave(cut_wave, 4.4, 1.8, DIM, stroke=2).shift([3.0, -0.5, 0])
        w = wave(nun_wave, 4.4, 1.8, NUN, stroke=3.5).shift([3.0, -0.5, 0])
        self.play(
            LaggedStart(*[MoveAlongPath(m, flow, rate_func=linear) for m in movers], lag_ratio=0.18, run_time=2.4),
            tract.nasal_in.animate(run_time=1.6).set_stroke(interpolate_color(ManimColor(BG), ManimColor(NUN), 0.3)),
            tract.labels[2].animate(run_time=1.0).set_color(NUN),
            Create(base, run_time=0.6),
            Create(w, rate_func=linear, run_time=3.4),
        )
        ripples = nasal_ripples(tract.nostril_point())
        self.add(*ripples)
        self.play(
            LaggedStart(*[r.animate(rate_func=linear).scale(5, about_point=tract.nostril_point()).set_stroke(opacity=0)
                          for r in ripples], lag_ratio=0.3),
            FadeOut(movers, run_time=0.6),
            run_time=1.4,
        )
        self.remove(*ripples)
        self.rest(0.2)

        # anlık değil — yerleşen, kök salan, süreklilik kazanan
        self.say("kalici")
        self.play(FadeOut(VGroup(tract, block, base, w)), run_time=0.8)
        spark = Star(n=6, outer_radius=0.35, inner_radius=0.12, color=GREY_B, fill_opacity=0.8).move_to([-4.0, 0.3, 0])
        anlik = tr("bir anlık tasdik", 32, GREY_B).next_to(spark, DOWN, buff=0.35)
        self.until(1.9)
        self.play(GrowFromCenter(spark), FadeIn(anlik), run_time=0.5)
        self.play(spark.animate.scale(0.1).set_opacity(0), anlik.animate.set_opacity(0.35), run_time=1.1)
        strike = Line(anlik.get_left(), anlik.get_right(), stroke_color=WARN, stroke_width=4)
        self.play(Create(strike), run_time=0.4)

        ground_y = -0.2
        ground = Line([0.0, ground_y, 0], [5.6, ground_y, 0], stroke_color=DIM, stroke_width=2)
        seed = Dot([2.8, 1.8, 0], radius=0.14, color=NUN)
        glow = Dot([2.8, ground_y, 0], radius=0.3, color=NUN).set_opacity(0.25)
        labels = VGroup(*[tr(s, 32, NUN) for s in ("yerleşen", "kök salan", "süreklilik kazanan")])
        labels[0].move_to([4.9, 0.6, 0])
        labels[1].move_to([5.0, -1.4, 0])
        labels[2].move_to([2.8, -3.3, 0])
        self.until(4.3)
        self.play(Create(ground), FadeIn(seed), run_time=0.5)
        self.play(seed.animate.move_to([2.8, ground_y, 0]), FadeIn(labels[0], shift=LEFT * 0.2), run_time=0.8, rate_func=rush_into)
        self.add(glow, seed)
        lv = roots(np.array([2.8, ground_y, 0]), depth=5, length=0.75)
        self.until(5.7)
        self.play(LaggedStart(*[Create(g, lag_ratio=0) for g in lv], lag_ratio=1.0), FadeIn(labels[1], shift=LEFT * 0.2),
                  run_time=1.6, rate_func=linear)
        self.until(6.9)
        pulses = [Circle(radius=0.2, color=NUN, stroke_width=3).move_to(seed) for _ in range(3)]
        self.add(*pulses)
        self.play(
            LaggedStart(*[p.animate.scale(6).set_stroke(opacity=0) for p in pulses], lag_ratio=0.35),
            glow.animate.set_opacity(0.45).scale(1.4),
            FadeIn(labels[2], shift=UP * 0.2),
            run_time=2.0,
        )
        self.remove(*pulses)
        self.rest(1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.9)


class S08_Yolculuk(Narrated):
    key = "S08_Yolculuk"

    def construct(self):
        word = ar("إِيمَان", 90, GREY_A).to_edge(UP, buff=0.3)
        xs = [5.0, 2.0, -1.4, -4.6]
        path = VMobject(stroke_color=GREY_B, stroke_width=3)
        path.set_points_smoothly([[6.3, 0.4, 0], [5.0, 0.8, 0], [3.5, 0.3, 0], [2.0, 0.8, 0],
                                  [0.3, 0.3, 0], [-1.4, 0.8, 0], [-3.0, 0.3, 0], [-4.6, 0.8, 0]])
        tail = DashedLine([-4.6, 0.8, 0], [-6.6, 0.5, 0], color=NUN, dash_length=0.12)
        stops = []
        specs = [("ء", HEMZE, "güçlü bir\nbaşlangıç"),
                 ("ء", HEMZE, "kuvvetin\npekişmesi"),
                 ("م", MIM, "güvene sığınma\nve toparlanma"),
                 ("ن", NUN, "içte yerleşip\ndevam eden hâl")]
        for x, (letter, col, txt) in zip(xs, specs):
            p = np.array([x, 0.8, 0])
            dot = Dot(p, radius=0.13, color=col)
            ring = Circle(radius=0.26, color=col, stroke_width=3).move_to(p)
            let = ar(letter, 72, col).next_to(dot, UP, buff=0.35)
            lab = Text(txt, font=LATIN, font_size=28, color=col, line_spacing=0.8).next_to(dot, DOWN, buff=0.4)
            stops.append(VGroup(dot, ring, let, lab))
        stops[1][0].scale(1.25)
        stops[1][1].set_stroke(width=5)

        self.say("yolculuk")
        self.play(FadeIn(word), Create(path, rate_func=linear), run_time=2.4)
        self.rest(0.1)

        for i, k in enumerate(("y1", "y2", "y3", "y4")):
            self.say(k)
            s = stops[i]
            anims = [GrowFromCenter(s[0]), Create(s[1]), FadeIn(s[2], shift=DOWN * 0.2), FadeIn(s[3], shift=UP * 0.15)]
            if i == 1:
                anims.append(Flash(s[0].get_center(), color=HEMZE, flash_radius=0.45))
            if i == 3:
                anims.append(Create(tail))
            self.play(*anims, run_time=1.0)
            self.rest(0.2)

        journey = VGroup(word, path, tail, *stops)
        self.play(journey.animate.scale(0.8).shift(UP * 0.7), run_time=0.8)
        q = tr("iman ≠ yalnızca “inandım ve doğruluyorum” demek", 36, GREY_A).move_to(DOWN * 1.9)
        seq = VGroup(
            tr("güçlü bir tasdik", 34, HEMZE), tr("→", 34, GREY_B),
            tr("güven", 34, MIM), tr("→", 34, GREY_B),
            tr("içte yaşayan bir hâl", 34, NUN),
        ).arrange(RIGHT, buff=0.3).move_to(DOWN * 3.0)
        self.say("yani")
        self.play(FadeIn(q, shift=UP * 0.2), run_time=0.9)
        self.until(3.6)
        self.play(q.animate.set_opacity(0.45), FadeIn(seq[0], shift=RIGHT * 0.2), run_time=0.7)
        self.until(5.0)
        self.play(FadeIn(seq[1]), FadeIn(seq[2], shift=RIGHT * 0.2), run_time=0.6)
        self.until(6.0)
        self.play(FadeIn(seq[3]), FadeIn(seq[4], shift=RIGHT * 0.2), run_time=0.7)
        self.rest(1.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.9)


class S09_Not(Narrated):
    key = "S09_Not"

    def construct(self):
        lines = VGroup(
            tr("Not", 34, HEMZE),
            tr("Bu, harflerin sözlük anlamı değil;", 36),
            tr("İbn Cinnî'nin ses ile mana arasındaki ilişkiye dair", 36),
            tr("yaklaşımından hareketle yapılan estetik bir okuma.", 36),
        ).arrange(DOWN, buff=0.3)
        box = SurroundingRectangle(lines, buff=0.45, corner_radius=0.15, stroke_color=DIM, stroke_width=2)
        self.wait(0.3)
        self.say("not")
        self.play(Create(box), FadeIn(lines[0]), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in lines[1:]], lag_ratio=0.8), run_time=2.6)
        self.rest(1.2)
        word = ar("إِيمَان", 170)
        tiny = VGroup(ar("أ", 60, HEMZE), ar("م", 60, MIM), ar("ن", 60, NUN)).arrange(LEFT, buff=0.6).next_to(word, DOWN, buff=0.3)
        self.play(FadeOut(VGroup(box, lines)), run_time=0.8)
        self.play(Write(word), run_time=1.8)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.15) for t in tiny], lag_ratio=0.4), run_time=1.2)
        self.wait(2.0)
        self.play(FadeOut(VGroup(word, tiny)), run_time=1.5)
        self.wait(0.5)
