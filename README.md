# Beckmann World Models

Academic project page at https://abecid.com/beckmann-world-models/.

The page contains a title and authors, a method figure, selected qualitative results, and quantitative results. Curated predictions retain recorded timing and checkpoint labels. Native evaluation resets recorded context every eight frames and scores VAE-reconstructed references.

Build using python3 scripts/build.py --public. The existing GitHub Actions workflow publishes dist-public.

This site repository contains no research code, model checkpoints, training data, or private manuscript. Internal review records are excluded from the public build.

## October 7, 2026 update

The full-data refinement table reports completed official RT-1 validation for the epoch-70 starting model, the original-objective continuation, and the recovery-feature checkpoint. Both continuations use 1,000 added updates. The complete evaluation record also retains Bridge-V2 results at 500 added updates. The matched-subset baseline table remains separate and unchanged. `data/native-refinement-20261007.json` retains exact metrics, checkpoint/aggregate identities, protocol and selection limitations. The static build verifies all 15 displayed full-data metric cells against that record.

LPIPS, FID and FVD improve with recovery feature supervision, with a small PSNR decrease. These are selected validation checkpoints; contact and motion errors remain. The selected qualitative clips use the same refined checkpoints under the official eight-frame prediction protocol. They retain consecutive saved frames at the original dataset frame rates, without enhancement, averaging or interpolation. Public media provenance identifies the exact episodes, target ranges, checkpoints and source-image hashes.
