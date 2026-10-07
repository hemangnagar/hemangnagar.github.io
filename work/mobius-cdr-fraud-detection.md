---
layout: problem
title: Detect SIM-box fraud at carrier scale
question: How do you detect SIM-box call bypass fraud from CDRs at carrier scale?
slug: mobius-cdr-fraud-detection
description: "Score each 30-minute CDR window against 24 hours of per-subscriber history in Spark, with the operator's rules inline. Latency: over 1 h to under 30 min."
permalink: /work/mobius-cdr-fraud-detection/
section: work
project: mobius
keywords: [SIM-box call bypass detection, A2P SMS bypass detection, OTP SMS bypass fraud, scoring 30-minute CDR windows against 24 hours of history, sizing a Spark cluster for 3 billion CDRs a day, telecom fraud detection pipeline]
image: /assets/og-hero.png
evidence:
  - Architecture (assets/mobius-architecture.svg), drawn from the description; no source code is published
  - Volumes, latency change, cluster sizes and the retention outcome supplied by Hemang
related: []
datePublished: 2026-10-07
dateModified: 2026-10-07
---
You score every 30-minute window of call detail records against the previous 24 hours of history for each subscriber number, in Spark, with the operator's own detection rules running inline. That replaced an hourly two-server batch and brought detection latency from over an hour to under 30 minutes. The largest deployment runs on 28 nodes at more than 3 billion voice records a day, and the same pipeline later took more than 50 billion SMS a day. It has been in production since 2015.

## Why it is hard

SIM-box fraud routes international calls through a bank of local SIM cards, so the terminating operator bills a local call instead of an international one. The signal is behavioral, not per-call. One record looks like an ordinary subscriber. A SIM box shows up as a number that makes many outbound calls, receives almost none, never moves between cells, and rotates through SIMs as they get blocked. You only see that by holding hours of history for every subscriber and comparing each new window against it.

Four things break at operator scale:

- **Volume.** A mid-sized operator produces billions of records a day. Holding a day of history for every subscriber, and joining each new batch against it, is a large distributed join every half hour, not a database query.
- **Latency.** Fraudsters watch for blocks and rotate SIMs. Detections that arrive an hour after the calls are useless; the SIM is gone. The old hourly batch on two servers took over an hour from the end of a window to a detection, and the operators' own analysts were finding misses after the fact.
- **Rules that change weekly.** Each operator's fraud team knows its own patterns and adjusts thresholds often. If a rule change needs a code release, the pipeline is always a week behind.
- **Commercial pressure.** Several accounts worth about $300K a year each were about to churn to a competitor over exactly those misses and delays. The rebuild had to work on the first deployment.

## How I solved it

I re-architected the detector as a Hadoop/Spark pipeline. Call detail records land in HDFS as one file set per 30-minute window. A Spark job joins the window with the previous 24 hours of per-MSISDN features, which live in HBase and are queried through Phoenix, computes the behavioral features for the window, and then runs the detection rules inline in the same job. The job writes the updated history back and emits detections with the evidence that fired them.

<figure class="ink"><img src="/assets/mobius-architecture.svg" width="1200" height="600" alt="Architecture of the Mobius fraud pipeline: CDR feeds land in HDFS in 30-minute windows; a Spark scoring job compares each window with 24 hours of per-subscriber history in HBase and Phoenix and runs customer-authored rules from MongoDB inline; detections go to a Node.js UI for the operator's analysts. Deployments range from 2 nodes at 30 million records a day to 28 nodes at over 3 billion." loading="lazy" decoding="async"><figcaption>The pipeline as deployed. Drawn from the description; the source is proprietary.</figcaption></figure>

The rules moved out of the code. A redesigned Node.js UI lets the operator's analysts author and edit detection rules themselves; the rules are stored in MongoDB and read by the Spark job on each window. A threshold change is live on the next window, not the next release.

Three design decisions carried the weight:

1. **Window and history sizes were chosen for the fraud, not the hardware.** Thirty minutes is short enough to catch a SIM before rotation and long enough to amortize the join. Twenty-four hours of history is where the behavioral signal stabilizes; longer windows cost storage without adding recall.
2. **Deployments are sized per customer.** The same pipeline runs on 2 nodes for an operator at 30 million records a day and on 28 nodes for one at more than 3 billion. Nothing in the code changes between them; only the cluster and the window file layout do.
3. **The namenode is highly available.** Early deployments lost the HDFS namenode more than once, which stopped every window behind it. Moving to an HA namenode pair removed the single point of failure, and it has not been the cause of a missed window since.

The trade-off I accepted: an inline rules engine in Spark is less flexible than a separate streaming rules service, and a bad rule can slow a window. In exchange, there is one job to operate, one place where the evidence is computed, and no second system to keep in sync with the history store.

## Evidence

| What | Before | After |
|---|---|---|
| Detection latency | over 1 hour, hourly batch on 2 servers | under 30 minutes, every 30-minute window |
| Largest deployment | — | 28 nodes, 3B+ voice CDRs/day |
| SMS | — | 50B+ SMS/day, 1B+ per 30-minute window |
| Smallest deployment | — | 2 nodes, 30M CDRs/day |
| Who writes the rules | engineers, per release | the operator's analysts, in the UI |
| In production | — | since 2015, still running |

The same pipeline was reused, with new features and rules, for A2P and OTP SMS bypass fraud, where grey routes deliver application-to-person messages through consumer SIMs. The join and the history store were unchanged; the features and the rules were the only additions.

The accounts that were about to leave stayed. The customers are multiple mobile operators in West Africa; I do not name them, and no source code from this system is published.

## When this applies, and when it doesn't

This design fits any detection problem where the signal is a subscriber's behavior over hours and the data arrives in bulk: SIM-box and SMS bypass fraud, A2P grey routes, wholesale fraud, and some account-takeover patterns. It needs an operator willing to run a Hadoop or Spark cluster, or a managed equivalent such as EMR, and a fraud team that will own its rules.

It does not fit call-by-call blocking, where a decision is needed in milliseconds while the call is being set up; that is a streaming or in-switch problem, and a 30-minute window is the wrong unit. It is also more than a small operator needs below a few million records a day, where a single database and a nightly job are enough. And if the fraud team cannot or will not maintain rules, an inline rules engine turns into a code backlog again; a managed model with a review queue is the better shape there.

## Stack

Hadoop, Spark, HBase with Phoenix, MongoDB, Node.js, and AWS (S3, Lambda, EMR) for the cloud-hosted deployments.
