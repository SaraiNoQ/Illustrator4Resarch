# Style-first workflow v0.7

## Problem

Version 0.6 classified nearly every visual choice as defaultable and instructed
the agent to ask only scientifically consequential questions. In the reported
main-results run, this correctly caused the agent to ask what `error` meant
while silently choosing chart type, palette, typography, and layout. The
behavior matched the old specification but not the intended product.

## Decision

Version 0.7 makes visual intent the first user-facing contract:

1. inspect a designated visual reference when present;
2. audit venue, chart/grammar, palette, typography, and layout;
3. present a Style Brief;
4. ask every unresolved style question with a recommendation;
5. append up to three scientific questions in the same response;
6. block formal rendering until both contracts are confirmed or delegated.

The model may parse data internally before the Style Brief so it can recommend
an honest chart. “Style first” governs interaction order, not scientific
carelessness.

## Delegation semantics

- “还没有决定” and “不确定” leave style pending.
- “你决定”, “按你的最佳推荐”, and “全部按推荐” explicitly delegate style.
- A designated reference resolves only properties visible in that image.
- Answering only a scientific question does not close the style gate.

## Figure Spec 1.1

New specs record style confirmation, style source, reference images, typography,
graphic grammar, layout, and chart selection status. Pending style or a merely
recommended chart makes the spec invalid. Legacy schema 1.0 remains readable
with a compatibility warning.

## Release gate

- exact reported prompt asks style questions before `error`;
- explicit delegation avoids redundant style questions;
- designated references are inspected and do not trigger repeated questions;
- science-only replies preserve the style block;
- confirmed requests complete render, deterministic QA, grayscale review, and
  visual inspection;
- repository copies, package, server checkout, and local installation match.
