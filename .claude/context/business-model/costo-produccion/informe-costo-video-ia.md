# Costo de producción — 1 video de IA de 9–10 min por día (Claude ↔ Higgsfield → YouTube)

_Estudio de costos para el pipeline de video largo. Última actualización: 2026-07-08._

> **TL;DR:** hacer **1 video de 10 min 100% generado por IA (Higgsfield) por día** cuesta **~$1.300–2.400/mes** (~$43–80/video), más ~3–6 meses de burn a $0 de ingreso hasta cruzar el umbral del YPP. **Es el camino más caro y va en contra del formato que el informe de YouTube recomienda** (faceless con voz en off + visuales de apoyo). El formato narrado con IA de acento cuesta **~$400–700/mes** por el mismo resultado monetizable. Este estudio ancla en [../youtube-monetizacion/informe-youtube.md](../youtube-monetizacion/informe-youtube.md) y las fichas de [IA adultos](../../videos/canales/ia-adultos.md) / [IA simple](../../videos/canales/ia-simple.md).

---

## Contexto: qué pide la estrategia

Del [informe de YouTube long-form](../youtube-monetizacion/informe-youtube.md): canal en **inglés**, **explicar IA para adultos**, videos de **10–15 min**, **un canal enfocado**, con **doblaje bilingüe (multi-audio en el mismo canal)** como diferencial. El formato que monetiza y que usan los benchmarks (LEMMiNO, Kurzgesagt, Anton Petrov) es **faceless: voz en off + visuales de apoyo** — no footage cinematográfico continuo.

Este estudio evalúa el escenario **"100% video IA continuo"** (los 10 min son footage de Higgsfield), que fue el pedido explícito, y lo compara con el formato del informe.

---

## 1) La conexión Claude ↔ Higgsfield

- Higgsfield tiene **API pública + SDK de Python oficial** ([higgsfield-client](https://github.com/higgsfield-ai/higgsfield-client)) → Claude puede orquestar todo el pipeline: guion EN → prompts de cada clip → generación → ensamblado → subida a YouTube.
- **La API solo está disponible en el plan Studio/Ultra** (el más caro). Los planes baratos ($15–39/mes) no dan API. La "conexión" no es un producto aparte: es la suscripción base + tiempo de desarrollo.
- **Costo único**: armar el pipeline (unos días con Claude Code, básicamente tiempo propio). No es una licencia recurrente.
- **Límite técnico clave**: cada clip dura **máximo 16 s**. Un video de 10 min (600 s) = **~40–75 clips**, y en la práctica se generan **3–5× por descarte**. Eso es lo que dispara el costo.

---

## 2) Costo mensual — 10 min/día, 100% video IA, 30 videos/mes

| Ítem | Costo/mes (USD) | Nota |
|---|---|---|
| **Higgsfield — generación (modelo económico, tipo Kling)** | **$1.000 – $1.800** | El grueso. ~50 clips útiles/video × iteración × 30. Plan Ultra + top-ups |
| Higgsfield — generación premium (Veo 3 / Sora 2) | $10.000 – $20.000+ | **Inviable a diario — descartado** |
| Claude API (guion EN + ~50 prompts/video + orquestación + versión ES) | $50 – $250 | Barato al lado de Higgsfield (Sonnet para prompts, Opus para guion) |
| Voz en off TTS **EN + ES** (multi-audio, ~600 min/mes) | $100 – $200 | El formato faceless **exige** narración. ElevenLabs Pro/Scale |
| Música/SFX + herramienta de ensamblado | $15 – $40 | Epidemic Sound + ffmpeg/CapCut |
| **TOTAL viable** | **≈ $1.300 – $2.400 / mes** | **~$43 – $80 por video** |

**Costos que no aparecen en la tabla pero son reales:**
- **Ensamblado diario** de ~50 clips + narración + subtítulos → trabajo humano o desarrollo de automatización (costo en tiempo, no en licencia).
- **Build inicial** de la integración Claude ↔ API ↔ YouTube (costo único).

---

## 3) Cruce con la monetización (RPM del informe)

Con RPM **IA/educación en inglés Tier-1 ≈ $8–12** ([informe YouTube](../youtube-monetizacion/informe-youtube.md)):

- **Break-even**: cubrir ~$1.800/mes exige **~150.000–225.000 views/mes** totales (≈ 5.000–7.500 por video). Un video que pegue 100k views ≈ $800–1.200 cubre medio mes.
- **Muro previo**: el YPP no paga hasta **1.000 subs + 4.000 hs de watch time**. Se arranca con **$0 de ingreso durante ~3–6 meses** mientras se paga el costo mensual. **Runway realista antes de monetizar: ~$4.000–14.000 en total.**
- **El bilingüe juega a favor del video IA**: los clips no tienen idioma → el mismo footage sirve EN y ES (solo se re-dobla la narración). La imagen se produce una vez y se exprime en los dos idiomas.

---

## 4) Tensión con el informe + comparación de formatos

Si en vez de "100% continuo" se usa Higgsfield para **B-roll de acento dentro de un explainer narrado** (lo que hacen los benchmarks del informe), el ítem Higgsfield cae de ~$1.500 a **~$150–400/mes**.

| Formato | Higgsfield/mes | Total/mes | Alineado con el informe | Riesgo política "Inauthentic" |
|---|---|---|---|---|
| **100% video IA continuo** (pedido) | $1.000–1.800 | **$1.300–2.400** | No (el informe pide narrado) | Mayor (plantilla replicable) |
| **Narrado + IA de acento** (informe) | $150–400 | **$400–700** | Sí | Menor |

---

## Veredicto

- **100% IA continuo**: técnicamente posible vía API Studio, **~$1.300–2.400/mes** + 3–6 meses de burn. Caro y en contra del propio informe.
- **Narrado + IA de acento**: **~$400–700/mes**, formato que monetiza, footage reusable EN/ES. **Recomendado.**

---

## Supuestos y método

- 30 videos/mes, 10 min c/u. ~50 clips útiles/video (clips de 10–12 s por coherencia; máx. técnico 16 s).
- Iteración 3–5× ya incorporada en el costo efectivo por clip útil (Kling ~$0,61–1,03 en plan; premium $3,36–9,33).
- Higgsfield: plan Ultra base ($99–149/mes) + top-ups (~$5/100 créditos, expiran a 90 días).
- Claude API y TTS son estimaciones de orden; el driver dominante del costo es siempre Higgsfield.
- Precios verificados a 2026-07; varían ±50% entre fuentes y updates.

## Fuentes

- [Higgsfield Pricing](https://higgsfield.ai/pricing) · [Higgsfield Cloud API](https://cloud.higgsfield.ai/) · [SDK Python (higgsfield-client)](https://github.com/higgsfield-ai/higgsfield-client)
- [Análisis de precios Higgsfield 2026 — Scopeful](https://www.scopeful.org/tools/higgsfield)
- Informes internos: [YouTube long-form/RPM](../youtube-monetizacion/informe-youtube.md), [nichos (histórico)](../estudio-nichos-youtube.md), fichas de canal [IA adultos](../../videos/canales/ia-adultos.md) / [IA simple](../../videos/canales/ia-simple.md)
