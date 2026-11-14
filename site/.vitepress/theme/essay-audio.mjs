export function createEssayAudioController({createAudio, urlForParagraph, onStateChange = () => {}}) {
  let audio = null;
  let generation = 0;
  let state = {status: 'idle', activeParagraph: null, failedParagraph: null};

  function emit(next) {
    state = next;
    onStateChange({...state});
  }

  function release() {
    if (!audio) return;
    audio.onplaying = null;
    audio.onended = null;
    audio.onerror = null;
    audio.pause();
    audio.removeAttribute?.('src');
    audio.src = '';
    audio.load?.();
  }

  function stop() {
    generation += 1;
    release();
    emit({status: 'idle', activeParagraph: null, failedParagraph: null});
  }

  function play(index) {
    generation += 1;
    release();
    const token = generation;
    audio ??= createAudio();
    const current = audio;
    const valid = () => token === generation && current === audio;
    const fail = () => {
      if (!valid()) return;
      release();
      emit({status: 'error', activeParagraph: index, failedParagraph: index});
    };
    current.onplaying = () => {
      if (valid()) emit({status: 'playing', activeParagraph: index, failedParagraph: null});
    };
    current.onended = () => {
      if (valid()) stop();
    };
    current.onerror = fail;
    current.src = urlForParagraph(index);
    emit({status: 'loading', activeParagraph: index, failedParagraph: null});
    Promise.resolve(current.play()).catch(fail);
  }

  function toggle(index) {
    if (state.activeParagraph === index && state.status !== 'error') stop();
    else play(index);
  }

  return {toggle, stop, getState: () => ({...state})};
}
