import type { ShortestConfig } from '@antiwork/shortest';
require('dotenv').config();

export default {
  headless: false,
  baseUrl: 'http://localhost:8080',
  testDir: 'app/__tests__',
  anthropicKey: process.env.ANTHROPIC_API_KEY || ''
} satisfies ShortestConfig; 