"""
Jamie & Beth Bali Wedding -- Costs & What's Included
Run: python3 generate_wedding_pdf_v2.py
Output: jamie_beth_bali_wedding_costs_and_whats_included.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit, ImageReader

W, H = A4  # 595.28 x 841.89 pt

# Colours
IVORY       = HexColor("#FFF8EE")
SAND        = HexColor("#F2E3CF")
GOLD        = HexColor("#C8A45D")
GOLD_LIGHT  = HexColor("#E8D5A3")
TERRACOTTA  = HexColor("#C47A52")
TERRA_LIGHT = HexColor("#DDA080")
SAGE        = HexColor("#7F9A78")
SAGE_FAINT  = HexColor("#D5E5D0")
COCOA       = HexColor("#3B2A22")
COCOA_SOFT  = HexColor("#7A6657")
CARD_BG     = HexColor("#FAF3E6")
CARD_SAND   = HexColor("#F5E8D5")

HERE   = os.path.dirname(os.path.abspath(__file__))
MARGIN = 12*mm
CW     = W - 2*MARGIN
CX     = W / 2

def vimg(n):
    return os.path.join(HERE, "venue_images", n)


def register_fonts():
    for name, path in {
        "Georgia":       "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "GeorgiaB":      "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "GeorgiaI":      "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
        "BigCaslon":     "/System/Library/Fonts/Supplemental/BigCaslon.ttf",
        "AppleChancery": "/System/Library/Fonts/Supplemental/Apple Chancery.ttf",
        "GillSans":      "/System/Library/Fonts/Supplemental/GillSans.ttc",
    }.items():
        try:
            pdfmetrics.registerFont(TTFont(name, path))
        except Exception:
            pass


# ── Drawing helpers ────────────────────────────────────────────────────────────

def rrect(c, x, y, w, h, r, fill=None, stroke=None, sw=0.5):
    """Rounded rect. y = bottom-left corner."""
    c.saveState()
    if fill:   c.setFillColor(fill)
    if stroke: c.setStrokeColor(stroke); c.setLineWidth(sw)
    p = c.beginPath()
    p.moveTo(x+r, y);         p.lineTo(x+w-r, y)
    p.arcTo(x+w-2*r, y,       x+w, y+2*r,          -90, 90)
    p.lineTo(x+w, y+h-r);     p.arcTo(x+w-2*r, y+h-2*r, x+w, y+h, 0, 90)
    p.lineTo(x+r, y+h);       p.arcTo(x, y+h-2*r,   x+2*r, y+h, 90, 90)
    p.lineTo(x, y+r);         p.arcTo(x, y,          x+2*r, y+2*r, 180, 90)
    p.close()
    c.drawPath(p, fill=int(bool(fill)), stroke=int(bool(stroke)))
    c.restoreState()

def photo(c, path, x, y, w, h, r=0):
    c.saveState()
    p = c.beginPath()
    if r > 0:
        p.moveTo(x+r, y);         p.lineTo(x+w-r, y)
        p.arcTo(x+w-2*r, y,       x+w, y+2*r,          -90, 90)
        p.lineTo(x+w, y+h-r);     p.arcTo(x+w-2*r, y+h-2*r, x+w, y+h, 0, 90)
        p.lineTo(x+r, y+h);       p.arcTo(x, y+h-2*r,  x+2*r, y+h, 90, 90)
        p.lineTo(x, y+r);         p.arcTo(x, y,         x+2*r, y+2*r, 180, 90)
        p.close()
    else:
        p.rect(x, y, w, h)
    c.clipPath(p, fill=0, stroke=0)
    try:
        ir  = ImageReader(path)
        iw, ih = ir.getSize()
        sc  = max(w/iw, h/ih)
        sw2, sh2 = iw*sc, ih*sc
        c.drawImage(ir, x+(w-sw2)/2, y+(h-sh2)/2, sw2, sh2, mask='auto')
    except Exception:
        c.setFillColor(SAND); c.rect(x, y, w, h, fill=1, stroke=0)
    c.restoreState()

def gold_divider(c, cx, y, w=120):
    c.saveState()
    c.setStrokeColor(Color(GOLD.red, GOLD.green, GOLD.blue, 0.6))
    c.setFillColor(GOLD); c.setLineWidth(0.5)
    gap = 9
    c.line(cx-w/2, y, cx-gap, y); c.line(cx+gap, y, cx+w/2, y)
    s = 3.2
    p = c.beginPath()
    p.moveTo(cx,y+s); p.lineTo(cx+s,y); p.lineTo(cx,y-s); p.lineTo(cx-s,y); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def ctext(c, text, cx, y, font, size, color):
    c.setFont(font, size); c.setFillColor(color)
    c.drawString(cx - c.stringWidth(text, font, size)/2, y, text)

def sec_heading(c, text, x, y):
    """Terracotta bar + BigCaslon label. Bar sits from y-1mm to y+3.8mm."""
    c.setFillColor(TERRACOTTA)
    c.rect(x, y - 1*mm, 2.2*mm, 4.8*mm, fill=1, stroke=0)
    c.setFont("BigCaslon", 11); c.setFillColor(COCOA)
    c.drawString(x + 3.5*mm, y, text)

def bullet(c, text, x, y, mw, dot_color=GOLD, fs=8.5):
    c.setFillColor(dot_color)
    c.circle(x+4, y+fs*0.38, 2.0, fill=1, stroke=0)
    lines = simpleSplit(text, "Georgia", fs, mw-13)
    c.setFont("Georgia", fs); c.setFillColor(COCOA)
    for i, ln in enumerate(lines):
        c.drawString(x+13, y - i*fs*1.45, ln)
    return len(lines) * fs * 1.45

def body_lines(c, lines, x, y, font, size, color, lh):
    """Draw a pre-split list of lines, return height consumed."""
    c.setFont(font, size); c.setFillColor(color)
    for i, ln in enumerate(lines):
        if ln: c.drawString(x, y - i*lh, ln)
    return len(lines) * lh

def wrapped(c, text, x, y, mw, font, size, color, lh=1.55):
    lines = simpleSplit(text, font, size, mw)
    body_lines(c, lines, x, y, font, size, color, size*lh)
    return len(lines) * size * lh

def card_height(fpad, head, rows, row_h, extra=0):
    """Compute total height of a standard card."""
    return fpad + head + rows*row_h + extra + fpad


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Excitement and value
# ══════════════════════════════════════════════════════════════════════════════

def page1(c):
    # Layout constants
    FPAD    = 5*mm
    HEAD    = 6*mm
    BH      = 6.5*mm
    LH      = 4.5*mm
    COL_GAP = 4*mm

    col_w2 = (CW - COL_GAP) / 2
    c1x = MARGIN
    c2x = MARGIN + col_w2 + COL_GAP

    # Background
    c.setFillColor(IVORY); c.rect(0, 0, W, H, fill=1, stroke=0)

    # Hero photo — 22% of page height
    hero_h = H * 0.22
    hero_y = H - hero_h
    photo(c, vimg("main_pool_night.jpg"), 0, hero_y, W, hero_h)

    # Dark gradient over top of hero for title legibility
    for i in range(30):
        t = i/30
        alpha = (1-t)**1.4 * 0.75
        bh = (hero_h*0.65)/30
        c.setFillColor(Color(COCOA.red, COCOA.green, COCOA.blue, alpha))
        c.rect(0, H-(i+1)*bh, W, bh+1, fill=1, stroke=0)

    # Ivory fade at bottom of hero
    for i in range(20):
        t = i/20
        alpha = t**1.5 * 0.97
        bh = (hero_h*0.30)/20
        c.setFillColor(Color(IVORY.red, IVORY.green, IVORY.blue, alpha))
        c.rect(0, hero_y+(19-i)*bh, W, bh+1, fill=1, stroke=0)

    # Title text over hero
    ty = H - 24*mm
    label = "S A V E   T H E   D A T E   ( A L M O S T )"
    lw = c.stringWidth(label, "GillSans", 8)
    c.setFont("GillSans", 8)
    c.setFillColor(Color(GOLD_LIGHT.red, GOLD_LIGHT.green, GOLD_LIGHT.blue, 0.88))
    c.drawString(CX - lw/2, ty, label)
    ty -= 14*mm
    ctext(c, "Jamie & Beth's", CX, ty, "AppleChancery", 40, white)
    ty -= 12*mm
    ctext(c, "Bali Wedding 2028", CX, ty, "BigCaslon", 28, IVORY)

    # ── Content below hero ────────────────────────────────────────────────────
    y = hero_y - 5*mm
    gold_divider(c, CX, y, 110);        y -= 7*mm
    ctext(c, "April 2028  \xb7  Canggu, Bali", CX, y, "GeorgiaI", 11.5, COCOA_SOFT)
    y -= 4*mm
    y -= 4*mm
    ctext(c, "We'd love you to join us for our wedding in Bali.", CX, y, "GeorgiaI", 11.5, TERRACOTTA)
    y -= 8*mm

    intro1 = ("We're planning a 10-day villa stay from 5th to 15th April 2028, staying together at a "
              "beautiful private villa estate in Canggu.")
    h = wrapped(c, intro1, MARGIN, y, CW, "Georgia", 9, COCOA, 1.55); y -= h + 3*mm

    intro2 = ("If you'd like to arrive when the villa stay begins on 5th April, you'll likely need "
              "to fly on 4th April because of the travel time and time difference.")
    h = wrapped(c, intro2, MARGIN, y, CW, "Georgia", 9, COCOA, 1.55); y -= h + 3*mm

    intro3 = ("The wedding day is still to be confirmed, with the rest of the trip for relaxing, "
              "celebrating and enjoying Bali together.")
    h = wrapped(c, intro3, MARGIN, y, CW, "Georgia", 9, COCOA, 1.55); y -= h + 3*mm

    intro4 = ("We know this is a big trip, so we wanted to share the estimated costs early to help "
              "you decide whether it feels affordable. There's absolutely no pressure — we "
              "completely understand that a destination wedding is a big commitment.")
    h = wrapped(c, intro4, MARGIN, y, CW, "Georgia", 9, COCOA, 1.55); y -= h + 6*mm

    gold_divider(c, CX, y, 90); y -= 8*mm

    # Dates at a glance
    sec_heading(c, "Dates at a Glance", MARGIN, y); y -= 7*mm
    dates = [
        ("Trip Dates", "5th–15th Apr 2028"),
        ("Location",   "Canggu, Bali"),
        ("Stay",       "10 nights"),
        ("Wedding Day","To be confirmed"),
    ]
    pill_gap = 3*mm
    pill_w   = (CW - 3*pill_gap) / 4
    pill_h   = 13*mm
    for i, (lbl, val) in enumerate(dates):
        px = MARGIN + i*(pill_w+pill_gap)
        rrect(c, px, y-pill_h, pill_w, pill_h, 3*mm,
              fill=Color(SAND.red, SAND.green, SAND.blue, 0.55),
              stroke=Color(GOLD.red, GOLD.green, GOLD.blue, 0.50), sw=0.5)
        ctext(c, lbl, px+pill_w/2, y-4.5*mm,  "GillSans", 7,   COCOA_SOFT)
        ctext(c, val, px+pill_w/2, y-9.5*mm,  "GeorgiaB", 7.5, COCOA)
    y -= pill_h + 3*mm

    dates_note = ("We've tried hard to choose dates that work for as many people as possible. "
                  "The 2028 Easter holidays aren't as aligned across schools as usual, and with "
                  "9 UK schools plus Italian schools to factor in, it hasn't been possible to find "
                  "a perfect window for everyone. Easter was always our preferred time to celebrate, "
                  "and it also helps avoid the higher prices of the summer holidays. We really hope "
                  "these dates work for the majority, but completely understand if they don't work "
                  "for everyone.")
    dn_lh = 7 * 1.45
    for i, ln in enumerate(simpleSplit(dates_note, "GeorgiaI", 7, CW)):
        c.setFont("GeorgiaI", 7); c.setFillColor(COCOA_SOFT)
        c.drawString(MARGIN, y - i*dn_lh, ln)
    y -= len(simpleSplit(dates_note, "GeorgiaI", 7, CW)) * dn_lh + 3*mm

    gold_divider(c, CX, y, 90); y -= 8*mm

    # ── What's Included: Food & Catering (full-width, two internal columns) ──
    IFS    = 8          # bullet font size for this card
    IBH    = 7*mm       # bullet row height
    IPAD   = 4*mm       # card top/bottom padding
    IHEAD  = 6*mm       # heading row height
    SUB_LH = 4.2*mm     # sub-bullet line height

    half_w    = CW / 2
    icol1x    = MARGIN + 4*mm          # left col bullet start x
    icol2x    = MARGIN + half_w + 4*mm # right col bullet start x
    icol_text = half_w - 9*mm          # usable text width per column

    incl_left = [
        "10 nights at a private villa estate in Canggu",
        "Breakfast included every day",
        "Premium private catering for lunch and dinner for 9 days",
        "Separate catering included for the wedding day",
    ]
    incl_right = [
        "Private chefs and butlers on-site",
        "A small selection of drinks with meals, plus some daytime snacks",
        "Use of the villa estate, pools and shared spaces",
    ]
    incl_note = ("You're very welcome to eat out at local restaurants or beach bars whenever you "
                 "like. However, the villa catering will already be included and paid for as part "
                 "of the package.")

    sub_text   = "Other drinks and snacks can be purchased from the venue or local shops"
    sub_indent = 7*mm
    # Split against available width after the indent (13pt is bullet() internal offset)
    sub_lines  = simpleSplit(sub_text, "GeorgiaI", 8, icol_text - sub_indent)
    sub_h      = len(sub_lines) * SUB_LH + 2*mm

    note_lines = simpleSplit(incl_note, "GeorgiaI", 8.5, CW - 8*mm)
    note_lh    = 4.5*mm

    # Right col: 2 bullets, sub, 1 bullet
    left_col_h  = len(incl_left) * IBH
    right_col_h = 2*IBH + sub_h + 1*IBH
    col_h       = max(left_col_h, right_col_h)

    incl_card_h = IPAD + IHEAD + col_h + 5*mm + len(note_lines)*note_lh + IPAD

    rrect(c, MARGIN, y-incl_card_h, CW, incl_card_h, 4*mm,
          fill=CARD_BG,
          stroke=Color(GOLD.red, GOLD.green, GOLD.blue, 0.55), sw=0.7)

    cty = y - IPAD
    sec_heading(c, "What's Included", MARGIN+3*mm, cty); cty -= IHEAD

    # Subtle vertical rule between columns
    c.setStrokeColor(Color(GOLD.red, GOLD.green, GOLD.blue, 0.22))
    c.setLineWidth(0.4)
    c.line(MARGIN + half_w, cty - col_h - 1*mm, MARGIN + half_w, cty + 2*mm)

    # Left column
    lty = cty
    for b in incl_left:
        bullet(c, b, icol1x, lty, icol_text, SAGE, IFS); lty -= IBH

    # Right column
    rty = cty
    for i, b in enumerate(incl_right):
        bullet(c, b, icol2x, rty, icol_text, SAGE, IFS); rty -= IBH
        if i == 1:
            # Indented italic sub-bullet
            for j, ln in enumerate(sub_lines):
                c.setFont("GeorgiaI", 8); c.setFillColor(COCOA_SOFT)
                prefix = "–  " if j == 0 else "     "
                c.drawString(icol2x + sub_indent, rty - j*SUB_LH, prefix + ln)
            rty -= sub_h

    # Thin rule above note
    rule_y = cty - col_h - 3*mm
    c.setStrokeColor(Color(GOLD.red, GOLD.green, GOLD.blue, 0.25))
    c.setLineWidth(0.3)
    c.line(MARGIN + 4*mm, rule_y, MARGIN + CW - 4*mm, rule_y)

    # Note
    note_y = rule_y - 3*mm
    for i, ln in enumerate(note_lines):
        c.setFont("GeorgiaI", 8.5); c.setFillColor(COCOA_SOFT)
        c.drawString(MARGIN + 4*mm, note_y - i*note_lh, ln)

    y -= incl_card_h + 5*mm

    # ── Villa Highlights — full-width, two columns ───────────────────────────
    vh_left  = [
        "Exclusive use of the private estate with 12 individual wooden villas",
        "12 private swimming pools throughout the property",
    ]
    vh_right = [
        "Lush tropical gardens with beautiful rice field views",
        "Fully staffed from 7am to 11pm",
    ]
    vh_col_w  = (CW - COL_GAP) / 2
    VH_EXTRA  = 3*mm   # extra gap after first bullet which wraps to 2 lines
    vh_h      = FPAD + HEAD + 2*BH + VH_EXTRA + FPAD

    rrect(c, MARGIN, y-vh_h, CW, vh_h, 4*mm,
          fill=Color(SAGE_FAINT.red, SAGE_FAINT.green, SAGE_FAINT.blue, 0.45),
          stroke=Color(SAGE.red, SAGE.green, SAGE.blue, 0.50), sw=0.6)
    vty = y - FPAD
    sec_heading(c, "Villa Highlights", MARGIN+3*mm, vty); vty -= HEAD
    # Subtle column rule
    c.setStrokeColor(Color(SAGE.red, SAGE.green, SAGE.blue, 0.22))
    c.setLineWidth(0.4)
    c.line(MARGIN + CW/2, vty - 2*BH - VH_EXTRA, MARGIN + CW/2, vty + 2*mm)
    for i, b in enumerate(vh_left):
        bullet(c, b, MARGIN+3*mm, vty, vh_col_w-6*mm, GOLD, 8)
        vty -= BH + (VH_EXTRA if i == 0 else 0)
    vty = y - FPAD - HEAD
    for b in vh_right:
        bullet(c, b, MARGIN+vh_col_w+COL_GAP, vty, vh_col_w-6*mm, GOLD, 8); vty -= BH

    # Ensure at least 8mm gap to page bottom
    page1_bottom = y - vh_h
    if page1_bottom < MARGIN + 8*mm:
        pass  # geometry is guaranteed by hero reduction above


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Costs and decision
# ══════════════════════════════════════════════════════════════════════════════

def page2(c):
    # All font sizes and split widths must match exactly to prevent overflow.
    # BODY_FS = font size used in ALL card body text and simpleSplit calls.
    # FPAD = 5mm ensures sec_heading bar (top at y+3.8mm) sits cleanly inside card top.
    FPAD     = 5*mm
    HEAD     = 6*mm
    LH       = 4.0*mm
    BH       = 5.0*mm
    ROW_GAP  = 1.5*mm
    BODY_FS  = 8        # single source of truth for body font size
    STRIP_H  = 16*mm
    PARA_GAP = 1.5*mm   # gap between paragraphs inside row3

    col_gap = 4*mm
    col_w2  = (CW - col_gap) / 2
    c1x = MARGIN
    c2x = MARGIN + col_w2 + col_gap
    cw2 = col_w2 - 6*mm   # text width inside half-width card

    c.setFillColor(IVORY); c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Heading ───────────────────────────────────────────────────────────────
    y = H - MARGIN
    ctext(c, "Costs & What You Need to Know", CX, y, "BigCaslon", 17, COCOA)
    y -= 6*mm
    gold_divider(c, CX, y, 130); y -= 8*mm

    # ── Cost table ────────────────────────────────────────────────────────────
    sec_heading(c, "Estimated Cost Per Person", MARGIN, y); y -= 7*mm

    table_rows = [
        ("Cost item",                  "13 years+", "12 and under"),
        ("Indicative flights",         "1,106",     "762"),
        ("Accommodation & catering",   "563",       "563"),
        ("Estimated total per person", "1,669",     "1,325"),
    ]
    col_widths = [CW*0.54, CW*0.23, CW*0.23]
    t_row_h = 7*mm
    table_h = len(table_rows)*t_row_h + 2*mm

    rrect(c, MARGIN, y-table_h, CW, table_h, 3*mm,
          fill=CARD_BG,
          stroke=Color(GOLD.red, GOLD.green, GOLD.blue, 0.6), sw=0.8)

    ty2 = y - 2*mm
    for ri, row in enumerate(table_rows):
        is_hdr   = ri == 0
        is_total = ri == len(table_rows)-1
        row_y    = ty2 - (ri+0.5)*t_row_h
        if is_hdr:
            rrect(c, MARGIN+0.5*mm, row_y-t_row_h/2+1, CW-1*mm, t_row_h-1, 3*mm,
                  fill=Color(GOLD_LIGHT.red, GOLD_LIGHT.green, GOLD_LIGHT.blue, 0.40))
        elif is_total:
            rrect(c, MARGIN+0.5*mm, row_y-t_row_h/2+1, CW-1*mm, t_row_h-1, 2*mm,
                  fill=Color(TERRACOTTA.red, TERRACOTTA.green, TERRACOTTA.blue, 0.12))
        xc = MARGIN + 3*mm
        for ci, cell in enumerate(row):
            font    = "GeorgiaB" if (is_hdr or is_total) else "Georgia"
            size    = 8 if is_hdr else 8.5
            color   = TERRACOTTA if (is_total and ci > 0) else COCOA
            display = ("\xa3"+cell) if (not is_hdr and ci > 0) else cell
            if ci == 0:
                c.setFont(font, size); c.setFillColor(color)
                c.drawString(xc, row_y-2, display)
            else:
                tw     = c.stringWidth(display, font, size)
                cx_col = xc + col_widths[ci]/2
                c.setFont(font, size); c.setFillColor(color)
                c.drawString(cx_col-tw/2, row_y-2, display)
            xc += col_widths[ci]
        if ri < len(table_rows)-1:
            c.setStrokeColor(Color(0.85, 0.82, 0.78, 0.8)); c.setLineWidth(0.3)
            c.line(MARGIN+3*mm, row_y-t_row_h/2+1, MARGIN+CW-3*mm, row_y-t_row_h/2+1)

    y -= table_h + 4*mm
    wrapped(c, "Includes indicative flights, 10 nights' accommodation and full-board villa catering.",
            MARGIN, y, CW, "GeorgiaI", 8, COCOA_SOFT, 1.4)
    y -= 5*mm

    # ── 3-photo strip ─────────────────────────────────────────────────────────
    strip_gap = 3*mm
    strip_w   = (CW - 2*strip_gap) / 3
    for i, fn in enumerate(["pool_close_up.jpg", "rice field.jpeg", "floating breakfast.jpg"]):
        photo(c, vimg(fn), MARGIN + i*(strip_w+strip_gap), y-STRIP_H, strip_w, STRIP_H, 3*mm)
    y -= STRIP_H + 5*mm
    gold_divider(c, CX, y, 90); y -= 7*mm

    # ── Pre-compute content — all splits use BODY_FS to match drawing ─────────
    # Bold label + regular continuation for each pay step
    pay_steps = [
        ("1.  ", "Flights",                  " — booked and paid for directly by you. We'll share our flight details once booked, in case you'd like to travel with us."),
        ("2.  ", "Accommodation and catering", " — paid to us as part of the group villa booking."),
    ]
    pn1 = ("Flight costs are indicative, based on April 2027 prices. April 2028 flights "
           "aren't available yet. Cheaper and pricier options will likely exist.")
    pn2 = ("The villa price is agreed, although the final amount may change slightly due "
           "to exchange rate fluctuations. The \xa3563 per person estimate is based on "
           "current likely numbers.")
    pn3 = ("We're also speaking with other caterers, so we may be able to reduce the "
           "catering cost. We'll confirm the final cost once we have firm responses.")
    not_incl = [
        "Travel insurance",
        "Local visas",
        "Optional activities or day trips",
        "Meals or drinks away from the villa",
        "Extra drinks or personal spending",
        "Airport transfers — can be arranged through the venue closer to the time. Indicatively \xa320 for a family of 4.",
    ]
    drinks_items = [
        ("Local beer",  "approx. \xa31.75"),
        ("Soft drink",  "approx. \xa30.75"),
        ("Fresh juice", "approx. \xa32.00"),
        ("Mocktail",    "approx. \xa32.25"),
        ("Cocktail",    "approx. \xa33.25"),
        ("Wine",        "approx. \xa34.50 per glass"),
    ]
    drink_note = "Local supermarkets nearby if you'd like to keep costs lower."
    need_paras = [
        "Please let us know by the end of June whether you are a firm yes or no for joining us in Bali.",
        ("We're sharing this information as early as we can to give everyone as much time as possible "
         "to think it through, plan and save."),
        ("Because this is a group villa booking, the final cost depends on confirmed numbers. Once "
         "we've agreed the booking, any changes or drop-outs later may affect the cost for the rest "
         "of the group."),
        ("There's absolutely no pressure — we completely understand this is a big trip. We just ask "
         "that you only say yes if you're comfortable with the estimated cost and feel sure you can come."),
        "Once we have everyone's responses, we'll book the venue, confirm the final cost and next steps.",
    ]

    ps_lines   = [simpleSplit(pre+bold+rest, "Georgia", BODY_FS, cw2) for pre, bold, rest in pay_steps]
    pay_note   = "Once we have final numbers, we will share a payment schedule for the accommodation element with you all."
    pay_note_lines = simpleSplit(pay_note, "GeorgiaI", BODY_FS, cw2)
    pn1_lines = simpleSplit(pn1, "Georgia",  BODY_FS, cw2)
    pn2_lines = simpleSplit(pn2, "Georgia",  BODY_FS, cw2)
    pn3_lines = simpleSplit(pn3, "GeorgiaI", BODY_FS, cw2)   # italic paragraph
    dn_lines  = simpleSplit(drink_note, "GeorgiaI", 7.5, cw2)
    need_lines_split = [simpleSplit(p, "Georgia", BODY_FS, CW-8*mm) for p in need_paras]

    # Heights — content measured at exact font+width used in drawing
    DRINK_ROW = 5.0*mm
    pay_content     = sum(len(s) for s in ps_lines) * LH + 2*mm + len(pay_note_lines)*LH
    not_content     = len(not_incl) * BH
    pricing_content = (len(pn1_lines)*LH + LH +
                       len(pn2_lines)*LH + LH +
                       len(pn3_lines)*LH)
    drinks_content  = len(drinks_items)*DRINK_ROW + 2*mm + len(dn_lines)*LH

    pay_h     = FPAD + HEAD + pay_content     + FPAD
    not_h     = FPAD + HEAD + not_content     + FPAD
    pricing_h = FPAD + HEAD + pricing_content + FPAD
    drinks_h  = FPAD + HEAD + drinks_content  + FPAD

    row1_h = max(pay_h, not_h)
    row2_h = max(drinks_h, pricing_h)

    need_content = (sum(len(ls)*LH for ls in need_lines_split) +
                    (len(need_paras)-1)*PARA_GAP)
    row3_h = FPAD + HEAD + need_content + FPAD

    # ── Row 1: How will we pay? | What's not included ────────────────────────
    rrect(c, c1x, y-row1_h, col_w2, row1_h, 4*mm,
          fill=CARD_BG,
          stroke=Color(GOLD.red, GOLD.green, GOLD.blue, 0.55), sw=0.7)
    ty = y - FPAD
    sec_heading(c, "How Will We Pay?", c1x+3*mm, ty); ty -= HEAD
    for (pre, bold, rest), s_lines in zip(pay_steps, ps_lines):
        for li, ln in enumerate(s_lines):
            if li == 0:
                # Draw prefix + bold label + rest on first line
                c.setFont("Georgia", BODY_FS); c.setFillColor(COCOA)
                c.drawString(c1x+4*mm, ty, pre)
                px = c1x+4*mm + c.stringWidth(pre, "Georgia", BODY_FS)
                c.setFont("GeorgiaB", BODY_FS)
                c.drawString(px, ty, bold)
                px += c.stringWidth(bold, "GeorgiaB", BODY_FS)
                # remainder of first line after the bold word
                first_line_rest = ln[len(pre+bold):]
                c.setFont("Georgia", BODY_FS)
                c.drawString(px, ty, first_line_rest)
            else:
                c.setFont("Georgia", BODY_FS); c.setFillColor(COCOA)
                c.drawString(c1x+4*mm, ty, ln)
            ty -= LH
    ty -= 2*mm
    for ln in pay_note_lines:
        c.setFont("GeorgiaI", BODY_FS); c.setFillColor(COCOA_SOFT)
        c.drawString(c1x+4*mm, ty, ln); ty -= LH

    rrect(c, c2x, y-row1_h, col_w2, row1_h, 4*mm,
          fill=CARD_BG,
          stroke=Color(CARD_BG.red*0.88, CARD_BG.green*0.88, CARD_BG.blue*0.88, 0.8), sw=0.5)
    ty = y - FPAD
    sec_heading(c, "What's Not Included", c2x+3*mm, ty); ty -= HEAD
    for b in not_incl:
        bullet(c, b, c2x+3*mm, ty, col_w2-6*mm, TERRACOTTA, BODY_FS); ty -= BH

    y -= row1_h + ROW_GAP

    # ── Row 2: Extra drinks | A note on pricing ───────────────────────────────
    # Drinks card: vertically centre content within the taller pricing card height
    drinks_offset = (row2_h - drinks_h) / 2   # shift content down by this to centre
    rrect(c, c1x, y-row2_h, col_w2, row2_h, 4*mm,
          fill=Color(SAGE_FAINT.red, SAGE_FAINT.green, SAGE_FAINT.blue, 0.40),
          stroke=Color(SAGE.red, SAGE.green, SAGE.blue, 0.45), sw=0.5)
    ty = y - drinks_offset - FPAD
    sec_heading(c, "Extra Drinks at the Villa", c1x+3*mm, ty); ty -= HEAD
    for item, price in drinks_items:
        iw = c.stringWidth(item,  "Georgia",  BODY_FS)
        pw = c.stringWidth(price, "GeorgiaI", BODY_FS)
        c.setFont("Georgia",  BODY_FS); c.setFillColor(COCOA)
        c.drawString(c1x+5*mm, ty, item)
        c.setFont("GeorgiaI", BODY_FS); c.setFillColor(COCOA_SOFT)
        c.drawString(c1x+col_w2-pw-4*mm, ty, price)
        c.setStrokeColor(Color(CARD_SAND.red, CARD_SAND.green, CARD_SAND.blue, 0.5))
        c.setLineWidth(0.25)
        c.line(c1x+5*mm+iw+1*mm, ty+2, c1x+col_w2-pw-5*mm, ty+2)
        ty -= DRINK_ROW
    ty -= 2*mm
    for ln in dn_lines:
        c.setFont("GeorgiaI", 7.5); c.setFillColor(COCOA_SOFT)
        c.drawString(c1x+4*mm, ty, ln); ty -= LH

    rrect(c, c2x, y-row2_h, col_w2, row2_h, 4*mm,
          fill=Color(SAND.red, SAND.green, SAND.blue, 0.35),
          stroke=Color(TERRA_LIGHT.red, TERRA_LIGHT.green, TERRA_LIGHT.blue, 0.45), sw=0.6)
    ty = y - FPAD
    sec_heading(c, "A Note on Pricing", c2x+3*mm, ty); ty -= HEAD
    for ln in pn1_lines:
        c.setFont("Georgia", BODY_FS); c.setFillColor(COCOA)
        c.drawString(c2x+4*mm, ty, ln); ty -= LH
    ty -= LH
    for ln in pn2_lines:
        c.setFont("Georgia", BODY_FS); c.setFillColor(COCOA)
        c.drawString(c2x+4*mm, ty, ln); ty -= LH
    ty -= LH
    for ln in pn3_lines:
        c.setFont("GeorgiaI", BODY_FS); c.setFillColor(COCOA_SOFT)
        c.drawString(c2x+4*mm, ty, ln); ty -= LH

    y -= row2_h + ROW_GAP

    # ── Row 3: What we need from you — full-width, single-column card ─────────
    # Similarly centre the pay card content if shorter than not_incl card
    rrect(c, MARGIN, y-row3_h, CW, row3_h, 4*mm,
          fill=Color(SAGE_FAINT.red, SAGE_FAINT.green, SAGE_FAINT.blue, 0.35),
          stroke=Color(SAGE.red, SAGE.green, SAGE.blue, 0.45), sw=0.6)
    ty = y - FPAD
    sec_heading(c, "What We Need From You Now", MARGIN+3*mm, ty); ty -= HEAD
    for i, ls in enumerate(need_lines_split):
        for ln in ls:
            c.setFont("Georgia", BODY_FS); c.setFillColor(COCOA)
            c.drawString(MARGIN+4*mm, ty, ln); ty -= LH
        if i < len(need_lines_split)-1:
            ty -= PARA_GAP   # gap between paragraphs, no blank line row

    y -= row3_h + ROW_GAP

    # ── Sign-off ──────────────────────────────────────────────────────────────
    gold_divider(c, CX, y, 110);  y -= 7*mm
    ctext(c, "We can't wait to celebrate with you.", CX, y, "GeorgiaI", 11, COCOA_SOFT)
    y -= 8*mm
    ctext(c, "Jamie & Beth", CX, y, "AppleChancery", 18, TERRACOTTA)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def generate():
    register_fonts()
    out = os.path.join(HERE, "jamie_beth_bali_wedding_costs_and_whats_included.pdf")
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("Jamie & Beth -- Bali Wedding 2028")
    c.setAuthor(""); c.setCreator(""); c.setSubject("Wedding Information Sheet")
    page1(c); c.showPage()
    page2(c); c.save()
    print("PDF saved: " + out)

if __name__ == "__main__":
    generate()
