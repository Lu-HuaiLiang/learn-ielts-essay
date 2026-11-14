import {generateSite} from './essay-library.mjs';
import {generateVocabulary} from './vocabulary-library.mjs';

const result = await generateSite();
console.log(`Generated ${result.pages} document pages: ${result.essays} essays, ${result.topics} topics, ${result.types} question types.`);
const vocabulary = await generateVocabulary();
console.log(`Generated ${vocabulary.pages} vocabulary pages: ${vocabulary.chapters} chapters, ${vocabulary.groups} groups, ${vocabulary.records} records (${vocabulary.distinctWords} distinct words).`);
