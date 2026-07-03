const configuredApiBase = ((import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '')
  .trim()
  .replace(/\/+$/, '');

const pointsToLocalBackend =
  /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(configuredApiBase);

export const API_BASE_URL =
  !configuredApiBase || (import.meta.env.PROD && pointsToLocalBackend)
    ? '/api'
    : configuredApiBase;

export const apiUrl = (path: string): string => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};
