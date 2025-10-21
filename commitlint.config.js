module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Make scope optional for docs type
    'scope-empty': [0],

    // Validate scope when provided
    'scope-enum': [
      2,
      'always',
      [
        'framework',  // Core framework documentation
        'guides',     // Implementation/quickstart guides
        'examples',   // Example content
        'readme',     // README and project overview
        'config',     // Configuration files
        'tooling',    // Development tools and automation
      ],
    ],
    'type-enum': [
      2,
      'always',
      [
        'docs',     // Documentation updates and additions
        'fix',      // Fix errors or issues in content
        'refactor', // Restructure or reorganize content
        'chore',    // Maintenance tasks
        'feat',     // New content or features
      ],
    ],
    'subject-case': [2, 'always', 'sentence-case'],
  },
};
