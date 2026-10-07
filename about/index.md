---
layout: page
title: About Hemang Nagar
description: "Data and AI engineer in Northern Virginia: 20+ years of production data systems, 10+ years of Spark, a fraud pipeline at 3B call records a day since 2015."
permalink: /about/
person: true
dateModified: 2026-10-07
---
I am a data and AI engineer in Vienna, Virginia, in the Washington, DC area. I have designed and built production data systems for more than twenty years, and I have worked in Apache Spark for more than ten of them. The work runs across three domains: data for financial institutions, federal and law-enforcement data, and telecom fraud.

## What I do now

I am an engineer and technical lead at KYM Advisors, where I lead architecture and hands-on engineering on data interoperability programs for the U.S. Intelligence Community. I joined in February 2022 and have been full-time there since May 2026. I hold an active U.S. government security clearance.

Alongside that work I take fixed-scope consulting engagements on governed data pipelines and on putting language models behind deterministic gates. The engagement types are on the [services page](/services/).

## What I have built at scale

From 2015 to 2026 I was head of product development and chief architect at Mobius Wireless Solution in Ashburn, Virginia. The main product was a SIM-box and SMS bypass fraud detection pipeline for mobile operators. I re-architected it from an hourly two-server batch into a Hadoop/Spark pipeline that scores every 30-minute window of call detail records against 24 hours of per-subscriber history. Its largest deployment runs on 28 nodes at more than 3 billion voice call records a day, and later more than 50 billion SMS a day. It has been in production since 2015. The [full case study](/work/mobius-cdr-fraud-detection/) has the architecture, the numbers and the trade-offs.

Earlier I was a principal consultant and lead developer on systems for the Department of Veterans Affairs, Marriott, Verisign, Red Hat Consulting, Fannie Mae, the Federal Communications Commission and RiskMetrics Group.

## How I work

The LLM proposes; the pipeline disposes. A model may propose a match, a parser repair, a summary or a decision, but a deterministic check decides whether it reaches the trusted layer, and every run replays identically. I work standards-first: data contracts that tests enforce (Open Data Contract Standard), lineage emitted on every run (OpenLineage), FHIR R4B where healthcare data is involved, and provenance from any user-facing figure back to the raw bytes it came from.

My open-source projects show the same habit in eight different domains. Each has a page that answers the question it was built for, under [Problems](/problems/), and a card with screenshots on the [home page](/#work).

## Education

I hold two master's degrees from Rensselaer Polytechnic Institute, in Computer and Systems Engineering and in Decision Sciences and Engineering, and a bachelor's degree in Instrumentation Engineering from the University of Mumbai.

## Contact

Email [hi@hemangnagar.dev](mailto:hi@hemangnagar.dev). I am on [GitHub](https://github.com/hemangnagar), [LinkedIn](https://www.linkedin.com/in/hemangnagar/) and [X](https://x.com/hnagar_dev). A [résumé (PDF)](/assets/hemang-nagar-resume.pdf) is available.
