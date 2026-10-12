const {themes: prismThemes} = require('prism-react-renderer');

const config = {
  title: 'piri',
  tagline: 'Compress. Extract. Inspect. Benchmark. Securely.',
  favicon: 'img/favicon.svg',
  url: 'https://wxguy.github.io',
  baseUrl: '/piri/',
  organizationName: 'wxguy',
  projectName: 'piri',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',
  trailingSlash: false,
  i18n: {defaultLocale: 'en', locales: ['en']},
  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: 'docs',
          sidebarPath: './sidebars.js',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          breadcrumbs: true,
          remarkPlugins: [],
        },
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      },
    ],
  ],
  themeConfig: {
    image: 'img/piri-social-card.svg',
    metadata: [
      {name: 'keywords', content: 'piri, archive, compression, tar, zip, zstd, 7z, CLI, backup, security'},
      {name: 'description', content: 'piri is a cross-platform, security-conscious archive and extraction utility with native backends and benchmark-driven selection.'},
    ],
    navbar: {
      title: 'piri',
      logo: {alt: 'piri logo', src: 'img/logo.svg'},
      items: [
        {to: '/docs/getting-started/installation', label: 'Get Started', position: 'left'},
        {to: '/docs/user-guide/usage', label: 'User Guide', position: 'left'},
        {to: '/docs/formats/supported-formats', label: 'Formats', position: 'left'},
        {to: '/docs/backends/architecture', label: 'Backends', position: 'left'},
        {to: '/docs/reference/cli', label: 'CLI Reference', position: 'left'},
        {to: '/docs/development/development-guide', label: 'Development', position: 'left'},
        {href: 'https://github.com/wxguy/piri', label: 'GitHub', position: 'right'},
        {href: 'https://github.com/wxguy/piri/releases', label: 'Downloads', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {title: 'Documentation', items: [
          {label: 'Installation', to: '/docs/getting-started/installation'},
          {label: 'Quick Start', to: '/docs/getting-started/quickstart'},
          {label: 'Formats', to: '/docs/formats/supported-formats'},
          {label: 'Security', to: '/docs/security/security-model'},
        ]},
        {title: 'Project', items: [
          {label: 'GitHub', href: 'https://github.com/wxguy/piri'},
          {label: 'Downloads', href: 'https://github.com/wxguy/piri/releases'},
          {label: 'WxGuy', href: 'https://wxguy.in/'},
          {label: 'Issues', href: 'https://github.com/wxguy/piri/issues'},
        ]},
        {title: 'More', items: [
          {label: 'Credits', to: '/docs/support/credits'},
          {label: 'License', to: '/docs/support/license'},
        ]},
      ],
      copyright: `Copyright © ${new Date().getFullYear()} WxGuy. Released under the MIT License.`,
    },
    prism: {theme: prismThemes.github, darkTheme: prismThemes.dracula},
    colorMode: {defaultMode: 'dark', disableSwitch: false, respectPrefersColorScheme: true},
    docs: {sidebar: {hideable: true, autoCollapseCategories: true}},
    tableOfContents: {minHeadingLevel: 2, maxHeadingLevel: 4},
    announcementBar: {
      id: 'piri20',
      content: 'piri 1.0.0 — initial piri release with broad format coverage and benchmark-driven selection.',
      backgroundColor: '#0b1220',
      textColor: '#dbeafe',
      isCloseable: true,
    },
  },
};

module.exports = config;
