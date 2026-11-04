"""Build everything, in order. Run: python src/make.py

Nothing in the game is written to. This only reads dev/game.html and art/.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ('extract.py', 'read the roster out of the game'),
    ('build_blocks.py', 'turn the game numbers into stat blocks'),
    ('panels.py', 'composite each monster into its scene'),
    ('storeart.py', 'the store cover image'),
    ('book.py', 'lay out the PDF (two passes, a few minutes)'),
    ('foundry.py', 'the free Foundry VTT module'),
]


def main():
    for script, what in STEPS:
        print('\n=== %s  (%s)' % (script, what))
        t = time.time()
        r = subprocess.run([sys.executable, os.path.join(HERE, script)] + sys.argv[1:],
                           cwd=HERE)
        if r.returncode:
            print('FAILED at %s' % script)
            return r.returncode
        print('    %.0fs' % (time.time() - t))
    print('\nall done')
    return 0


if __name__ == '__main__':
    sys.exit(main())
