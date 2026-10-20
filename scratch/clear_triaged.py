# One-off helper: take already-triaged NOT REBUILDABLE items off the top of the queue (skipping blocked ones),
# one commit each, until the first item that still needs work.
import subprocess, re
done = []
while True:
    L = open('queue.md', encoding='utf8').read().split('\n')
    items = [j for j, l in enumerate(L) if l.startswith('- [File:') and 'BLOCKED-ON-EXTERNAL' not in l and 'NEEDS-DECISION' not in l]
    i = items[0]; line = L[i]
    m = re.search(r' — (NOT REBUILDABLE.*)$', line)
    if not m:
        print('next:', line[:300]); break
    name = re.match(r'- \[File:([^\]]+)\]', line).group(1)
    del L[i]; open('queue.md', 'w', encoding='utf8').write('\n'.join(L))
    with open('devlog.md', 'a', encoding='utf8') as f:
        f.write(f"- File:{name}: removed from the queue; already triaged as {m.group(1)}\n")
    subprocess.run(['git', 'add', 'queue.md', 'devlog.md'], check=True)
    subprocess.run(['git', 'commit', '-q', '-m', f'{name}: off the queue (already triaged not rebuildable)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01MahXmkWSoLiEgfYsCeMKSw'], check=True)
    done.append(name)
print('removed', len(done), done)
