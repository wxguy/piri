const sidebars = {
  docs: [
    'intro',
    {
      type: 'category', label: 'Getting Started', collapsed: false, items: [
        'getting-started/installation',
        'getting-started/platforms',
        'getting-started/backend-installation',
        'getting-started/quickstart',
        'getting-started/concepts',
        'getting-started/standalone',
      ],
    },
    {
      type: 'category', label: 'User Guide', collapsed: false, items: [
        'user-guide/usage',
        'user-guide/practical-recipes',
        'user-guide/automation',
      ],
    },
    {
      type: 'category', label: 'Formats', items: [
        'formats/supported-formats',
        'formats/compatibility-matrix',
      ],
    },
    {
      type: 'category', label: 'Backends', items: [
        'backends/architecture',
        'backends/capabilities',
        'backends/troubleshooting',
      ],
    },
    {
      type: 'category', label: 'Security', items: [
        'security/security-model',
        'security/integrity',
        'security/resource-limits',
      ],
    },
    {
      type: 'category', label: 'Benchmarking', items: [
        'benchmarking/methodology',
        'benchmarking/recipes',
      ],
    },
    {
      type: 'category', label: 'Reference', items: [
        'reference/cli',
        'reference/configuration',
        'reference/api',
        'reference/environment',
        'reference/exit-codes',
      ],
    },
    {
      type: 'category', label: 'Development', items: [
        'development/architecture',
        'development/development-guide',
        'development/contributing',
        'development/backend-development',
        'development/testing',
        'development/local-testing',
      ],
    },
    {
      type: 'category', label: 'Releases', items: [
        'releases/changelog',
        'releases/releasing',
        'releases/documentation-site',
      ],
    },
    {
      type: 'category', label: 'Support', items: [
        'support/faq',
        'support/troubleshooting',
        'support/help',
        'support/credits',
        'support/license',
      ],
    },
  ],
};

module.exports = sidebars;
