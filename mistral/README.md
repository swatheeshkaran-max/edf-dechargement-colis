# Mistral — verified Bois de Boulogne riverside image set

This project stores visual references for the VNF floating-site project at **10 allée du bord de l'eau, Bois de Boulogne, Paris**.

## Verification

The image set was checked against the official VNF project record:

- Project page: https://domaine-public-fluvial.vnf.fr/avis/plan-deau-etablissement-flottant-paris-bois-de-boulogne/
- Official map coordinate on the page: **48.8635008, 2.2285939**
- Official notice: `source_documents/official_vnf_notice_paris_bois_de_boulogne.pdf`
- Site description: Seine, right bank; Galion emplacement; Bois de Boulogne bank and access path.

The five files in `images/` are either directly linked by the official VNF page or extracted from the official VNF notice. `IMAGE_MANIFEST.csv` records the source, verification reason, dimensions, and SHA-256 hash for each file.

## Files

- `01_official_vnf_galion_front_2026-05.jpg`: close view of the Galion, gangway and river edge.
- `02_official_vnf_plan_emplacement_2026-05.png`: official plan image of the Galion emplacement.
- `03_official_notice_location_map.jpg`: official notice location map.
- `04_official_notice_aerial_site_context.jpg`: official notice aerial context image.
- `05_official_notice_aerial_galion_footprint.jpg`: official notice aerial image with the Galion footprint highlighted.

The modelling envelope agreed for Blender is the 55 m site length plus 30 m upstream and 30 m downstream, approximately 115 m of riverside context. The existing Galion is reference geometry only and will be replaced in the final concept scene.

## Excluded image

The generic `Bitmap.jpg` shown on the VNF page was not included because it is a practical-guide illustration and does not depict this project location.

## Blender use

Use the plan image for scaled top-view tracing. Use the aerial images for bank, vegetation and mooring context. Use the Galion photograph only as a visual reference while the final two replacement boats remain separate Blender assets.
