# Virus — Phase 4/5 Blueprint: Parent Model, Child Specialists, and Device Adaptation

## What this phase is

This document sketches a concrete plan for taking the current Virus project from a single continuously learning model into a more powerful architecture where:

- one parent model acts as the general foundation,
- multiple child models specialize in specific domains,
- the system remains adaptable to desktop, server, and mobile devices,
- the design supports future portability without rewriting the entire project.

The goal is not just to make the system bigger. The goal is to make it more stable, more modular, and more practical for real deployment.

---

## Level 0: Core idea

At the most basic level, the project should be thought of as a layered intelligence system:

1. Parent model
   - broad general knowledge
   - strong basic reasoning and language behavior
   - acts as the root intelligence

2. Child models
   - inherit from the parent
   - specialize in narrow tasks
   - are lighter and more efficient for dedicated use cases

3. Memory and routing layer
   - decides when to use the parent vs. a child
   - stores important patterns and past experiences
   - reduces forgetting and context drift

4. Device adaptation layer
   - allows the same architecture to run on CPU, GPU, or mobile
   - chooses the right model size and precision based on hardware

This is the simplest way to make the project scalable without making it brittle.

---

## Why this matters

The current system is already a good prototype for:

- conversation
- text generation
- small continual learning
- lightweight memory-based behavior

But for long-term growth, a single model becomes limiting because it must carry too many roles at once.

A parent/child system solves that by separating:

- general intelligence
- specialist knowledge
- efficient on-device execution

---

## Phase 4/5 design goal

### Main objective

Allow the parent model to create and supervise child models that specialize in specific areas of work, while keeping the core identity of the parent intact.

### Intended behavior

The child should not be a fresh random model.
It should inherit the parent’s core behavior, then be trained further in a specific domain.

That means the child should be:

- stable
- less likely to forget the parent’s general behavior
- better at focused tasks
- easier to run on smaller hardware

---

## Recommended architecture

## 1. Parent model

The parent should be the broad foundation model.

It should be responsible for:

- general conversation
- broad knowledge retention
- high-level decision making
- producing a stable behavioral base

It should be trained on:

- conversation data
- general knowledge
- coding examples
- correction data
- long-term memory traces

The parent should be the model that creates or guides specialization.

---

## 2. Child model

Each child should be a smaller specialist model that inherits from the parent.

Possible child domains:

- coding assistant
- writing assistant
- math specialist
- emotional support assistant
- wiki/knowledge specialist
- Minecraft policy specialist
- mobile personal assistant

Each child should be trained with:

- parent-seeded initialization
- domain-specific data
- replay of core parent behavior
- memory retention mechanisms

The child should not be trained from scratch unless the system explicitly wants a completely independent specialist.

---

## 3. Shared backbone + adapters

The most practical design is:

- shared backbone inherited from the parent
- small domain-specific adapter layers added on top
- specialist output head for the child’s domain

This lets the child be:

- smaller than the parent
- faster to run
- cheaper to deploy
- less prone to catastrophic forgetting

This is much better than rebuilding a full new model for every specialty.

---

## 4. Memory and replay system

A child should not rely only on new training data.
It needs a memory scaffold.

### Core memory layers

1. Parent memory
   - general rules
   - personality and style
   - core behavior patterns

2. Child memory
   - specialist facts
   - topic-specific habits
   - task-specific examples

3. Replay memory
   - periodic reminders of parent behavior
   - prevents the child from drifting too far away

4. Retrieval memory
   - stores past useful experiences
   - lets the child recall relevant information quickly

This is the “tattooed knowledge” idea in practical form:

- the child starts with the parent’s core identity
- then grows a specialist layer on top
- the parent’s core remains visible and recoverable

---

## Detailed training process

## Step 1: Train or preserve the parent

The parent should first be trained well enough to be stable.

This includes:

- general language ability
- coherent response behavior
- memory retention behavior
- robust basic instructions

The parent is the reference model.

---

## Step 2: Create a child initialization from the parent

Instead of random initialization:

- load parent weights into the child model
- preserve the shared layers
- optionally freeze the lower layers to keep core behavior intact

This makes the child inherit the parent’s behavior before specialization begins.

---

## Step 3: Add specialist training data

The child should be trained on focus-specific examples.

Examples:

- coding child: Python, C++, debugging logs, API docs
- writing child: essays, summaries, tone control, structured writing
- knowledge child: curated factual data, Q/A pairs, references
- Minecraft child: action policies, state transitions, decision data

The training set should be small, high-quality, and domain-precise.

---

## Step 4: Add replay from the parent

This is critical.

During child training, the system should periodically include:

- general conversation examples
- parent-style responses
- stable instruction-following samples
- broad behavior examples

This makes the child less likely to forget the parent’s base identity.

---

## Step 5: Add distillation

Distillation means the child learns not just from labels, but from the parent’s outputs.

The parent can generate examples and the child learns to mimic them.

This creates a strong soft transfer of knowledge:

- parent teaches the child how to behave
- child learns the style, structure, and depth of reasoning
- specialist training then refines the child further

This is one of the best ways to make the “tattooed knowledge” idea real.

---

## Step 6: Deploy the child as a specialist runtime

Once a child is trained:

- it can be used independently for its chosen task
- it can be routed to when the task matches its domain
- it can be run on lighter hardware than the full parent

This makes the overall system much more efficient.

---

## How to make forgetting much less likely

Forgetting is the main problem in specialist training.

To reduce it, the child should use all of these:

1. Parent initialization
2. Frozen shared layers
3. Adapter tuning rather than full retraining
4. Replay memory
5. Distillation from the parent
6. Periodic evaluation against general tasks
7. Memory retrieval for old concepts

If you do these well, the child becomes a stable specialist instead of a fragile overfit model.

---

## Suggested project structure for this phase

```text
Virus/
├── parent/
│   └── general_model
├── children/
│   ├── coding_child
│   ├── writing_child
│   ├── knowledge_child
│   └── mobile_child
├── memory/
│   ├── replay_buffer
│   ├── retrieval_store
│   └── long_term_notes
├── router/
│   └── task_to_child_selector
├── deploy/
│   ├── desktop
│   ├── server
│   └── mobile
└── config/
    └── device_profiles
```

---

## How to verticalize the project

“Verticalize” here means making the system more focused, more specialized, and more deployable.

### 1. Make the architecture modular

Separate the system into:

- model core
- training pipeline
- memory system
- routing logic
- deployment layer

This makes it easier to swap parts later.

### 2. Make the model size configurable

You want different versions of the system:

- tiny mobile model
- medium desktop model
- larger server model

The same codebase should support all of them.

### 3. Make the training pipeline hardware-aware

The pipeline should know:

- whether it is running on CPU only
- whether GPU is available
- whether the target is mobile or server

This prevents the project from being locked into one hardware setup.

### 4. Make quantization a first-class step

Quantization is one of the biggest enablers for portability.

Ideal targets:

- 8-bit inference for mobile or edge devices
- 4-bit inference for very small devices
- mixed precision for GPU systems

### 5. Make export formats device-ready

The trained model should be exportable to formats such as:

- TorchScript
- ONNX
- ONNX Runtime
- PyTorch Mobile
- ExecuTorch

This allows the project to move between environments without redesign.

### 6. Make the memory system portable

Memory should not depend on one machine setup.

Possible future options:

- local JSON or SQLite memory
- embedded vector search
- lightweight on-device embeddings
- remote memory server

### 7. Build a runtime profile system

A good future addition is a profile file such as:

```json
{
  "target": "mobile",
  "device": "cpu",
  "precision": "int8",
  "max_model_size": "80mb"
}
```

Then the system can adapt automatically based on the profile.

---

## Device adaptability plan

## CPU-only

Use this when:

- you want maximum compatibility
- you are on a weak machine
- you want safe inference without GPU dependency

Best for:

- simple local testing
- small models
- low-power devices
- mobile fallback mode

---

## CPU + GPU

Use this when:

- you want faster training and inference
- your machine has a decent GPU but not a massive one
- you want flexibility

Best for:

- mixed workloads
- development and experimentation
- medium-size models
- local training with reasonable speed

---

## GPU-only

Use this when:

- you want the fastest throughput
- you are training larger models
- you want full acceleration for heavier inference

Best for:

- server-side training
- large-scale experimentation
- high-performance deployment

---

## Important note about device selection

Yes — in practice you can control whether the system uses CPU only, CPU + GPU, or GPU only.

In PyTorch, the standard approach is:

```python
import torch

device = torch.device("cpu")
# or
device = torch.device("cuda")
# or
device = torch.device("cuda:0")
```

For GPU selection, you can also use:

```bash
CUDA_VISIBLE_DEVICES=0 python your_script.py
```

And for forcing CPU-only execution:

```bash
CUDA_VISIBLE_DEVICES='' python your_script.py
```

### In the current repo

The current training script already uses a device selection pattern based on whether CUDA is available. In [auto_train.py](auto_train.py), the model is placed on:

- CUDA if available
- otherwise CPU

So the project is already partially hardware-aware.

### What is missing

What is not fully implemented yet is a clean user-facing switch such as:

- `--device cpu`
- `--device cuda`
- `--device auto`

That would make the workflow much easier to control.

---

## Recommended next implementation steps

## Phase 4: Parent/child foundation

1. Add a configurable device selector
2. Add a parent model checkpoint workflow
3. Add a child initialization pipeline
4. Add a replay buffer for parent behavior
5. Add a routing layer for selecting the right child

## Phase 5: Deployment and portability

1. Export to TorchScript or ONNX
2. Add quantization support
3. Add a tiny mobile profile
4. Add a desktop/server profile
5. Add a runtime profile loader
6. Add fallback behavior for low-power devices

---

## Practical mobile strategy

For a phone such as a Tecno Pova 6 Neo, the best path is not to run the full parent model locally at first.

### Best deployment plan

- parent runs on desktop or server
- child runs on phone for specialized tasks
- the child is smaller and quantized
- memory and retrieval stay lightweight

### Mobile-friendly target

A mobile child should be:

- compact
- quantized
- low-latency
- task-specific
- memory-efficient

That is the best way to make the system usable on real hardware without requiring a powerful device.

---

## Final recommendation

The most robust future version of the project should be built as a hierarchy:

- parent model for general intelligence
- child specialists for narrow tasks
- memory and replay for stability
- hardware profiles for CPU, GPU, and mobile
- export and quantization for portability

That is the most realistic way to make the project both powerful and adaptable.

If you keep the architecture modular from the start, then later you can move any part of the system to another device without needing to rebuild everything from zero.
