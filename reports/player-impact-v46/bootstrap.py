from pathlib import Path
root=Path('reports/player-impact-v46');old=Path('reports/player-impact-v45')
worker=(old/'worker.mjs').read_text(encoding='utf-8').replace("from './engine.mjs'","from '../player-impact-v45/engine.mjs'").replace("from './fine-collector.mjs'","from '../player-impact-v45/fine-collector.mjs'")
(root/'worker.mjs').write_text(worker,encoding='utf-8')
score=(old/'score.py').read_text(encoding='utf-8').replace('player-impact-v45','player-impact-v46').replace("'v45'","'v46'").replace('-v45-', '-v46-')
(root/'score.py').write_text(score,encoding='utf-8')
fine=(old/'score-fine.py').read_text(encoding='utf-8').replace("ROOT=Path('reports/player-impact-v45')","ROOT=Path('reports/player-impact-v46')").replace("source=read(ROOT/'make-evaluation.json')","source=read(Path('reports/player-impact-v45/make-evaluation.json'))").replace("choice=read(ROOT/'choice-evaluation.json')","choice=read(Path('reports/player-impact-v45/choice-evaluation.json'))").replace('-v45-','-v46-')
(root/'score-fine.py').write_text(fine,encoding='utf-8')
