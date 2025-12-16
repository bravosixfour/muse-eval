# MUSE Model Evaluation Sheet

Generated: 2025-12-16T13:30:55.031470

Model: qwen/qwen-image-edit-plus

---

## Scoring Guide
- **5**: Excellent - Meets all criteria, production quality
- **4**: Good - Minor issues, usable for concept work
- **3**: Acceptable - Noticeable issues but intent clear
- **2**: Poor - Major issues, needs regeneration
- **1**: Failed - Unusable result

---


## Precise Scale

### Sofa sizing - specific dimensions
**Test ID:** scale_001
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `scale_001_132615.png`

**Prompt:**
> Replace the sofa with a large sectional that fills approximately 70% of the wall width. The sectional should be L-shaped, facing right, in warm gray bouclé fabric. Maintain proper scale relative to the coffee table and rug.

**Success Criteria:**
- [ ] Sofa proportionally sized to wall (not too big/small)
- [ ] L-shape orientation correct
- [ ] Scale relationship with other furniture maintained
- [ ] Fabric texture visible

**Failure Indicators:**
- [ ] Sofa obviously wrong scale
- [ ] Floating or clipping into floor
- [ ] Other furniture distorted

**Score:** ___/5

**Notes:**
```

```

---

### Pendant light height
**Test ID:** scale_002
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `scale_002_132628.png`

**Prompt:**
> Add a large globe pendant light centered above the dining table. The pendant should hang at standard dining height - low enough to illuminate the table but high enough to not obstruct views across the table. Warm brass finish, frosted glass globe approximately 50cm diameter.

**Success Criteria:**
- [ ] Pendant centered over table
- [ ] Height looks appropriate for dining
- [ ] Scale proportional to table size
- [ ] Brass/glass materials visible

**Failure Indicators:**
- [ ] Pendant too high (near ceiling) or too low (in face)
- [ ] Dramatically wrong size
- [ ] Off-center placement

**Score:** ___/5

**Notes:**
```

```

---


## Product Replication

### Chair from reference
**Test ID:** product_001
**Difficulty:** very_hard
**Status:** ✅ Generated
**Output:** `product_001_132645.png`

**Prompt:**
> Place the tufted accent chair from the reference image in the corner by the window, replacing the existing armchair. Match the exact design - button tufting, curved back, turned legs. Position angled toward the room. The chair should integrate naturally with the room's lighting.

**Success Criteria:**
- [ ] Recognizable as the reference chair style
- [ ] Correct proportions and details
- [ ] Button tufting visible
- [ ] Turned legs present
- [ ] Natural lighting integration

**Failure Indicators:**
- [ ] Generic chair instead of reference style
- [ ] Wrong proportions or details
- [ ] Tufting missing
- [ ] Materials clearly wrong

**Score:** ___/5

**Notes:**
```

```

---

### Chair style in dining room
**Test ID:** product_002
**Difficulty:** very_hard
**Status:** ✅ Generated
**Output:** `product_002_132703.png`

**Prompt:**
> Replace the dining chairs with chairs matching the style from the reference image - elegant tufted design with turned legs. Keep the same count of chairs and their positions around the table. Scale appropriately for dining height.

**Success Criteria:**
- [ ] Chair design matches reference style
- [ ] Tufting preserved
- [ ] Leg style accurate
- [ ] Correct count of chairs
- [ ] Scale appropriate for dining

**Failure Indicators:**
- [ ] Generic chairs generated
- [ ] Key design features lost
- [ ] Wrong proportions

**Score:** ___/5

**Notes:**
```

```

---


## Multi-Element

### Full room transformation - 4 changes
**Test ID:** complex_001
**Difficulty:** very_hard
**Status:** ✅ Generated
**Output:** `complex_001_132717.png`

**Prompt:**
> Transform this space: 1) Change wall color to deep forest green, 2) Replace sofa with cream linen sectional, 3) Add a large vintage Persian rug in reds and blues, 4) Swap the coffee table for a round marble-top table with brass base. Keep the existing lighting and artwork.

**Success Criteria:**
- [ ] Wall color changed to green
- [ ] Sofa replaced with cream sectional
- [ ] Persian rug added with correct colors
- [ ] Coffee table is round marble/brass
- [ ] Lighting and artwork preserved

**Failure Indicators:**
- [ ] Only some changes applied
- [ ] Elements that should be preserved were changed
- [ ] Incoherent result / visual chaos
- [ ] Items missing entirely

**Score:** ___/5

**Notes:**
```

```

---

### Kitchen renovation - surfaces + hardware
**Test ID:** complex_002
**Difficulty:** very_hard
**Status:** ✅ Generated
**Output:** `complex_002_132732.png`

**Prompt:**
> Renovate this kitchen: Replace countertops with white Calacatta marble with dramatic gray veining. Change cabinet color to deep navy blue with satin finish. Replace all hardware with unlacquered brass pulls and knobs. Keep backsplash, appliances, and layout exactly as is.

**Success Criteria:**
- [ ] Countertops are white marble with veining
- [ ] Cabinets are navy blue
- [ ] Hardware appears brass
- [ ] Backsplash unchanged
- [ ] Appliances unchanged

**Failure Indicators:**
- [ ] Marble looks generic/plastic
- [ ] Hardware missing or wrong
- [ ] Backsplash or appliances modified
- [ ] Layout changed

**Score:** ___/5

**Notes:**
```

```

---


## Photorealistic Integration

### Shadow and lighting consistency
**Test ID:** realism_001
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `realism_001_132745.png`

**Prompt:**
> Add a tall floor lamp with a linen drum shade in the corner to the right of the sofa. The lamp should cast realistic shadows consistent with the existing lighting in the room. Brushed nickel base, warm white light glowing through the shade.

**Success Criteria:**
- [ ] Floor lamp placed correctly
- [ ] Shadow direction matches room lighting
- [ ] Light glow through shade visible
- [ ] Materials look realistic
- [ ] Edges clean (not floating/clipping)

**Failure Indicators:**
- [ ] No shadow or wrong direction
- [ ] Lamp appears pasted/floating
- [ ] Harsh edges / obvious compositing
- [ ] Material looks CG/fake

**Score:** ___/5

**Notes:**
```

```

---

### Reflection and material interaction
**Test ID:** realism_002
**Difficulty:** very_hard
**Status:** ✅ Generated
**Output:** `realism_002_132757.png`

**Prompt:**
> Replace the coffee table with a glass-top table with polished chrome legs. The glass should show realistic reflections of the room - the ceiling, nearby furniture, windows. Chrome legs should reflect the floor and surroundings.

**Success Criteria:**
- [ ] Glass transparency correct
- [ ] Reflections visible on glass
- [ ] Chrome shows environmental reflections
- [ ] Table integrates naturally
- [ ] Proportions correct

**Failure Indicators:**
- [ ] Glass looks solid/opaque
- [ ] No reflections
- [ ] Chrome looks matte/painted
- [ ] Obvious fake integration

**Score:** ___/5

**Notes:**
```

```

---


## Consistency

### Same edit, three runs
**Test ID:** consistency_001
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `consistency_001_132814.png`

**Prompt:**
> Change the sofa to a mid-century modern style in mustard yellow velvet. Wooden tapered legs, clean lines, slightly angled back. Keep everything else exactly the same.

**Success Criteria:**
- [ ] Sofa is mid-century style
- [ ] Color is mustard yellow
- [ ] Velvet texture visible
- [ ] Wooden legs present

**Failure Indicators:**
- [ ] Drastically different results each run
- [ ] Style inconsistent between runs
- [ ] Color varies significantly

**Score:** ___/5

**Notes:**
```

```

---

### Same edit, three runs
**Test ID:** consistency_001_run2
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `consistency_001_run2_132830.png`

**Prompt:**
> Change the sofa to a mid-century modern style in mustard yellow velvet. Wooden tapered legs, clean lines, slightly angled back. Keep everything else exactly the same.

**Success Criteria:**
- [ ] Sofa is mid-century style
- [ ] Color is mustard yellow
- [ ] Velvet texture visible
- [ ] Wooden legs present

**Failure Indicators:**
- [ ] Drastically different results each run
- [ ] Style inconsistent between runs
- [ ] Color varies significantly

**Score:** ___/5

**Notes:**
```

```

---

### Same edit, three runs
**Test ID:** consistency_001_run3
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `consistency_001_run3_132843.png`

**Prompt:**
> Change the sofa to a mid-century modern style in mustard yellow velvet. Wooden tapered legs, clean lines, slightly angled back. Keep everything else exactly the same.

**Success Criteria:**
- [ ] Sofa is mid-century style
- [ ] Color is mustard yellow
- [ ] Velvet texture visible
- [ ] Wooden legs present

**Failure Indicators:**
- [ ] Drastically different results each run
- [ ] Style inconsistent between runs
- [ ] Color varies significantly

**Score:** ___/5

**Notes:**
```

```

---


## Material Transfer

### Stone sample to countertop
**Test ID:** material_001
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `material_001_132857.png`

**Prompt:**
> Replace the kitchen countertops with the marble from the reference image. Match the exact vein pattern, color, and finish. Apply consistently across all counter surfaces including the island. Maintain edge profile and thickness.

**Success Criteria:**
- [ ] Marble resembles reference sample
- [ ] Vein pattern similar
- [ ] Color tone matches
- [ ] Applied to all counter surfaces
- [ ] Looks like continuous slab

**Failure Indicators:**
- [ ] Generic marble generated
- [ ] Veining doesn't match
- [ ] Color significantly off
- [ ] Inconsistent application

**Score:** ___/5

**Notes:**
```

```

---

### Fabric sample to upholstery
**Test ID:** material_002
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `material_002_132920.png`

**Prompt:**
> Reupholster the sofa with the fabric from the reference image. Match the exact color, texture, and pattern. The fabric should drape naturally showing the texture and any pattern at the correct scale for furniture.

**Success Criteria:**
- [ ] Fabric color matches reference
- [ ] Texture/pattern visible
- [ ] Scale appropriate for sofa
- [ ] Natural drape and folds
- [ ] Consistent across all cushions

**Failure Indicators:**
- [ ] Color significantly different
- [ ] Pattern missing or wrong scale
- [ ] Flat/unrealistic application
- [ ] Inconsistent across surfaces

**Score:** ___/5

**Notes:**
```

```

---


## Style Transfer

### Japandi transformation
**Test ID:** style_001
**Difficulty:** medium
**Status:** ✅ Generated
**Output:** `style_001_133023.png`

**Prompt:**
> Transform this room to match the Japandi aesthetic from the reference image. Apply: low-profile furniture forms, warm light wood tones, neutral color palette with black accents, natural textures (linen, wool, wood), deliberate negative space, minimal ornamentation. Preserve room architecture.

**Success Criteria:**
- [ ] Overall Japandi feel achieved
- [ ] Low-profile furniture
- [ ] Warm neutral palette
- [ ] Natural materials visible
- [ ] Space feels intentionally minimal
- [ ] Room architecture preserved

**Failure Indicators:**
- [ ] Style doesn't read as Japandi
- [ ] Too cluttered or too empty
- [ ] Colors wrong for style
- [ ] Architecture modified

**Score:** ___/5

**Notes:**
```

```

---


## Edge Cases

### Preserve specific elements
**Test ID:** edge_001
**Difficulty:** hard
**Status:** ✅ Generated
**Output:** `edge_001_133035.png`

**Prompt:**
> Change ONLY the wall color to warm white. Keep absolutely everything else exactly as is - all furniture, art, lighting, flooring, window treatments, decor items. Nothing should move or change except the wall color.

**Success Criteria:**
- [ ] Wall color changed
- [ ] Every single other element identical
- [ ] No furniture moved
- [ ] Art/decor unchanged
- [ ] Lighting unchanged

**Failure Indicators:**
- [ ] Other elements modified
- [ ] Furniture positions changed
- [ ] Items removed or added
- [ ] Lighting/mood shifted

**Score:** ___/5

**Notes:**
```

```

---

### Remove single object cleanly
**Test ID:** edge_002
**Difficulty:** medium
**Status:** ✅ Generated
**Output:** `edge_002_133052.png`

**Prompt:**
> Remove the coffee table completely. Fill the space naturally with continuous flooring matching the existing floor exactly. Do not add anything new. All other furniture and decor must remain exactly in place.

**Success Criteria:**
- [ ] Coffee table removed
- [ ] Floor filled in naturally
- [ ] Floor matches existing
- [ ] Nothing else changed
- [ ] No artifacts where table was

**Failure Indicators:**
- [ ] Table partially visible
- [ ] Floor fill obvious/wrong
- [ ] Other furniture moved
- [ ] Artifacts or smearing

**Score:** ___/5

**Notes:**
```

```

---
