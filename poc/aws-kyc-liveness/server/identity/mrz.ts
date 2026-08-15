const MRZ_LINE_LENGTH = 30;
const CHECK_WEIGHTS = [7, 3, 1] as const;

export type MrzResult = {
  found: boolean;
  checksumsValid: boolean;
  documentNumberValid: boolean;
  dateOfBirthValid: boolean;
  expiryDateValid: boolean;
  compositeValid: boolean;
  dateOfBirth: string | null;
  name: string | null;
};

function characterValue(character: string): number {
  if (character === "<") return 0;
  if (/^[0-9]$/.test(character)) return Number(character);
  const code = character.charCodeAt(0);
  return code >= 65 && code <= 90 ? code - 55 : 0;
}

export function mrzChecksum(input: string): number {
  return Array.from(input).reduce((sum, character, index) => sum + characterValue(character) * CHECK_WEIGHTS[index % CHECK_WEIGHTS.length], 0) % 10;
}

export function checksumMatches(input: string, checkDigit: string): boolean {
  return /^\d$/.test(checkDigit) && mrzChecksum(input) === Number(checkDigit);
}

export function normalizeIdentityName(value: string): string {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().replace(/[^A-Z]/g, " ").replace(/\s+/g, " ").trim();
}

export function namesAreConsistent(left: string | null | undefined, right: string | null | undefined): boolean {
  if (!left || !right) return true;
  const leftParts = new Set(normalizeIdentityName(left).split(" ").filter(Boolean));
  const rightParts = new Set(normalizeIdentityName(right).split(" ").filter(Boolean));
  return Array.from(leftParts).every(part => rightParts.has(part)) || Array.from(rightParts).every(part => leftParts.has(part));
}

function dateFromMrz(value: string): string | null {
  if (!/^\d{6}$/.test(value)) return null;
  const year = Number(value.slice(0, 2));
  const currentTwoDigitYear = new Date().getUTCFullYear() % 100;
  const fullYear = year > currentTwoDigitYear ? 1900 + year : 2000 + year;
  const month = Number(value.slice(2, 4));
  const day = Number(value.slice(4, 6));
  const date = new Date(Date.UTC(fullYear, month - 1, day));
  if (date.getUTCFullYear() !== fullYear || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
  return `${fullYear}-${value.slice(2, 4)}-${value.slice(4, 6)}`;
}

function normalizeMrzLine(value: string): string {
  return value.toUpperCase().replace(/[^A-Z0-9<]/g, "");
}

export function extractTd1Lines(source: string): string[] | null {
  const directLines = source
    .split(/\r?\n/)
    .map(normalizeMrzLine)
    .filter(line => line.length >= MRZ_LINE_LENGTH - 2 && line.length <= MRZ_LINE_LENGTH)
    .map(line => line.padEnd(MRZ_LINE_LENGTH, "<"));
  if (directLines.length >= 3) return directLines.slice(0, 3);
  const contiguous = normalizeMrzLine(source);
  if (contiguous.length < MRZ_LINE_LENGTH * 3) return null;
  const candidate = contiguous.slice(0, MRZ_LINE_LENGTH * 3);
  return [candidate.slice(0, 30), candidate.slice(30, 60), candidate.slice(60, 90)];
}

export function parseTd1Mrz(source: string): MrzResult {
  const lines = extractTd1Lines(source);
  if (!lines) return { found: false, checksumsValid: false, documentNumberValid: false, dateOfBirthValid: false, expiryDateValid: false, compositeValid: false, dateOfBirth: null, name: null };
  const [line1, line2, line3] = lines;
  const documentNumberValid = checksumMatches(line1.slice(5, 14), line1[14]);
  const dateOfBirthValid = checksumMatches(line2.slice(0, 6), line2[6]);
  const expiryDateValid = checksumMatches(line2.slice(8, 14), line2[14]);
  const compositeInput = `${line1.slice(5, 30)}${line2.slice(0, 7)}${line2.slice(8, 15)}${line2.slice(18, 29)}`;
  const compositeValid = checksumMatches(compositeInput, line2[29]);
  const name = line3.replace(/<+/g, " ").trim() || null;
  return { found: true, checksumsValid: documentNumberValid && dateOfBirthValid && expiryDateValid && compositeValid, documentNumberValid, dateOfBirthValid, expiryDateValid, compositeValid, dateOfBirth: dateFromMrz(line2.slice(0, 6)), name };
}
