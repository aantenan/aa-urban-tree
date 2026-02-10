module.exports = {
  root: true,
  env: { browser: true, es2022: true },
  extends: ['eslint:recommended', 'plugin:react/recommended', 'plugin:react/jsx-runtime'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: '18' } },
  plugins: ['react'],
  rules: {
    'react/prop-types': 'off',
  },
};
