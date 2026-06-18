# Dataset — provenance & how to obtain it

The evaluation data (`test-00000-of-00001.parquet`, ~233 MB) is **not
committed to this repo**. It exceeds GitHub's 100 MB file limit, so it is
git-ignored (see the `*.parquet` rule in the root `.gitignore`).

## Where it came from

The parquet file is the **LiveCodeBench code-generation samples** dataset,
pulled from Hugging Face:

> `livecodebench-code-generation-samples`

It contains LiveCodeBench problems (wrapped by LiveBench's `coding_generation`
tasks): natural-language statements plus public and private test cases. Some
dumps store the private test cases as plain JSON, others as
base64(zlib(pickle(json))) — `lcb_loader.py` normalizes both.

## How to get it

Download the dataset from Hugging Face and place the parquet file here:

```
finalProblemsets/test-00000-of-00001.parquet
```

For example, with the Hugging Face CLI:

```bash
huggingface-cli download livecodebench-code-generation-samples \
  --repo-type dataset --local-dir finalProblemsets/
```

(Adjust the exact repo path/owner to match the source you were given.)

## How it's loaded

`lcb_loader.py` reads the problems and normalizes each into a single dict
shape (`question_id`, `title`, `prompt`, `difficulty`, `tests`, …). See the
module docstring in [lcb_loader.py](lcb_loader.py) for the full schema.
