"""Pass 2 + 3 jobs for the new worlds: knocked-out pictures and video starting frames."""
import json, os
W = json.load(open("worlds/worlds.json")); jobs = []
for w in W:
    for i, a in enumerate(w["areas"]):
        bgu = f"wraw/bg_{w['id']}_{i}.url"
        for m in a["pool"] + [a["boss"]]:
            mu = f"wraw/m_{m['slug']}.url"
            if not os.path.exists(mu) or not os.path.exists(bgu): continue
            mr, br = open(mu).read().strip(), open(bgu).read().strip()
            jobs.append({"id": f"ko_{m['slug']}", "ar": "1:1", "refs": [mr], "prompt": f"The same comic creature as in the second reference image ({m['desc']}), knocked out cold after losing a fight: lying sprawled flat on the ground in a crumpled heap, fully lying down and limp, not standing, dazed with X-shaped eyes, its weapon dropped beside it if it has one, battered and bruised with torn edges. Correct anatomy: exactly one head and one body, the same number of limbs as the reference. Cartoon comic style, side view, whole body visible, isolated on a plain flat pure white background, no scenery, no text, no signs."})
            jobs.append({"id": f"frame_{m['slug']}", "ar": "16:9", "refs": [mr, br], "prompt": f"Cinematic wide shot for a game battle scene: the exact creature from the second reference image ({m['desc']}) stands in the middle of the exact place from the third reference image, facing the viewer in a menacing fighting stance, full body visible from head to feet with space around it. Keep the place exactly as in the third reference image. Only this one creature, no other characters, no text, no signs."})
json.dump(jobs, open("gen/jobsW2.json", "w")); print(len(jobs))
