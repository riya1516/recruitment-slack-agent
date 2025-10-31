/**
 * アプリケーション設定
 */

// API Base URL
// 本番環境ではVITE_API_URLから取得、なければ相対パス（Renderの同一ドメイン前提）
// 開発環境ではlocalhost:8000を使用
export const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000/api/v1' : '/api/v1');

console.log('API Base URL:', API_BASE_URL);
