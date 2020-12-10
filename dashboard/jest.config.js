module.exports = {
  preset: "@vue/cli-plugin-unit-jest/presets/typescript-and-babel",
  collectCoverage: true,
  collectCoverageFrom: ["<rootDir>/src/**/*.ts", "<rootDir>/src/**/*.vue"],
  coverageReporters: ["lcovonly"],
  moduleFileExtensions: ["ts", "vue", "js"]
};
