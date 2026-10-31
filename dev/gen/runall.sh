cd /tmp/claude-0/-home-user/8da1ae95-9ac9-5639-830a-e1825fc256be/scratchpad
(cd gen && python3 kie.py jobsW2.json ../wraw2 >> logW2.txt 2>&1)
python3 gen/procW.py wraw >> gen/procW.log 2>&1
python3 gen/procW.py wraw2 >> gen/procW.log 2>&1
