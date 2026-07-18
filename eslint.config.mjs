import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = [
  {
    ignores: [
      ".agents/**",
      ".claude/**",
      ".codex/**",
      ".next/**",
      "backend/.venv/**",
      "pred-market-design/**"
    ]
  },
  ...nextVitals,
  ...nextTs
];

export default eslintConfig;
