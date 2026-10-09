// Flat brand illustrations (ink #363435, orange #F58634, gray #858688)
const C = { ink: '#363435', ink2: '#2A2829', orange: '#F58634', gray: '#858688', light: '#C9C8C6', white: '#FFFFFF' };

const ICONS = {
  // ---------- products (viewBox 0 0 420 320, facing right) ----------
  botina: `<svg viewBox="0 0 420 320" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="210" cy="300" rx="185" ry="12" fill="#000" opacity=".08"/>
    <path d="M34 248 L392 248 Q404 250 403 266 Q401 288 378 288 L52 288 Q30 288 30 268 Z" fill="${C.ink2}"/>
    <g fill="${C.ink}" opacity=".9">${[...Array(13)].map((_, i) => `<rect x="${56 + i * 25}" y="280" width="14" height="10" rx="2"/>`).join('')}</g>
    <path d="M36 236 L398 236 Q404 248 398 254 L36 254 Z" fill="${C.light}"/>
    <rect x="36" y="232" width="364" height="9" rx="4" fill="${C.orange}"/>
    <path d="M58 232 L58 56 Q58 40 74 40 L186 40 Q200 40 201 56 L206 128 Q214 160 262 172 L338 190 Q396 204 398 232 Z" fill="${C.ink}"/>
    <path d="M300 182 L338 190 Q396 204 398 232 L286 232 Q282 200 300 182 Z" fill="#454344"/>
    <path d="M292 186 Q280 206 286 232" fill="none" stroke="${C.gray}" stroke-width="3" stroke-dasharray="7 6"/>
    <path d="M104 74 L156 74 L166 206 L112 206 Z" fill="${C.gray}"/>
    <g stroke="#6f7072" stroke-width="3">${[...Array(6)].map((_, i) => `<line x1="${112 + i * 9}" y1="80" x2="${118 + i * 9}" y2="200"/>`).join('')}</g>
    <rect x="52" y="30" width="154" height="30" rx="15" fill="#4a4849"/>
    <path d="M52 40 Q30 40 30 62 L30 84 Q30 96 42 96 L58 96 L58 40 Z" fill="${C.orange}"/>
    <path d="M70 70 L70 222 L282 222" fill="none" stroke="${C.gray}" stroke-width="3" stroke-dasharray="7 6" opacity=".7"/>
  </svg>`,

  coturno: `<svg viewBox="0 0 420 320" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="210" cy="306" rx="180" ry="11" fill="#000" opacity=".08"/>
    <path d="M44 258 L388 258 Q400 260 399 274 Q397 296 374 296 L60 296 Q40 296 40 276 Z" fill="${C.ink2}"/>
    <g fill="${C.ink}" opacity=".9">${[...Array(12)].map((_, i) => `<rect x="${66 + i * 26}" y="288" width="15" height="10" rx="2"/>`).join('')}</g>
    <rect x="44" y="246" width="352" height="16" rx="6" fill="${C.light}"/>
    <rect x="44" y="242" width="352" height="9" rx="4" fill="${C.orange}"/>
    <path d="M78 242 L78 18 Q78 6 90 6 L200 6 Q212 6 212 18 L216 150 Q224 176 266 186 L334 200 Q392 214 394 242 Z" fill="${C.ink}"/>
    <path d="M168 10 L212 10 L216 150 Q220 168 240 178 L176 178 Z" fill="#454344"/>
    <g fill="${C.orange}">${[...Array(7)].map((_, i) => `<circle cx="${186 + i * 1.2}" cy="${30 + i * 21}" r="5.5"/>`).join('')}</g>
    <g stroke="${C.light}" stroke-width="5" stroke-linecap="round">${[...Array(6)].map((_, i) => `<line x1="${180 + i * 1.2}" y1="${32 + i * 21}" x2="${208 + i * 1.2}" y2="${50 + i * 21}"/>`).join('')}</g>
    <path d="M300 194 Q288 216 292 242" fill="none" stroke="${C.gray}" stroke-width="3" stroke-dasharray="7 6"/>
    <rect x="72" y="0" width="146" height="26" rx="13" fill="#4a4849"/>
    <path d="M90 40 L90 232 L290 232" fill="none" stroke="${C.gray}" stroke-width="3" stroke-dasharray="7 6" opacity=".7"/>
  </svg>`,

  tenis: `<svg viewBox="0 0 420 320" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="210" cy="298" rx="188" ry="11" fill="#000" opacity=".08"/>
    <path d="M28 238 L396 238 Q408 246 404 264 Q400 284 374 284 L50 284 Q26 284 24 262 Z" fill="${C.white}" stroke="${C.light}" stroke-width="4"/>
    <path d="M26 262 L404 262 Q400 284 374 284 L50 284 Q28 284 26 262 Z" fill="${C.ink}"/>
    <path d="M40 238 L40 140 Q40 112 70 108 L120 104 Q150 102 168 120 L222 160 Q250 176 300 184 L350 192 Q398 202 398 238 Z" fill="${C.gray}"/>
    <path d="M40 140 Q40 112 70 108 L120 104 Q132 104 140 110 L132 150 Q100 160 62 158 Z" fill="${C.ink}"/>
    <path d="M300 184 L350 192 Q398 202 398 238 L310 238 Q300 210 300 184 Z" fill="${C.ink}"/>
    <path d="M70 214 Q170 200 236 168 Q260 156 290 160 Q250 196 170 222 Q120 236 70 232 Z" fill="${C.orange}"/>
    <g stroke="${C.white}" stroke-width="6" stroke-linecap="round">${[...Array(4)].map((_, i) => `<line x1="${176 + i * 20}" y1="${128 + i * 12}" x2="${196 + i * 20}" y2="${116 + i * 12}"/>`).join('')}</g>
    <path d="M34 112 Q30 92 50 92 L64 94 L64 112 Z" fill="${C.orange}"/>
  </svg>`,

  sapato: `<svg viewBox="0 0 420 320" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="210" cy="292" rx="186" ry="11" fill="#000" opacity=".08"/>
    <path d="M30 236 L394 236 Q406 238 405 254 Q403 276 380 276 L48 276 Q28 276 28 256 Z" fill="${C.ink2}"/>
    <rect x="32" y="226" width="368" height="10" rx="4" fill="${C.orange}"/>
    <path d="M44 226 L44 140 Q44 118 66 116 L130 112 Q150 112 162 124 L210 160 Q244 176 300 184 L344 192 Q398 202 400 226 Z" fill="${C.ink}"/>
    <path d="M118 116 L162 124 L214 162 Q200 172 168 170 L130 150 Z" fill="#4a4849"/>
    <g fill="${C.light}">${[...Array(4)].map((_, i) => `<circle cx="${140 + i * 18}" cy="${132 + i * 10}" r="4.5"/>`).join('')}</g>
    <g stroke="${C.gray}" stroke-width="4" stroke-linecap="round">${[...Array(3)].map((_, i) => `<line x1="${142 + i * 18}" y1="${134 + i * 10}" x2="${158 + i * 18}" y2="${144 + i * 10}"/>`).join('')}</g>
    <path d="M296 184 Q284 204 290 226" fill="none" stroke="${C.gray}" stroke-width="3" stroke-dasharray="7 6"/>
    <path d="M56 140 L56 214 L286 214" fill="none" stroke="${C.gray}" stroke-width="3" stroke-dasharray="7 6" opacity=".7"/>
  </svg>`,

  // ---------- line icons (viewBox 0 0 100 100) ----------
  lama: `<svg viewBox="0 0 100 100"><path d="M50 14 C50 14 26 44 26 60 a24 24 0 0 0 48 0 C74 44 50 14 50 14Z" fill="currentColor"/><path d="M40 62 a10 10 0 0 0 10 10" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/><circle cx="16" cy="78" r="5" fill="currentColor"/><circle cx="86" cy="74" r="6" fill="currentColor"/><circle cx="80" cy="30" r="4" fill="currentColor"/></svg>`,
  impacto: `<svg viewBox="0 0 100 100"><path d="M56 6 L22 56 L46 56 L38 94 L78 40 L52 40 Z" fill="currentColor"/></svg>`,
  relogio: `<svg viewBox="0 0 100 100"><circle cx="50" cy="52" r="36" fill="none" stroke="currentColor" stroke-width="9"/><path d="M50 30 L50 54 L66 64" fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/><rect x="40" y="4" width="20" height="10" rx="4" fill="currentColor"/></svg>`,
  check: `<svg viewBox="0 0 100 100"><path d="M22 52 L42 72 L80 30" fill="none" stroke="currentColor" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  capacete: `<svg viewBox="0 0 100 100"><path d="M18 66 Q18 26 50 24 Q82 26 82 66 Z" fill="currentColor"/><rect x="8" y="64" width="84" height="12" rx="6" fill="currentColor"/><rect x="44" y="18" width="12" height="30" rx="5" fill="#fff" opacity=".9"/></svg>`,
  fabrica: `<svg viewBox="0 0 100 100"><path d="M8 88 L8 46 L30 58 L30 46 L52 58 L52 46 L74 58 L74 14 L90 14 L90 88 Z" fill="currentColor"/><g fill="#363435"><rect x="16" y="68" width="10" height="10" rx="2"/><rect x="36" y="68" width="10" height="10" rx="2"/><rect x="56" y="68" width="10" height="10" rx="2"/></g></svg>`,
  hospital: `<svg viewBox="0 0 100 100"><rect x="14" y="14" width="72" height="72" rx="18" fill="currentColor"/><path d="M50 30 V70 M30 50 H70" stroke="#363435" stroke-width="13" stroke-linecap="round"/></svg>`,
  campo: `<svg viewBox="0 0 100 100"><rect x="34" y="22" width="28" height="30" rx="4" fill="none" stroke="currentColor" stroke-width="7"/><path d="M14 66 L14 52 L62 52 L84 56 L88 70 Z" fill="currentColor"/><circle cx="30" cy="72" r="16" fill="currentColor"/><circle cx="30" cy="72" r="6" fill="#363435"/><circle cx="78" cy="78" r="10" fill="currentColor"/><circle cx="78" cy="78" r="4" fill="#363435"/></svg>`,
  escudo: `<svg viewBox="0 0 200 230"><path d="M100 8 L188 40 L188 108 Q188 182 100 222 Q12 182 12 108 L12 40 Z" fill="${C.orange}"/><path d="M100 26 L172 52 L172 108 Q172 168 100 202 Q28 168 28 108 L28 52 Z" fill="none" stroke="#fff" stroke-width="5" opacity=".55"/></svg>`,
  pin: `<svg viewBox="0 0 120 160"><path d="M60 156 C60 156 8 92 8 58 a52 52 0 0 1 104 0 C112 92 60 156 60 156Z" fill="${C.orange}"/><circle cx="60" cy="58" r="22" fill="#fff"/></svg>`,
  globo: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="38" fill="none" stroke="currentColor" stroke-width="8"/><ellipse cx="50" cy="50" rx="16" ry="38" fill="none" stroke="currentColor" stroke-width="7"/><path d="M14 50 H86 M20 30 H80 M20 70 H80" stroke="currentColor" stroke-width="6"/></svg>`,
  insta: `<svg viewBox="0 0 100 100"><rect x="12" y="12" width="76" height="76" rx="22" fill="none" stroke="currentColor" stroke-width="9"/><circle cx="50" cy="50" r="17" fill="none" stroke="currentColor" stroke-width="9"/><circle cx="72" cy="28" r="6" fill="currentColor"/></svg>`,
  local: `<svg viewBox="0 0 100 100"><path d="M50 94 C50 94 16 56 16 36 a34 34 0 0 1 68 0 C84 56 50 94 50 94Z" fill="currentColor"/><circle cx="50" cy="36" r="13" fill="#fff"/></svg>`,
  pegada: `<svg viewBox="0 0 60 140"><path d="M30 4 Q56 4 56 40 Q56 70 46 84 L14 84 Q4 70 4 40 Q4 4 30 4Z" fill="currentColor"/><path d="M14 94 L46 94 Q52 116 46 130 Q30 140 14 130 Q8 116 14 94Z" fill="currentColor"/><g stroke="#F6F4F1" stroke-width="5" stroke-linecap="round"><line x1="16" y1="26" x2="44" y2="26"/><line x1="12" y1="42" x2="48" y2="42"/><line x1="14" y1="58" x2="46" y2="58"/><line x1="18" y1="108" x2="42" y2="108"/><line x1="20" y1="122" x2="40" y2="122"/></g></svg>`,
};
