import type { NextPage } from 'next';
import Head from 'next/head';
import SmarterAssistant from '../components/SmarterAssistant';
import styles from '../styles/Smarter.module.css';

const SmarterPage: NextPage = () => {
  return (
    <div className={styles.container}>
      <Head>
        <title>Smarter Assistant</title>
        <meta name="description" content="Voice-based AI assistant using speech recognition" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <SmarterAssistant />
      </main>

      <footer className={styles.footer}>
        <p>Powered by Web Speech API and OpenAI</p>
      </footer>
    </div>
  );
};

export default SmarterPage;
