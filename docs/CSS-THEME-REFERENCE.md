# CSS Theme Reference — USDseal Inspector

**Pflichtlektüre vor jedem `var(--*)` in neuem Code.**
Alle Variablen sind in `src/inspector.html` `:root { }` definiert.
Stand: v0.28.0.7

---

## Definierte Variablen

### Brand / Akzent
| Variable | Wert | Verwendung |
|---|---|---|
| `--primary` | `#F97316` | Orange — CTA-Buttons, Highlights, Icons |
| `--primary-dark` | `#C2410C` | Dunkel-Orange — Hover, Akzentleisten in PDF |
| `--accent` | `#0891B2` | Teal — Links, sekundäre CTAs |
| `--accent-dark` | `#065F73` | Dunkel-Teal — Link-Hover |

### Text
| Variable | Wert | Verwendung |
|---|---|---|
| `--text-heading` | `#1A1A1A` | Überschriften, Labels, primärer Body-Text |
| `--text-body` | `#555555` | Normaler Fließtext |
| `--text-desc` | `#888888` | Beschreibungen, Hints, sekundäre Zeilen |
| `--text-secondary` | `#999999` | Weniger wichtige Info, Meta-Labels |
| `--text-muted` | `#AAAAAA` | Footer, Timestamps, sehr zurückhaltendes UI |
| `--text-disabled` | `#CCCCCC` | Disabled-Zustand, Platzhalter |

### Hintergründe
| Variable | Wert | Verwendung |
|---|---|---|
| `--bg-canvas` | `#FFFFFF` | Karten, Panels, Tester-Panel |
| `--bg-neutral` | `#FAFAFA` | Seiten-Hintergrund, Section-Hintergrund |
| `--bg-primary-tint` | `#FFF8F4` | Oranges Tint — Version-Badge, Hover-States |
| `--bg-accent-tint` | `#F0FDFE` | Teal-Tint — Info-Boxen, Accent-Highlights |

### Borders
| Variable | Wert | Verwendung |
|---|---|---|
| `--border-card` | `#F0F0F0` | Außenrand von Cards/Panels (sehr hell) |
| `--border-inner` | `#E5E5E5` | Innere Trennlinien, Input-Borders, Dropdowns |
| `--border-primary` | `#FBD5BC` | Oranges Tint-Border — Badge, Primary-Akzent |
| `--border-accent` | `#A5F0F9` | Teal-Tint-Border — Accent-Boxen |

### Typografie
| Variable | Wert | Verwendung |
|---|---|---|
| `--font` | `-apple-system, SF Pro Display, …` | Systemfont-Stack, alle UI-Texte |
| `--mono` | `'SF Mono', 'Fira Code', …` | Code-Blöcke, Hashes, Checksums |

---

## Häufige Anti-Pattern (Root-Cause v0.28.0.5 + v0.28.0.6)

Diese Variablen sind **NICHT definiert** — Browser fällt auf `transparent`/`inherit` zurück:

| ❌ Falsch (undefined) | ✅ Richtig (defined) | Kontext |
|---|---|---|
| `var(--border)` | `var(--border-inner)` | Input-Felder, Panel-Borders, Tester-Block |
| `var(--border-outer)` | `var(--border-card)` | Canvas-Wrap, Außenränder von Section-Containern |
| `var(--bg)` | `var(--bg-neutral)` | Seiten- / Section-Hintergrund |
| `var(--bg-section)` | `var(--bg-neutral)` | Advanced-Player-Bereiche, Section-Hintergründe |
| `var(--surface)` | `var(--bg-canvas)` | Weiße Karten-Hintergründe |
| `var(--text)` | `var(--text-heading)` | Primärer Text (wenn kein spezifischerer Key passt) |

**Merkhilfe:** Im Theme gibt es kein "generisches" Kürzel.
Jede Variable trägt ihren Zweck im Namen: `bg-*`, `text-*`, `border-*`.

---

## Konvention für neue Sprints

1. **Vor jedem `var(--xxx)`**: hier nachschauen, ob die Variable in der Tabelle steht.
2. Kein Raten nach Analogie (`--border` klingt plausibel, ist aber nicht definiert).
3. Neue semantische Farben (z. B. `--red-error`) gehören zuerst in `:root` — dann in diese Doku — dann in den Code.
4. Hartkodierte Hex-Literale für einmalige Ausnahmen (z. B. `#DC2626` für einen Inline-Fehlertext) sind okay, wenn es kein passendes Theme-Äquivalent gibt. In `--primary-dark` oder `--border-inner` umschreiben, wenn sich ein Muster abzeichnet.
5. `build.py` gibt eine Warnung aus bei undefinierten `var(--*)` — Build stoppt nicht, aber ignorieren ist keine Option.

---

## Schnellreferenz Farb-Hierarchie

```
Primary (Orange):   --primary  →  --primary-dark
Accent (Teal):      --accent   →  --accent-dark
Text:               --text-heading  →  --text-body  →  --text-desc  →  --text-secondary  →  --text-muted  →  --text-disabled
Background:         --bg-canvas (weiß)  →  --bg-neutral (off-white)  →  --bg-primary-tint  →  --bg-accent-tint
Border:             --border-card (sehr hell)  →  --border-inner  →  --border-primary  →  --border-accent
```
