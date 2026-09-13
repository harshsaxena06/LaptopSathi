export type StrengthLevel = 0 | 1 | 2 | 3 | 4;

export interface PasswordStrength {
  score: StrengthLevel; // 0 = very weak .. 4 = very strong
  label: string;
}

/**
 * A lightweight, dependency-free heuristic (not a full zxcvbn port). Scores
 * length, character-class variety, and penalizes obvious repeated/sequential
 * patterns. Good enough to give the user real-time, honest feedback without
 * shipping a large wordlist to the client.
 */
export function calculatePasswordStrength(password: string): PasswordStrength {
  if (!password) return { score: 0, label: '' };

  let points = 0;
  if (password.length >= 8) points += 1;
  if (password.length >= 12) points += 1;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) points += 1;
  if (/\d/.test(password)) points += 1;
  if (/[^A-Za-z0-9]/.test(password)) points += 1;

  const hasRepeats = /(.)\1{2,}/.test(password);
  const hasSequence = /(012|123|234|345|456|567|678|789|abc|bcd|cde|qwe|asd)/i.test(password);
  if (hasRepeats || hasSequence) points -= 1;

  const score = Math.max(0, Math.min(4, points)) as StrengthLevel;
  const labels = ['Very weak', 'Weak', 'Fair', 'Strong', 'Very strong'];
  return { score, label: labels[score] };
}
