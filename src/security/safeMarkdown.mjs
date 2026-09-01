const SAFE_LINK_PROTOCOLS = new Set(['http:', 'https:', 'mailto:']);
const SAFE_IMAGE_PROTOCOLS = new Set(['http:', 'https:']);

export function safeMarkdownUrl(url, key) {
  const value = typeof url === 'string' ? url.trim() : '';
  if (!value) return '';

  if (
    value.startsWith('#') ||
    value.startsWith('/') ||
    value.startsWith('./') ||
    value.startsWith('../')
  ) {
    return value;
  }

  if (!/^[a-zA-Z][a-zA-Z\d+.-]*:/.test(value)) {
    return value;
  }

  try {
    const parsed = new URL(value);
    const allowedProtocols = key === 'src' ? SAFE_IMAGE_PROTOCOLS : SAFE_LINK_PROTOCOLS;
    return allowedProtocols.has(parsed.protocol.toLowerCase()) ? value : '';
  } catch {
    return '';
  }
}
