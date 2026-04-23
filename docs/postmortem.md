# Invasion Spacers — Postmortem

- **Team:** TEAM E
- **Members:** Armando Hernandez, Asad Tirmizi, Malec Basel Tarabein, Mahran Alkhalil.
- **Date:** 04/22/2026

---

## What went well

### 1. The core loop became much stronger after the level and leader structure was added.

Early versions of the game felt like a simple shooter with repetitive waves. The later levels structure, stronger leaders, defense line phase, and clear wave progression made the game feel like a complete arcade loop instead of a one scene prototype. This also made the game more exciting because of the leader and leader defense line encounters.

### 2. Audio and feedback added a lot of value once the game was already stable.

The project improved significantly when sounds, ambience, cues, pickup feedback, hit flashes, and transition overlays were added after the gameplay loop was already working. The game feels much more responsive and readable now than it did before the feedback pass.

### 3. The visual upgrade made the game feel much more complete.

The game improved a lot when the basic look was replaced with level backgrounds, player ships, enemies, leaders, bullets, and powerup icons. Before that pass, the game worked mechanically but still looked more like a prototype. After the visual pass, each level felt more distinct, the HUD looked more connected to the space theme, and the game felt closer to a real space .

---

## What went wrong

### 1. Late-stage polish exposed many small interaction bugs

Once the project had menus, audio, powerups, leaders, score saving, and multiple states, many small bugs appeared. Examples included black screen softlocks, overlay spacing problems, sound replay bugs, score entry menu overlap, and guard phase problems. None of these were individually huge, but together they took a lot of time to find and clean up.

### 2. Enemy wave behavior

The early grid-style wave layout was too basic and was also called out during feedback. We spent time adjusting formations and movement multiple times before the enemies started to feel less scripted and more alive. This slowed progress because wave behavior was closely connected to difficulty, firing, and level pacing, so every change affected several parts of the game at once.

### 3. Portability issues appeared late.

The project ran well on the development machine, but a dry run on another Mac exposed a Python compatibility problem caused by newer type-hint syntax. The repo structure also needed a final cleanup because the project root had become crowded over time. This showed that packaging and portability checks should have been done earlier instead of waiting until the end.

---

## What we would change

- We would lock the enemy-wave design earlier and stop reworking it after it reached the “good enough and fun” stage.
- We would do a real dry run on another machine earlier, especially after major structure changes.
- We would move to the cleaner `src/` structure earlier in the project so the repo stayed organized throughout development instead of being cleaned up near the end.
- We would create a stricter feature cutoff after the core loop, then spend the rest of the time only on tuning, bug fixing, and documentation.

---

## Iteration evidence

### Before

The wave formations were too grid-like and felt basic. Feedback during development also pointed out that the opening combat looked repetitive and did not create much pressure or variety.

### Change

Enemy wave behavior was revised several times. Entry behavior was changed so enemies appear from different places, move into the play field more dynamically, and create more pressure through varied firing and movement. Leaders were also expanded with a defense-line phase and more intentional pacing.

### After

The game now has a much clearer progression arc. Level transitions are more readable, the leaders feel more like real set-piece moments, and normal waves feel less static. Playtesting during later iterations showed that the game felt faster, more exciting, and more complete than the earlier version.

