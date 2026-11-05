# EDF EPR2 ship / hatch-geometry research register — 2026-11-05

**Scope.** This is a non-destructive research record for future berth, hull, hatch, hold, crane-outreach and cargo-access analysis. It supplements (does not overwrite) the existing repo and the project Excel model.

**Project inputs supplied by the user:** CE cargo mass **500 t** (not 110 t from the old repo README); GV cargo mass 580 t; PP 154 t. Preliminary lifting accessories CE/GV +30 t, PP +15.5 t. LR 11350 selected **SLDB 54 and 60 m** with **B suspended derrick ballast 600 t at 25 m**. Crane longitudinal X=90 m from start of allowed 154 m quay envelope; 5 m docking stations and both ship orientations. Provisional transverse reference 28.5 m from crane centre to near vessel side. These are *study assumptions*, not externally verified berth/rigging facts.

## Saved files
- `all_vessel_pdf_source_register.csv`: **111** archived ship-spec PDF records from `epr2_exports/PDF_DIMENSION_INDEX.csv`, linked to the **190** existing cargo-screening rows where ship-name match is possible. Every row links directly to the archived PDF, preserves extracted dimensions and carries a confidence grade. Unchecked diagrams remain marked unchecked.
- `drawing_verified_geometry.csv`: original-page-specific visual evidence from manufacturer/operator/Baltic Shipping diagrams; clear separation between main-deck hatch footprints, hold dimensions, tween-deck levels, and exact stern offsets.
- `issues_to_resolve.csv`: conflicting or ambiguous sources requiring resolution before final crane-access calculations.

## Visual verification performed
1. **Briese Costamar/Lunamar**, official [two-page family sheet](https://briese.de/themes/briese/pdf/download_3_306.pdf?t=1748860554), PDF page 2. Side view: hold length **61.80 m**, breadth **11.20 m**. Main deck: **62.20 m** along hatch footprint. Do **not** treat 62.20 m as an independently confirmed *clear* hatch opening. [Independent Costamar account](https://www.scheepvaartwest.be/CMS/index.php/general-cargo/12644-costamar-imo-9552020) states 61.80 m for hold and hatch. Neither document gives a dimensioned offset from the **extreme stern** to aft hatch edge. Source LOA varies: Briese 99.48 m; independent 99.49 m; another [broker sheet](https://f.hubspotusercontent-eu1.net/hubfs/25209499/Documents/Vessel%20details%20with%20drawing/COSTAMAR%20vessel%20details.pdf) says 99.99 m.
2. **Briese ECO 9.1K family**, [family drawing](https://briese.de/themes/briese/pdf/download_3_444.pdf?t=1707741199), PDF page 2: **112.58 m** main-deck length, **97.33 m** tween-deck span, **84.78 m** lower hold length. Different levels are not interchangeable. Drawing labels ECO TITAN, so transfer to sister ships is **provisional**, subject to vessel-specific plans.
3. **Vertom Penhar**, [owner PDF](https://www.vertom.nl/wp-content/uploads/2025/03/00-leaflet-Penhar.pdf), PDF page 2: large **aft** hold ~59.60 m and smaller **forward** hold 18.70 m, visual direction confirmed; no stern-origin dimensions. [Operator website](https://www.vertom.nl/penhar/) instead says 59.90 m for hold 2, a contradiction.
4. **Niklas**, [independent Baltic Shipping sheet](https://balticshipping.dk/wp-content/uploads/2023/05/Niklas-11.pdf), PDF page 2: **56.55 m** hold/hatch length, width **10.15 m**, frame markers ~32.4–103.7, bow shown to the right; frame reference ≠ automatically extreme stern coordinate. Repository's Casper spec index reports width **10.02 m**.
5. **Vertom Meridiaan**, [owner sheet](https://vertom.com/wp-content/uploads/2024/11/00-leaflet-Vertom-Meridiaan.pdf): two holds 25.50 and 61.60 m; the [independent catalogue](https://www.scheepvaartwest.be/CMS/index.php/general-cargo/11522-vertom-meridiaan-imo-9385881) says 25.20 m for hold 1. Neither provides an exact stern offset.
6. **Vesper (Casper)**, archived [operator PDF](https://github.com/swatheeshkaran-max/edf-dechargement-colis/blob/main/casper_pdf/VESPER.pdf) indexed as hold/hatch 61.80 m, while [historical vessel account](https://www.flickr.com/photos/tags/imo9369514/) says 61.57 m. The vessel is IMO **9369514**, not the unrelated bulk carrier Vesper IMO 1061180.

**No exact numeric extreme-stern-to-hatch position was independently verified.** All numeric stern-offset cells are intentionally blank. A visually approximate diagram position must never be silently used as a precise berth coordinate.

## Procedure for the next calculation
1. Use vessel **IMO** to resolve name and sister-ship ambiguity; confirm LOA/beam/draught and hold and hatch separately.
2. Obtain dimensioned GA/capacity plan with scale and datum; measure (d_{stern \to aft\ hatch}) and (d_{stern \to aft\ hold}), using the vessel's **extreme stern**, not AP, unless AP-to-stern offset is also measured.
3. Map each cargo centre in real hatch/hold to absolute quay X/Y for the two orientations and permitted 5 m ship docking shifts.
4. Check clearance through **hatch** for every cargo route; opening widths must not be substituted from hold widths, nor can tween deck structural suitability be assumed.
5. Compute (R_i=\sqrt{(x_i-90)^2+(28.5+y_i)^2}) separately for each cargo lifting point; compare against the exact **SLDB/B** applicable chart for the selected 600 t/25 m derrick ballast arrangement and both booms; then screen loads including agreed rigging allowances.
6. Flag conflicts and missing primary documents as **PENDING GA**, never as PASS.

## Quality convention
- **B**: primary operator/family drawing visually reviewed, with external corroboration where described, but no precise aft offset.
- **C**: family-only drawing or a source discrepancy; vessel-specific approval needed.
- **D**: text extracted from PDF archived in the repo; drawing not yet inspected.

Do not infer that the presence of two links is two independent confirmations when both originate from the same operator.
