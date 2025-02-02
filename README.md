# Dolly for M Science

This repository extends Databricks' [Dolly](https://huggingface.co/databricks/dolly-v2-12b) to train on Sundial Beacon data.  The Dolly [repository](https://github.com/databrickslabs/dolly) documentation is good---and included below---but lacks a few important tips and tricks.

### Cluster Setup

Train on a GPU cluster running Databricks runtime 13.0 or higher with GPU support, not 12.2 as suggested below.  Feel free to use `nkatuna_gpu_cluster`, or copy its cluster configurations to create your own *single node* GPU cluster.  The `p4d.24xlarge` instances (A100) are very challenging to provision so use the `g5.4xlarge` (A10) instead.  You only need one worker.  Don't increase your cluster size thinking that you'll save time.

We've found that Databricks clusters will occasionally crash without warning during training.  If this happens just restart your cluster and replay your notebook.

### Training Data

In order to limit training time we've used only a subset of Beacon data to train the model.  There are three approaches that we've seen to using LLMs for data science:
 * Translate the data directly into text for the LLM to process
 * Feed text insights and contextualizing information (e.g., investment research) into the LLM 
 * Give the LLM the schema of database tables containing data and insights and ask only for SQL to pull data and insights directly from those database tables

 Here, we attempt only the first approach, and have rewritten the data loading modules in Dolly to pull in M Science data.


### Model Selection

The Dolly [code](https://github.com/databrickslabs/dolly) allows you to specify a foundational model.  We've found that more recent changes to the code better support `EleutherAI/pythia-6.9b` rather than `databricks/dolly-v2-12b`.

### Feedback

Please give us your feedback as you play with the model!


## Dolly

Databricks’ [Dolly](https://huggingface.co/databricks/dolly-v2-12b) is an instruction-following large language model trained on the Databricks machine learning platform
that is licensed for commercial use. Based on `pythia-12b`, Dolly is trained on ~15k instruction/response fine tuning records
[`databricks-dolly-15k`](https://huggingface.co/datasets/databricks/databricks-dolly-15k) generated
by Databricks employees in capability domains from the InstructGPT paper, including brainstorming, classification, closed QA, generation,
information extraction, open QA and summarization. `dolly-v2-12b` is not a state-of-the-art model, but does exhibit surprisingly
high quality instruction following behavior not characteristic of the foundation model on which it is based.

Databricks is committed to ensuring that every organization and individual benefits from the transformative power of artificial intelligence. The Dolly model family represents our first steps along this journey, and we’re excited to share this technology with the world.

The model is available on Hugging Face as [databricks/dolly-v2-12b](https://huggingface.co/databricks/dolly-v2-12b).

## Model Overview

`dolly-v2-12b` is a 12 billion parameter causal language model created by [Databricks](https://databricks.com/) that is derived from
[EleutherAI’s](https://www.eleuther.ai/) [Pythia-12b](https://huggingface.co/EleutherAI/pythia-12b) and fine-tuned
on a [~15K record instruction corpus](https://github.com/databrickslabs/dolly/tree/master/data) generated by Databricks employees and released under a permissive license (CC-BY-SA)


## Known Limitations

### Performance Limitations
**`dolly-v2-12b` is not a state-of-the-art generative language model** and, though quantitative benchmarking is ongoing, is not designed to perform
competitively with more modern model architectures or models subject to larger pretraining corpuses.

The Dolly model family is under active development, and so any list of shortcomings is unlikely to be exhaustive, but we include known limitations and misfires here as a means to document and share our preliminary findings with the community.
In particular, `dolly-v2-12b` struggles with: syntactically complex prompts, programming problems, mathematical operations, factual errors,
dates and times, open-ended question answering, hallucination, enumerating lists of specific length, stylistic mimicry, having a sense of humor, etc.
Moreover, we find that `dolly-v2-12b` does not have some capabilities, such as well-formatted letter writing, present in the original model.

### Dataset Limitations
Like all language models, `dolly-v2-12b` reflects the content and limitations of its training corpuses.

- **The Pile**: GPT-J’s pre-training corpus contains content mostly collected from the public internet, and like most web-scale datasets,
it contains content many users would find objectionable. As such, the model is likely to reflect these shortcomings, potentially overtly
in the case it is explicitly asked to produce objectionable content, and sometimes subtly, as in the case of biased or harmful implicit
associations.

- **`databricks-dolly-15k`**: The training data on which `dolly-v2-12b` is instruction tuned represents natural language instructions generated
by Databricks employees during a period spanning March and April 2023 and includes passages from Wikipedia as references passages
for instruction categories like closed QA and summarization. To our knowledge it does not contain obscenity, intellectual property or
personally identifying information about non-public figures, but it may contain typos and factual errors.
The dataset may also reflect biases found in Wikipedia. Finally, the dataset likely reflects
the interests and semantic choices of Databricks employees, a demographic which is not representative of the global population at large.

Databricks is committed to ongoing research and development efforts to develop helpful, honest and harmless AI technologies that
maximize the potential of all individuals and organizations.

## Getting Started with Response Generation

If you'd like to simply test the model without training, the model is available on Hugging Face as [databricks/dolly-v2-12b](https://huggingface.co/databricks/dolly-v2-12b).

To use the model with the `transformers` library on a machine with A100 GPUs:

```
from transformers import pipeline
import torch

instruct_pipeline = pipeline(model="databricks/dolly-v2-12b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")
```

You can then use the pipeline to answer instructions:

```
instruct_pipeline("Explain to me the difference between nuclear fission and fusion.")
```

### Generating on Other Instances

A100 instance types are not available in all cloud regions, or can be hard to provision. Inference is possible on other GPU instance types.

#### A10 GPUs

The 6.9B and 2.8B param models should work as-is.

To generate using the 12B param model on A10s (ex: `g5.4xlarge`, 1 x A10 24GB), it's necessary to load and run generating using 8-bit weights, which impacts the results slightly:

- Also install `bitsandbytes`
- Add `model_kwargs={'load_in_8bit': True}` to the `pipeline()` command shown above

#### V100 GPUs

When using V100s (ex: `p3.2xlarge`, 1 x V100 16GB, `NC6s_v3`), in all cases, set `torch_dtype=torch.float16` in `pipeline()` instead.

Otherwise, follow the steps above. The 12B param model may not function well in 8-bit on V100s.

## Getting Started with Training

- Add the `dolly` repo to Databricks (under Repos click Add Repo, enter `https://github.com/databrickslabs/dolly.git`, then click Create Repo).
- Start a `12.2 LTS ML (includes Apache Spark 3.3.2, GPU, Scala 2.12)` single-node cluster with node type having 8 A100 GPUs (e.g. `Standard_ND96asr_v4` or `p4d.24xlarge`). Note that these instance types may not be available in all regions, or may be difficult to provision. In Databricks, note that you must select the GPU runtime first, and unselect "Use Photon", for these instance types to appear (where supported).
- Open the `train_dolly` notebook in the Repo (which is the `train_dolly.py` file in the Github `dolly` repo), attach to your GPU cluster, and run all cells.  When training finishes, the notebook will save the model under `/dbfs/dolly_training`.

### Training on Other Instances

A100 instance types are not available in all cloud regions, or can be hard to provision. Training is possible on other GPU instance types, 
for smaller Dolly model sizes, and with small modifications to reduce memory usage. These modifications are not optimal, but are simple to make. 

Select your GPU family type from the `gpu_family` widget, enter the number of GPUs available in the `num_gpus` widget, and then run the rest of the code. 
A number of different options will be set for you to train the model for one of the following GPU types:
- A100 (default)
- A10 
- V100

Details of the different configurations are below.

#### A100 GPUs

A100 GPUs are preferred for training all model sizes, and are the only GPUs that can train the 12B param model in a reasonable amount of time.
As such, this is the default configuration, as set in the `a100_config.json` deepspeed config file.

#### A10 GPUs

Training the 12B param model is not recommended on A10s.

To train the 6.9B param model on A10 instances (ex: `g5.24xlarge`, 4 x A10 24GB; `Standard_NV72ads_A10_v5`, 2 x A10),
simply select `a10` from the `gpu_family` widget and enter the number of GPUs available in the `num_gpus` widget, then run the rest of the code. 
This will use the `a10_config.json` deepspeed config file, which makes the following changes:

- `per-device-train-batch-size` and `per-device-eval-batch-size` are set to 3 in the `train_dolly.py` invocation of `deepspeed`
- Within the `"zero_optimization"` section of the deepspeed config, we have added:
  ```
  "offload_optimizer": {
    "device": "cpu",
    "pin_memory": true
  },
  ```

#### V100 GPUs

To run on V100 instances with 32GB of GPU memory (ex: `p3dn.24xlarge` or `Standard_ND40rs_v2`), 
simply select `v100` from the `gpu_family` widget and enter the number of GPUs available in the `num_gpus` widget, and then run the rest of the code. 
This will use the `v100_config.json` deepspeed config file, which makes the following changes:

- It makes the changes described above for A10s
- It enables fp16 floating point format
- It sets the `per-device-train-batch-size` and `per-device-eval-batch-size` to 3
  
You may be able to slightly increase the batch size with 32GB instances, compared to what works above for 24GB A10s.

## Running Unit Tests Locally

```
pyenv local 3.8.13
python -m venv .venv
. .venv/bin/activate
pip install -r requirements_dev.txt
./run_pytest.sh
```
