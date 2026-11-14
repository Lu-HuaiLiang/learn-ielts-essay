import DefaultTheme from 'vitepress/theme';
import {inBrowser} from 'vitepress';
import EssayReader from './EssayReader.vue';
import VocabularyReader from './VocabularyReader.vue';
import VocabularyStories from './VocabularyStories.vue';
import NotesLayout from './NotesLayout.vue';
import '../../../mubu-editor/src/fonts.css';
import './style.css';

export default {
  extends: DefaultTheme,
  Layout: NotesLayout,
  enhanceApp({app, router}) {
    app.component('EssayReader', EssayReader);
    app.component('VocabularyReader', VocabularyReader);
    app.component('VocabularyStories', VocabularyStories);
    if (inBrowser) {
      const previous = router.onAfterRouteChange ?? router.onAfterRouteChanged;
      router.onAfterRouteChange = async to => {
        await previous?.(to);
        window.dispatchEvent(new Event('vocabulary-route-ready'));
      };
    }
  },
};
