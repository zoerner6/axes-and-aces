# rebuild the website from game.html + finished videos, and push it live
O=/tmp/claude-0/-home-user/8da1ae95-9ac9-5639-830a-e1825fc256be/scratchpad; R=/home/user/axes-and-aces
cd $O && python3 gen/syncvids.py && python3 gen/buildsite.py
cp $O/site/index.html $O/site/play.html $O/site/sw.js $O/site/manifest.json $R/
mkdir -p $R/vid $R/art; rsync -a --ignore-existing $O/site/vid/ $R/vid/ 2>/dev/null || cp -n $O/site/vid/* $R/vid/
mkdir -p $R/music $R/b $R/img; cp $O/site/img/* $R/img/; cp $O/site/music/* $R/music/; cp $O/site/b/* $R/b/; cp $O/site/art/* $R/art/
cd $R && git add -A && git commit -qm "${1:-Update game}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M2qNstVto4LdKjMMy5aftL" && git push 2>&1 | tail -1
