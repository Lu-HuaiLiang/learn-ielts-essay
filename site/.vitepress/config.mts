import {defineConfig} from 'vitepress';
import {fileURLToPath} from 'node:url';
import sidebar from './sidebar.json';
import vocabularySidebar from './vocabulary-sidebar.json';

export default defineConfig({
  lang: 'zh-CN',
  title: '雅思写作范文',
  description: '70 篇雅思英文范文与 22 个主题的词汇学习手册，支持按话题、题型和逻辑词群阅读。',
  base: process.env.SITE_BASE || '/',
  outDir: fileURLToPath(new URL('../../dist', import.meta.url)),
  cleanUrls: false,
  lastUpdated: false,
  markdown: {typographer: false},
  head: [['meta', {name: 'theme-color', content: '#ffffff'}]],
  themeConfig: {
    nav: [
      {text: '首页', link: '/'},
      {text: '按话题', link: '/topics/'},
      {text: '按题型', link: '/types/'},
      {text: '词汇学习', link: '/vocabulary/'},
    ],
    sidebar: {'/vocabulary/': vocabularySidebar, '/': sidebar},
    outline: false,
    docFooter: {prev: false, next: false},
    sidebarMenuLabel: '目录',
    returnToTopLabel: '回到顶部',
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    skipToContentLabel: '跳转到内容',
    notFound: {
      title: '页面未找到',
      quote: '请从范文目录或词汇学习目录选择内容。',
      linkLabel: '返回首页',
      linkText: '返回首页',
    },
    search: {
      provider: 'local',
      options: {
        _render(src, env, md) {
          const html = md.render(src, env);
          if (env.frontmatter?.search === false) return '';
          // VitePress expects the heading's first link to be its local anchor.
          // Keep dictionary labels as plain text in the search-only rendering.
          return html.replace(/<a\b[^>]*class="vocabulary-dictionary-link\b[^\"]*"[^>]*>([\s\S]*?)<\/a>/g, '$1');
        },
        miniSearch: {
          options: {
            // Segment Chinese definitions and group titles as well as English words.
            tokenize(text: string) {
              const segmenter = new Intl.Segmenter('zh-CN', {granularity: 'word'});
              return Array.from(segmenter.segment(text)).filter(part => part.isWordLike).map(part => part.segment);
            },
          },
        },
        locales: {
          root: {
            translations: {
              button: {buttonText: '搜索', buttonAriaLabel: '搜索内容'},
              modal: {
                displayDetails: '显示详细列表',
                resetButtonTitle: '清空搜索',
                backButtonTitle: '关闭搜索',
                noResultsText: '没有找到相关内容',
                footer: {selectText: '选择', navigateText: '切换', closeText: '关闭'},
              },
            },
          },
        },
      },
    },
  },
});
