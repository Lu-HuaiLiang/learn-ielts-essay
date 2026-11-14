const prefix = 'ielts-vocabulary.story-progress.v1.';
const defaultPosition = () => ({visible: 1, scrollTop: 0});
const scrollPosition = value => Number.isFinite(value) && value >= 0 ? value : 0;

export function loadStoryProgress(chapter, steps, storage = () => window.localStorage) {
  try {
    const saved = JSON.parse(storage().getItem(prefix + chapter));
    const index = steps.findIndex(step => step.id === saved?.wordId);
    return index < 0 ? defaultPosition() : {visible: index + 1, scrollTop: scrollPosition(saved.scrollTop)};
  } catch {
    return defaultPosition();
  }
}

export function saveStoryProgress(chapter, wordId, scrollTop, storage = () => window.localStorage) {
  try {
    storage().setItem(prefix + chapter, JSON.stringify({wordId, scrollTop: scrollPosition(scrollTop)}));
  } catch { /* Keep the current reading session usable if browser storage is unavailable. */ }
}
