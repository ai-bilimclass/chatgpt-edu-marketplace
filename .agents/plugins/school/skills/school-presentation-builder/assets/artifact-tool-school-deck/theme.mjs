export const SLIDE = Object.freeze({ width: 1280, height: 720 });
export const FRAME = Object.freeze({ left: 64, top: 48, width: 1152, height: 624 });

export const PALETTES = Object.freeze({
  academicBlue: { dark: "#12355B", main: "#2F80ED", pale: "#EAF3FB", accent: "#F2C94C", ink: "#263238", paper: "#FFFFFF" },
  seaTealWarmYellow: { dark: "#0F5B66", main: "#138A98", pale: "#EEF8F8", accent: "#F4B942", ink: "#263238", paper: "#FFFFFF" },
  indigoCoral: { dark: "#3730A3", main: "#6366F1", pale: "#F3F4FF", accent: "#E76F51", ink: "#263238", paper: "#FFFFFF" },
  terracottaNavy: { dark: "#8A3F2D", main: "#2C5F73", pale: "#F8F5F2", accent: "#2C5F73", ink: "#263238", paper: "#FFFFFF" },
});

export const FONT = "Arial";
export const PT = Object.freeze({ deckTitle: 50, slideTitle: 35, lead: 28, subhead: 24, body: 22, caption: 16, source: 13 });
export const ptToPx = (pt) => pt * 96 / 72;

export function textStyle(pt, color, extra = {}) {
  // `fontSize` is pixels in grouped styles. Keep `fontSizePt` as explicit
  // intent for compatible runtimes and provide the correct pixel equivalent.
  return { typeface: FONT, fontSize: ptToPx(pt), fontSizePt: pt, color, ...extra };
}
