import React from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

const features = [
  ['⚡', 'Native performance', 'Use mature system compressors and archive utilities when they provide better performance or format coverage.'],
  ['🛡️', 'Security first', 'Validate paths, limits and overwrite policy before extraction. Keep unsafe archives from becoming unsafe filesystem operations.'],
  ['🧭', 'One interface', 'Create, extract, inspect, test and detect archives through one predictable command-line interface.'],
  ['📊', 'Benchmark driven', 'Measure compression size, speed and extraction performance on your own data before choosing a format.'],
  ['🌐', 'Cross-platform', 'Use piri on Linux, macOS and Windows through standalone releases.'],
  ['🧩', 'Extensible', 'Use the backend registry and plugin entry points to add capabilities without redesigning the CLI.'],
];

function Feature({icon, title, children}) {
  return <div className={styles.feature}>
    <div className={styles.featureIcon}>{icon}</div>
    <Heading as="h3">{title}</Heading>
    <p>{children}</p>
  </div>;
}

export default function Home() {
  return <Layout title="Universal Archive Utility" description="A modern, secure and benchmark-driven archive utility for Linux, macOS and Windows.">
    <main>
      <header className={styles.hero}>
        <div className="container">
          <div className={styles.eyebrow}>PIRI 1.0.0 · OPEN SOURCE · MIT</div>
          <Heading as="h1">Compress. Extract.<br/><span>Inspect. Benchmark.</span></Heading>
          <p className={styles.heroText}>
            A modern archive and extraction utility that combines a simple CLI,
            native backends, strong extraction policies and benchmark-driven selection.
          </p>
          <div className={styles.buttons}>
            <Link className="button button--primary button--lg" to="/docs/getting-started/installation">Get started</Link>
            <Link className="button button--secondary button--lg" to="/docs/getting-started/quickstart">Quick start</Link>
            <a className="button button--secondary button--lg" href="https://github.com/wxguy/piri">View on GitHub</a>
          </div>
          <div className={styles.terminal}>
            <div className={styles.terminalBar}><span/><span/><span/><em>terminal</em></div>
            <pre><code>{`$ curl -fsSL https://wxguy.github.io/piri/install.sh | bash
$ piri -i my-data -o backup.tar.zst
$ piri -t backup.tar.zst
✓ archive integrity test passed`}</code></pre>
          </div>
        </div>
      </header>

      <section className={styles.stats}>
        <div className="container">
          <div className={styles.statGrid}>
            <div><strong>50+</strong><span>format families</span></div>
            <div><strong>3</strong><span>major desktop platforms</span></div>
            <div><strong>2</strong><span>installation models</span></div>
            <div><strong>1</strong><span>consistent CLI</span></div>
          </div>
        </div>
      </section>

      <section className="container padding-vert--xl">
        <div className={styles.sectionIntro}>
          <div className={styles.kicker}>BUILT FOR REAL WORK</div>
          <Heading as="h2">Simple for beginners. Serious for experts.</Heading>
          <p>Start with three commands or dive into backend capabilities, security policies, benchmarks and the Python API.</p>
        </div>
        <div className={styles.features}>
          {features.map(([icon, title, text]) => <Feature key={title} icon={icon} title={title}>{text}</Feature>)}
        </div>
      </section>

      <section className={styles.darkBand}>
        <div className="container">
          <div className={styles.split}>
            <div>
              <div className={styles.kicker}>CHOOSE YOUR PATH</div>
              <Heading as="h2">Documentation for every level</Heading>
          <p>From installing piri to writing a backend plugin, the documentation follows the way people actually use it.</p>
            </div>
            <div className={styles.pathGrid}>
              <Link to="/docs/getting-started/installation"><b>New user</b><span>Install and make your first archive →</span></Link>
              <Link to="/docs/getting-started/backend-installation"><b>System administrator</b><span>Install native backends by OS →</span></Link>
              <Link to="/docs/reference/cli"><b>Power user</b><span>Master the complete CLI →</span></Link>
              <Link to="/docs/development/architecture"><b>Developer</b><span>Understand and extend piri →</span></Link>
            </div>
          </div>
        </div>
      </section>

      <section className="container padding-vert--xl">
        <div className={styles.sectionIntro}>
          <div className={styles.kicker}>KNOW WHAT YOU HAVE</div>
          <Heading as="h2">Formats and backends stay visible</Heading>
          <p>piri separates format recognition from backend availability and operation capabilities. No guessing from file extensions alone.</p>
          <div className={styles.buttons}>
            <Link className="button button--primary" to="/docs/formats/compatibility-matrix">Format matrix</Link>
            <Link className="button button--secondary" to="/docs/backends/capabilities">Backend capabilities</Link>
          </div>
        </div>
      </section>
    </main>
  </Layout>;
}
